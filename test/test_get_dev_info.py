# -*- coding: UTF-8 -*-
# @Time    : 2024/10/119:35
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : test_get_dev_info.py
# @IDE     : PyCharm
from serial_manager import Serial_Manager


class Dev_Info_Util:
    @classmethod
    def getDevInfo(cls, com: str):
        """
        获取设备信息
        :param com:
            串口号
        :return:
            state: True(成功)
            data:  版本号,Mac地址
        """
        CMD_S = ["TL_ATS_IN\n", "TL_GET_VER\n", "TL_GET_BTMAC\n", "TL_ATS_OFF\n"]

        boSuccess = Serial_Manager.openSerial(com)
        if not boSuccess:
            return False, [], "打开串口设备失败,请检查串口"

        try:
            lstRlt = []
            state, tmpLstRes = Serial_Manager.sendATCommand(CMD_S[0])
            if (not state) or ("SUCCESS" not in tmpLstRes[0]):
                return False, [], "进入工厂模式失败,请检查设备"

            state, tmpLstRes = Serial_Manager.sendATCommand(CMD_S[1])
            if (not state) or ("SUCCESS" not in tmpLstRes[0]):
                return False, [], "获取设备版本号失败,请检查设备"
            # 解析版本号
            VER_TAG = "VER="
            tmpStr: str = tmpLstRes[0]
            tmpIdx = tmpStr.find(VER_TAG)
            tmpVer = tmpStr[tmpIdx + len(VER_TAG): len(tmpStr)].strip()
            lstRlt.append(tmpVer)

            state, tmpLstRes = Serial_Manager.sendATCommand(CMD_S[2])
            if (not state) or ("SUCCESS" not in tmpLstRes[0]):
                return False, [], "获取设备Mac地址失败,请检查设备"
            # 解析Mac地址
            MAC_TAG = "BTMAC="
            tmpStr: str = tmpLstRes[0]
            tmpIdx = tmpStr.find(MAC_TAG)
            tmpMac = tmpStr[tmpIdx + len(MAC_TAG): len(tmpStr)].strip()
            lstRlt.append(tmpMac)

            # 退出工厂模式
            state, tmpLstRes = Serial_Manager.sendATCommand(CMD_S[3])
            if (not state) or ("SUCCESS" not in tmpLstRes[0]):
                print("退出工厂模式失败,请检查设备")

            return True, lstRlt, "Success"
        except Exception as e:
            print("获取设备信息失败:" + repr(e))
        finally:
            Serial_Manager.closeSerial()
        return False, [], "Fail"


if __name__ == "__main__":
    boState, rlts = Dev_Info_Util.getDevInfo("com11")
    print(boState, rlts)