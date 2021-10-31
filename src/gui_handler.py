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
    def __init__(self,useCuda):
        self.window=MainWindow()
        self.asr= LiveWav2Vec2()
        self.window.setText("loading...")
        self.useCuda=useCuda

        #no device
        defaultDevice=self.asr.getDefaultDeviceId()
        if defaultDevice==-1:
            print("no device")
            self.window.setText("no device")
            return

        #load setting
        self.setting=SettingHandler({
            "lang":"Korean",
            "device":self.asr.deviceIdDict[defaultDevice],
            "model":"wav2vec2_large_xlsr_japanese_hiragana_1028"
        })
        self.setting.selectionListAll["lang"]=TranslateHandler.langCodeDict  #put dict for check conflict when load setting
        self.setting.selectionListAll["device"]=self.asr.deviceNameDict
        self.setting.selectionListAll["model"]={
            "wav2vec2_large_xlsr_japanese_hiragana_1028":"wav2vec2_large_xlsr_japanese_hiragana_1028",
            "facebook/wav2vec2-large-960h-lv60-self":"facebook/wav2vec2-large-960h-lv60-self"
        }
        self.currentSetting=self.setting.loadSetting()
        self.setting.saveSetting(self.currentSetting)
        print("current Setting=============")
        print(self.currentSetting)


        #setup combobox
        self.window.setupComboBox(self.window.cb1,self.asr.deviceNameDict,self.currentSetting["device"],self.changeDevice)
        self.window.setupComboBox(self.window.cb2,TranslateHandler.langCodeDict,self.currentSetting["lang"],self.changeLang)
        self.window.setupComboBox(self.window.cb3,self.setting.selectionListAll["model"],self.currentSetting["model"],self.changeModel)

        #start asr model
        deviceId=self.setting.selectionListAll["device"][self.currentSetting["device"]]
        self.asr.start(self.currentSetting["model"],deviceId,self.useCuda)

        # thread for data consumer
        lang=self.setting.selectionListAll["lang"][self.currentSetting["lang"]]
        self.asrOutputHandler = AsrOutputHandler(self.asr.asr_output_queue,lang)
        self.asrOutputHandler.outputSignal.connect(self.window.setTextAppend)
        self.asrOutputHandler.start()








    def changeLang(self,selectedName):
        lang=self.saveSettingAndGetVal("lang",selectedName)
        self.asrOutputHandler.setLang(lang)

    def changeDevice(self,selectedName):
        device=self.saveSettingAndGetVal("device",selectedName)
        self.asr.changeDevice(device)

    def changeModel(self,selectedName):
        modelName=self.saveSettingAndGetVal("model",selectedName)
        self.window.setText("loading...")
        self.asr.changeModelProcess(modelName,self.useCuda)


    def saveSettingAndGetVal(self,settingType,selectedName):
        print("change "+settingType+str(selectedName))
        self.currentSetting[settingType]=selectedName
        self.setting.saveSetting(self.currentSetting)
        settingVal=self.setting.selectionListAll[settingType][self.currentSetting[settingType]]
        return settingVal





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

            text=TranslateHandler.translate(text,tolang=self.getLang(),fromlang="auto")
            print(text)
            self.outputSignal.emit(text)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    # useCuda = True if torch.cuda.is_available() else False
    guiHandler = GuiHandler(useCuda=False)
    guiHandler.window.show()
    sys.exit(app.exec_())



"""
pyinstaller gui_handler.py -y -n wav2vec2_live_japanese_translator --hidden-import=pytorch --collect-data torch --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata importlib_metadata  --copy-metadata dataclasses
"""
