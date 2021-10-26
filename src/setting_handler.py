import os
import pickle


class SettingHandler:
    def __init__(self, defaultList):
        self.settingPath="setting.pickle"
        self.defaultList=defaultList
        self.selectionListAll=dict()



    def loadSetting(self,):
        currentSetting=dict()

        #load setting from file
        if os.path.exists(self.settingPath):
            with open(self.settingPath, 'rb') as f:
                currentSetting = pickle.load(f)

        #if no setting load from default
        for key in self.defaultList:
            if key not in currentSetting.keys():
                currentSetting[key]=self.defaultList[key]

        #check conflict, not in selectionList
        for key in self.defaultList:
            if key in self.selectionListAll.keys():
                if currentSetting[key] not in self.selectionListAll[key].keys():
                    currentSetting[key]=self.defaultList[key]

        return currentSetting

    def saveSetting(self,settingList):
        with open(self.settingPath, 'wb') as f:
            pickle.dump(settingList, f)








if __name__ == '__main__':
    settingHandler = SettingHandler()
    print(settingHandler.loadSetting())
    settingHandler.saveSetting({"lang":"en","device":"test_device"})
    print(settingHandler.loadSetting())
