import time

import fw_reader
from local_data_util import Local_Data_Util
from protocol import Protocol, Fwu_Ack_Packet, Fwu_Data_Ack_Packet
from serial_manager import Serial_Manager


class FW_Manager:
    fwData = None
    fwLen = 0
    curIndex = 0
    perPckSize = Protocol.FWU_MAX_DATA_LEN
    remainFwCnt = 0

    # 烧入状态
    BS_FREE = 0
    # 开始请求同步状态
    BS_REQUEST_SYNC = 1
    # 数据传输中
    BS_DATA_TRANSFER = 2
    # 数据传输结束
    BS_DATA_TRANSFER_END = 3
    # 升级成功
    BS_UPGRADE_SUCCESS = 4
    # 升级出错
    BS_UPGRADE_ERROR = 5

    # 状态切换
    MID_STATE_CHANGE = 0x00

    # 数据传输结束
    MID_DATA_TRANSFER_END = 0x01

    # 数据请求
    MID_ACK = 0x02

    # 烧入状态
    burn_state = BS_FREE

    # DEMO类型,调用清除Flash需要时间,因此需要额外等待时间
    DEMO_ERASE_TIMEOUT = 20000

    burn_progress = -1

    # qt线程(信号量回调事件)
    qthread_obj = None

    Print_Mode = 1
    SI_TAG_INFO = "info"
    SI_TAG_ERROR = "error"
    SI_TAG_EXCEPT = "except"
    SI_TAG_PROGRESS = "progress"
    SI_TAG_SUCCESS = "success"
    SI_TAG_END = "end"
    SI_TAG_COPEN = "cpen"
    SI_TAG_CHSTATE = "chstate"
    SI_TAG_CMODULE_WAIT = "cm_wait"

    @classmethod
    def clearData(cls):
        cls.fwData = None
        cls.fwLen = 0
        cls.curIndex = 0
        cls.perPckSize = Protocol.FWU_MAX_DATA_LEN
        cls.burn_state = cls.BS_FREE
        cls.remainFwCnt = 0
        cls.burn_progress = -1

    @classmethod
    def setFwData(cls, fwLen: int, fwData: bytes):
        cls.fwData = fwData
        cls.fwLen = fwLen
        cls.curIndex = 0
        cls.remainFwCnt = fwLen

    @classmethod
    def startFwBurn(cls, fwPath: str, comType: str):
        if cls.burn_state != cls.BS_FREE:
            cls.showInfo("当前不处于空闲状态,不能烧入!", cls.SI_TAG_ERROR)
            return

        cls.clearData()
        cls.showInfo(f"读取固件文件:{fwPath}", cls.SI_TAG_INFO)
        status, fw_data = fw_reader.readFromEx(fwPath)
        if not status:
            cls.showInfo("读取固件文件失败!", cls.SI_TAG_ERROR)
            return
        cls.showInfo(f"len={len(fw_data)}", cls.SI_TAG_INFO)
        cls.setFwData(len(fw_data), fw_data)

        cls.showInfo(f"打开串口:{comType}", cls.SI_TAG_INFO)
        status = Serial_Manager.openSerial(comType)
        if not status:
            cls.showInfo("打开串口失败!", cls.SI_TAG_ERROR)
            return

        cls.burn_progress = -1

        # 进入dfu模式前,先发送ATS指令
        preCms = ["TL_ATS_IN\n", "TL_GET_VER\n"]
        cls.showInfo("进入dfu模式前,先发送ATS指令...", cls.SI_TAG_INFO)
        for tmpCmd in preCms:
            boOK, rlts = Serial_Manager.sendATCommand(tmpCmd)
            # print(boOK, rlts[0])
            if boOK:
                cls.showInfo(f"{boOK}, {rlts[0]}", cls.SI_TAG_INFO)
            else:
                cls.showInfo(f"{boOK}", cls.SI_TAG_INFO)

        cls.showInfo("发送进入dfu模式指令...", cls.SI_TAG_INFO)
        boOK = Serial_Manager.enterDfuMode()
        cls.showInfo(f"进入dfu模式结果状态:{boOK}", cls.SI_TAG_INFO)
        if not boOK:
            cls.showInfo("进入dfu模式失败，退出烧入!", cls.SI_TAG_ERROR)
            return
        time.sleep(1)
        cls.showInfo("进入duf模式成功,执行开始烧入逻辑...", cls.SI_TAG_INFO)

        try:
            while True:
                # 空闲状态
                if cls.burn_state == cls.BS_FREE:
                    cls.showInfo("请求开始烧入...", cls.SI_TAG_INFO)
                    cls.burn_state = cls.BS_REQUEST_SYNC
                    cls.onBurnProgress(cls.curIndex)
                    cls.sendBurnStateMessage()

                    # demo版本需要额外等待时间
                    tmpAddTime = 0
                    binTypeValue = Local_Data_Util.getUpgradeTypeValue()
                    if binTypeValue == Local_Data_Util.FW_VALUE_DEMO:
                        tmpAddTime = cls.DEMO_ERASE_TIMEOUT

                    tmpPacket = Protocol.makeStartPacket(cls.fwLen, cls.fwData)
                    fwu_ack = Fwu_Ack_Packet()
                    rlt, resBuffer = Serial_Manager.sendPacketAck(tmpPacket, fwu_ack.getSize(), tmpAddTime)
                    if not rlt:
                        cls.showInfo("数据处理异常，烧入失败...1", cls.SI_TAG_ERROR)
                        break
                    fwu_ack.fromBuffer(resBuffer)

                    if (fwu_ack.header.sync_byte == Protocol.SYNC_BYTE) and (fwu_ack.header.pack_type == 0x52):
                        # drop response, wait ack
                        fwu_ack = Fwu_Ack_Packet()
                        rlt, resBuffer = Serial_Manager.readData(fwu_ack.getSize(), Serial_Manager.WAIT_ACK_TIMEOUT)
                        if not rlt:
                            cls.showInfo("数据处理异常，烧入失败...1.1", cls.SI_TAG_ERROR)
                            break
                        fwu_ack.fromBuffer(resBuffer)

                    tmpCheckSum = Protocol.make_checksum(resBuffer, len(resBuffer) - 1)
                    checkState = (fwu_ack.header.sync_byte == Protocol.SYNC_BYTE) and \
                                 (fwu_ack.header.pack_type == Protocol.PACK_IND) and \
                                 (fwu_ack.header.major_id == Protocol.ID_UPGRADE_INDICATOR) and \
                                 (fwu_ack.header.minor_id == Protocol.IND_UPGRADE_STATE_CHANGE) and \
                                 (fwu_ack.header.length == 1) and \
                                 (fwu_ack.state == Protocol.IND_UPGRADE_INIT_COMPLETE) and \
                                 (fwu_ack.checksum == tmpCheckSum)
                    if not checkState:
                        cls.showInfo("状态错误1.2:" + fwu_ack.showInfo(), cls.SI_TAG_ERROR)
                        break

                    # 开始传输数据
                    cls.showInfo("开始传输数据...", cls.SI_TAG_INFO)
                    cls.burn_state = cls.BS_DATA_TRANSFER
                    cls.sendBurnStateMessage()

                # 数据传输状态
                elif cls.burn_state == cls.BS_DATA_TRANSFER:
                    needSendData = False
                    tmpFwData = None
                    if cls.remainFwCnt >= cls.perPckSize:
                        tmpFwData = cls.fwData[cls.curIndex:cls.curIndex + cls.perPckSize]
                        cls.curIndex = cls.curIndex + cls.perPckSize
                        cls.remainFwCnt = cls.remainFwCnt - cls.perPckSize
                        needSendData = True
                    else:
                        if cls.remainFwCnt > 0:
                            tmpFwData = cls.fwData[cls.curIndex:cls.fwLen]
                            cls.curIndex = cls.curIndex + len(tmpFwData)
                            cls.remainFwCnt = cls.remainFwCnt - len(tmpFwData)
                            needSendData = True
                    if needSendData:
                        tmpPacket = Protocol.makeUpgradingPacket(tmpFwData)
                        fwu_ack = Fwu_Data_Ack_Packet()
                        rlt, resBuffer = Serial_Manager.sendPacketAck(tmpPacket, fwu_ack.getSize())
                        if not rlt:
                            cls.showInfo("数据处理异常，烧入失败...2", cls.SI_TAG_ERROR)
                            break
                        cls.onBurnProgress(cls.curIndex)

                        fwu_ack.fromBuffer(resBuffer)
                        tmpCheckSum = Protocol.make_checksum(resBuffer, len(resBuffer) - 1)
                        checkState = (fwu_ack.header.sync_byte == Protocol.SYNC_BYTE) and \
                                     (fwu_ack.header.pack_type == Protocol.PACK_IND) and \
                                     (fwu_ack.header.major_id == Protocol.ID_UPGRADE_INDICATOR) and \
                                     (fwu_ack.header.minor_id == Protocol.IND_UPGRADE_ACK) and \
                                     (fwu_ack.header.length == 0x02) and \
                                     (fwu_ack.checksum == tmpCheckSum)
                        if not checkState:
                            cls.showInfo("状态错误2.1:" + fwu_ack.showInfo(), cls.SI_TAG_ERROR)
                            break
                    else:
                        cls.showInfo("数据传输结束,发送结束状态数据包...", cls.SI_TAG_INFO)
                        cls.burn_state = cls.BS_DATA_TRANSFER_END
                        cls.sendBurnStateMessage()

                elif cls.burn_state == cls.BS_DATA_TRANSFER_END:
                    tmpPacket = Protocol.makeUpgradeEndPacket()
                    fwu_ack = Fwu_Ack_Packet()

                    rlt, resBuffer = Serial_Manager.sendPacketAck(tmpPacket, fwu_ack.getSize())
                    if not rlt:
                        cls.showInfo("数据处理异常，烧入失败...3", cls.SI_TAG_ERROR)
                        break

                    fwu_ack.fromBuffer(resBuffer)
                    checkState = (fwu_ack.header.sync_byte == Protocol.SYNC_BYTE) and \
                                 (fwu_ack.header.pack_type == Protocol.PACK_IND) and \
                                 (fwu_ack.header.major_id == Protocol.ID_UPGRADE_INDICATOR) and \
                                 (fwu_ack.header.minor_id == Protocol.IND_UPGRADE_DATA_TRANSFER_END)
                    if not checkState:
                        cls.showInfo("状态错误3.1:" + fwu_ack.showInfo(), cls.SI_TAG_ERROR)
                        break

                    # 读取状态数据(固件数据完成后)
                    fwu_ack = Fwu_Ack_Packet()
                    rlt, resBuffer = Serial_Manager.readData(fwu_ack.getSize(), Serial_Manager.WAIT_ACK_TIMEOUT)
                    if not rlt:
                        cls.showInfo("数据处理异常，烧入失败...3.2!", cls.SI_TAG_ERROR)
                        break
                    fwu_ack.fromBuffer(resBuffer)
                    tmpCheckSum = Protocol.make_checksum(resBuffer, len(resBuffer) - 1)
                    checkState = (fwu_ack.header.sync_byte == Protocol.SYNC_BYTE) and \
                                 (fwu_ack.header.pack_type == Protocol.PACK_IND) and \
                                 (fwu_ack.header.major_id == Protocol.ID_UPGRADE_INDICATOR) and \
                                 (fwu_ack.header.minor_id == Protocol.IND_UPGRADE_STATE_CHANGE) and \
                                 (fwu_ack.header.length == 0x01) and \
                                 (fwu_ack.state == Protocol.IND_UPGRADE_COMPLETE) and \
                                 (fwu_ack.checksum == tmpCheckSum)
                    if not checkState:
                        cls.showInfo("状态错误3.3:" + fwu_ack.showInfo(), cls.SI_TAG_ERROR)
                        break
                    cls.burn_state = cls.BS_UPGRADE_SUCCESS
                    cls.sendBurnStateMessage()

                elif cls.burn_state == cls.BS_UPGRADE_SUCCESS:
                    cls.showInfo("烧入成功...", cls.SI_TAG_SUCCESS)
                    break
        except Exception as e:
            cls.showInfo("烧入失败:" + repr(e), cls.SI_TAG_EXCEPT)
        finally:
            Serial_Manager.closeSerial()


    @classmethod
    def onBurnProgress(cls, curIndex):
        ratio = int(1.0 * curIndex / cls.fwLen * 100)
        if cls.burn_progress != ratio:
            cls.burn_progress = ratio
            # strInfo = "%d%s" % (cls.burn_progress, "%")
            cls.showInfo(f"已传输:{curIndex} 剩余:{cls.fwLen - curIndex}" , cls.SI_TAG_PROGRESS)

    @classmethod
    def showInfo(cls, info: str, errorTag: str):
        if cls.Print_Mode != 0:
            print(info)

        # 警告,这里的信号对象只能是信号对象所有者调用。否则会出现emit属于不存在的问题
        if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
            cls.qthread_obj.call_fun_signal.emit(errorTag, [info])

    @classmethod
    def sendBurnStateMessage(cls):
        if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
            cls.qthread_obj.call_fun_signal.emit(cls.SI_TAG_CHSTATE, [cls.burn_state])

    @classmethod
    def setQthreadObj(cls, qtObj):
        cls.qthread_obj = qtObj

    @classmethod
    def endBurnProcess(cls):
        cls.clearData()
        cls.qthread_obj = None
