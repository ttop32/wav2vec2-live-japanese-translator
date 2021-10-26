# https://wikidocs.net/87141

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from translate_handler import TranslateHandler
from setting_handler import SettingHandler
from wav2vec2_live import LiveWav2Vec2
from gui import MainWindow
import multiprocessing
import threading


class GuiHandler:
    def __init__(self,modelName,useCuda):
        self.window=MainWindow()
        self.asr= LiveWav2Vec2()
        self.modelName=modelName
        self.window.setText("loading...")

        #no device
        defaultDevice=self.asr.getDefaultDeviceId()
        if defaultDevice==-1:
            print("no device")
            self.window.setText("no device")
            return

        #load setting
        self.setting=SettingHandler({
            "lang":"Korean",
            "device":self.asr.deviceIdDict[defaultDevice]
        })
        self.setting.selectionListAll["lang"]=TranslateHandler.langCodeDict  #put dict for check conflict when load setting
        self.setting.selectionListAll["device"]=self.asr.deviceNameDict
        self.currentSetting=self.setting.loadSetting()
        self.setting.saveSetting(self.currentSetting)
        print("current Setting=============")
        print(self.currentSetting)


        #setup combobox
        self.window.setupComboBox(self.window.cb1,self.asr.deviceNameDict,self.currentSetting["device"],self.changeDevice)
        self.window.setupComboBox(self.window.cb2,TranslateHandler.langCodeDict,self.currentSetting["lang"],self.changeLang)

        #start asr model
        deviceId=self.setting.selectionListAll["device"][self.currentSetting["device"]]
        self.asr.start(self.modelName,deviceId,useCuda)

        # thread for data consumer
        lang=self.setting.selectionListAll["lang"][self.currentSetting["lang"]]
        self.asrOutputHandler = AsrOutputHandler(self.asr.asr_output_queue,lang)
        self.asrOutputHandler.outputSignal.connect(self.window.setTextAppend)
        self.asrOutputHandler.start()

    def changeDevice(self,text):
        print("changDevice"+str(text))
        self.currentSetting["device"]=text
        self.setting.saveSetting(self.currentSetting)
        device=self.setting.selectionListAll["device"][self.currentSetting["device"]]
        self.asr.changeDevice(device)

    def changeLang(self,text):
        print("changLang"+str(text))
        self.currentSetting["lang"]=text
        self.setting.saveSetting(self.currentSetting)
        lang=self.setting.selectionListAll["lang"][self.currentSetting["lang"]]
        self.asrOutputHandler.setLang(lang)



class AsrOutputHandler(QThread):
    outputSignal = pyqtSignal(str)

    def __init__(self, output_queue,lang):
        super().__init__()
        self.output_queue = output_queue
        self.lang=lang
        self.lock = threading.Lock()

    def setLang(self,lang):
        with self.lock:
            self.lang=lang

    def getLang(self):
        with self.lock:
            lang=self.lang
        return lang

    def run(self):
        #check model loaded
        firstOutput=self.output_queue.get()[0]
        self.outputSignal.emit(firstOutput)

        while True:
            text,sample_length,inference_time = self.output_queue.get()
            print(f"{sample_length:.3f}s\t{inference_time:.3f}s\t{text}")

            text=TranslateHandler.translate(text,tolang=self.getLang(),fromlang="ja")
            print(text)
            self.outputSignal.emit(text)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    guiHandler = GuiHandler(modelName="wav2vec2_large_xlsr_japanese_hiragana",useCuda=False)
    guiHandler.window.show()
    sys.exit(app.exec_())



"""
pyinstaller gui_handler.py -y -n wav2vec2_live_japanese_translator --hidden-import=pytorch --collect-data torch --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata importlib_metadata  --copy-metadata dataclasses
"""
