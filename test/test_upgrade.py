# -*- coding: UTF-8 -*-
# @Time    : 2024/9/279:03
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : test_upgrade.py
# @IDE     : PyCharm
import random
import sys
import time

import fw_reader
from fw_manager import FW_Manager
from protocol import Protocol
from serial_manager import Serial_Manager


def testIntBits():
    a = 962
    hb = (a >> 8) & 0xff
    lb = a & 0xff
    print(a, hex(hb), hex(lb))
    bts = a.to_bytes(2, byteorder="big", signed=False)
    print(bts)


def showHexPacket(data: list, tag: str):
    print(tag)
    strInfo = ""
    for tmpV in data:
        strInfo = strInfo + "%02x" % tmpV + " "
        # strInfo = strInfo + "%02d" % tmpV + " "
    print(strInfo)


def testCmds():
    try:
        Serial_Manager.openSerial("com4")

        cms = ["TL_ATS_IN\n", "TL_GET_VER\n", "TL_GET_BTNAME\n", "TL_GET_BTMAC\n", "TL_GET_MODEL\n", "TL_GET_BAT_LEVEL\n"]

        for tmpCmd in cms:
            cmd = tmpCmd
            state, rlt = Serial_Manager.sendATCommand(cmd)
            print(state, rlt)
            time.sleep(1)

        # boOK = Serial_Manager.enterDfuMode()
        # print("Enter dfu mode:", boOK)
    except Exception as e:
        print(repr(e))
    finally:
        Serial_Manager.closeSerial()


def listBurnPacketByHex():
    fw_path = "./fw/XG_BT_FW_3nod_240814_0401_Test_DFU.bin"
    data, length = fw_reader.readFrom(fw_path)
    print(f"load fw...length={length}")
    FW_Manager.setFwData(length, data)

    startPck = Protocol.makeStartPacket(FW_Manager.fwLen, FW_Manager.fwData)
    showHexPacket(startPck, "start")

    remainLen = length
    dataIndex = 0
    curIndex = 0
    while True:
        if remainLen >= Protocol.FWU_MAX_DATA_LEN:
            tmpBuf = FW_Manager.fwData[curIndex: curIndex + Protocol.FWU_MAX_DATA_LEN]
            fwPck = Protocol.makeUpgradingPacket(tmpBuf)
            print(f"size={len(fwPck)}")
            showHexPacket(fwPck, f"fw={dataIndex}")
            remainLen = remainLen - Protocol.FWU_MAX_DATA_LEN
            dataIndex = dataIndex + 1
        elif remainLen > 0:
            tmpBuf = FW_Manager.fwData[curIndex: Protocol.FWU_MAX_DATA_LEN]
            fwPck = Protocol.makeUpgradingPacket(tmpBuf)
            showHexPacket(fwPck, f"fw={dataIndex}")
            remainLen = remainLen - Protocol.FWU_MAX_DATA_LEN
            dataIndex = dataIndex + 1
        if remainLen == 0:
            break
        break

    endPck = Protocol.makeUpgradeEndPacket()
    showHexPacket(endPck, "end")


def testBurnFlush():
    fw_path = "./fw/XG_BT_FW_3nod_240814_0401_Test_DFU.bin"
    comType = "com11"
    FW_Manager.startFwBurn(fw_path, comType)


def test_Args():
    print(sys.argv)

    fw_file = ""
    comType = ""
    print(f"com={comType} fw_file={fw_file}")


def test_random():
    span_tag = "SPAN_TAG_"
    strInfo = span_tag * 2
    print(strInfo)

    for i in range(1100):
        tmpA = random.randint(1, 255)
        print(tmpA, "%02x" % tmpA)


# testIntBits()
# testCmds()
# testIntBits()
test_random()