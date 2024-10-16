# -*- coding: UTF-8 -*-
# @Time    : 2024/9/2616:59
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : local_data_util.py
# @IDE     : PyCharm
import os
import pickle


class Local_Data_Util:
    # bt 文件类型 (固件文件选择升级类型相关)
    FW_TYPE_BT = "bt"

    # voice 文件类型 (固件文件选择升级类型相关)
    FW_TYPE_VOICE = "voice"

    # demo 文件类型 (固件文件选择升级类型相关)
    FW_TYPE_DEMO = "demo"

    # 升级类型(c模块协议)
    MODULE_TYPE_C = "c"

    # 升级类型(python模块协议)
    MODULE_TYPE_PY = "py"

    # bt类型对应的数值
    FW_VALUE_BT = 0x00

    # voice类型对应的数值
    FW_VALUE_VOICE = 0x02

    # demo类型对应的数值
    FW_VALUE_DEMO = 0x03

    # 当前选择的文件数据(本地与内存共享)
    fwSharedData = {
        "btPath": "",           # bt 类型文件路径
        "voicePath": "",        # voice 类型文件路径
        "demoPath": "",         # demo 类型文件路径
        "sltType": "bt",        # 选中的类型("bt","voice","demo"类型 默认选择bt类型)
        "moduleType": "c"       # 升级类型(”c":c模块协议,"py":python模块协议)
    }

    boLoaded: bool = False      # 是否从本地加载了数据

    @classmethod
    def loadData(cls):
        """
        加载本地数据
        :return state:
            True(加载成功)
            False(加载失败)
        data:
            "fw_path" 固件文件目录
        """
        filePath = os.getcwd() + "\\data\\data.pickle"
        if os.path.exists(filePath):
            try:
                tmpFile = open(filePath, 'rb')
                cls.fwSharedData = pickle.load(tmpFile)
                cls.boLoaded = True
                return True
            except Exception as e:
                print(repr(e))
        return False

    @classmethod
    def saveData(cls):
        """
        保存数据对象到本地
        :param data:
            数据对象,带bin文件路径的数据
        :return:
            state: True(成功) False(失败)
        """
        try:
            filePath = os.getcwd() + "\\data\\data.pickle"
            tmpFile = open(filePath, 'wb')
            pickle.dump(Local_Data_Util.fwSharedData, tmpFile)
            tmpFile.close()
            return True
        except Exception as e:
            print(repr(e))
        return False

    @classmethod
    def getUpgradeTypeValue(cls):
        """
        得到升级文件的类型参数
        :return:
            00:bt voice:02 demo:03
        """
        kValues = {
            "bt": cls.FW_VALUE_BT,
            "voice": cls.FW_VALUE_VOICE,
            "demo": cls.FW_VALUE_DEMO
        }
        return kValues[cls.fwSharedData["sltType"]]

    @classmethod
    def getUpgradeBinFile(cls):
        """
        根据默认的升级类型,得到bin文件本地路径
        :return:
           bin文件路径
        """
        if cls.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
            return cls.fwSharedData["btPath"]
        elif cls.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
            return cls.fwSharedData["voicePath"]
        else:
            return cls.fwSharedData["demoPath"]