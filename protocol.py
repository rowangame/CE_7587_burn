
# 消息包头结结构体
from local_data_util import Local_Data_Util


class Fwu_Header:
    def __init__(self):
        self.sync_byte = -1
        self.pack_type = -1
        self.major_id = -1
        self.minor_id = -1
        self.length = -1

    def getSize(self):
        return 5

    def getBuffer(self):
        tmpBuffer = []
        tmpBuffer.append(self.sync_byte)
        tmpBuffer.append(self.pack_type)
        tmpBuffer.append(self.major_id)
        tmpBuffer.append(self.minor_id)
        tmpBuffer.append(self.length)
        return tmpBuffer


# 固件内容包头结构体
class Fwu_Data_Header:
    def __init__(self):
        self.sync_byte = -1
        self.pack_type = -1
        self.major_id = -1
        self.minor_id = -1
        self.length = [-1, -1]

    def getSize(self):
        return 4 + 2

    def getBuffer(self):
        tmpBuffer = []
        tmpBuffer.append(self.sync_byte)
        tmpBuffer.append(self.pack_type)
        tmpBuffer.append(self.major_id)
        tmpBuffer.append(self.minor_id)
        tmpBuffer.append(self.length[0])
        tmpBuffer.append(self.length[1])
        return tmpBuffer

# 固件升级初始化消息包
class Fwu_Init_Packet:
    def __init__(self):
        self.header = Fwu_Header()
        self.fw_size = [-1, -1, -1]
        self.fw_checksum = -1
        self.data_len = [-1, -1]
        self.upgrade_type = -1
        self.checksum = -1

    def getSize(self):
        return self.header.getSize() + (3 + 1 + 2 + 1 + 1)

    def getBuffer(self):
        tmpBuffer = []

        tmpHdBuf = self.header.getBuffer()
        for tmpV in tmpHdBuf:
            tmpBuffer.append(tmpV)

        tmpBuffer.append(self.fw_size[0])
        tmpBuffer.append(self.fw_size[1])
        tmpBuffer.append(self.fw_size[2])
        tmpBuffer.append(self.fw_checksum)

        tmpBuffer.append(self.data_len[0])
        tmpBuffer.append(self.data_len[1])
        tmpBuffer.append(self.upgrade_type)

        return tmpBuffer


# 消息包结束
class Fwu_End_Packet:
    def __init__(self):
        self.header = Fwu_Header()
        self.checksum = -1

    def getSize(self):
        return self.header.getSize() + 1

    def getBuffer(self):
        tmpBuffer = []

        tmpHdBuf = self.header.getBuffer()
        for tmpV in tmpHdBuf:
            tmpBuffer.append(tmpV)

        return tmpBuffer


# 固件内容结构体
class Fwu_Data_Packet:
    def __init__(self):
        self.header = Fwu_Data_Header()
        self.reserved = [0, 0]
        self.data = []
        self.checksum = -1

    def getSize(self):
        return self.header.getSize() + (2 + len(self.data) + 1)

    def getBuffer(self):
        tmpBuffer = []

        tmpHdBuffer = self.header.getBuffer()
        for tmpV in tmpHdBuffer:
            tmpBuffer.append(tmpV)

        tmpBuffer.append(self.reserved[0])
        tmpBuffer.append(self.reserved[1])

        for tmpV in self.data:
            tmpBuffer.append(tmpV)

        return tmpBuffer

# 状态请求回复消息包
class Fwu_Ack_Packet:
    def __init__(self):
        self.header = Fwu_Header()
        self.state = -1
        self.checksum = -1

    def getSize(self):
        return self.header.getSize() + 2

    def fromBuffer(self, buffer: list):
        self.header.sync_byte = buffer[0]
        self.header.pack_type = buffer[1]
        self.header.major_id = buffer[2]
        self.header.minor_id = buffer[3]
        self.header.length = buffer[4]
        self.state = buffer[5]
        self.checksum = buffer[6]

    def getBuffer(self):
        tmpBuffer = []

        tmpHdBuffer = self.header.getBuffer()
        for tmpV in tmpHdBuffer:
            tmpBuffer.append(tmpV)

        tmpBuffer.append(self.state)
        tmpBuffer.append(self.checksum)

        return tmpBuffer

    def showInfo(self):
        tmpBuffer = self.getBuffer()
        strInfo = ""
        for tmpV in tmpBuffer:
            strInfo += "%02x" % tmpV + " "
        return strInfo


# 固件内容请求回复消息包
class Fwu_Data_Ack_Packet:
    def __init__(self):
        self.header = Fwu_Header()
        self.reserved = [0, 0]
        self.checksum = -1

    def getSize(self):
        return self.header.getSize() + (2 + 1)

    def fromBuffer(self, buffer: list):
        self.header.sync_byte = buffer[0]
        self.header.pack_type = buffer[1]
        self.header.major_id = buffer[2]
        self.header.minor_id = buffer[3]
        self.header.length = buffer[4]
        self.reserved[0] = buffer[5]
        self.reserved[1] = buffer[6]
        self.checksum = buffer[7]

    def getBuffer(self):
        tmpBuffer = []

        tmpHdBuffer = self.header.getBuffer()
        for tmpV in tmpHdBuffer:
            tmpBuffer.append(tmpV)

        tmpBuffer.append(self.reserved[0])
        tmpBuffer.append(self.reserved[1])

        tmpBuffer.append(self.checksum)

        return tmpBuffer

    def showInfo(self):
        tmpBuffer = self.getBuffer()
        strInfo = ""
        for tmpV in tmpBuffer:
            strInfo += "%02x" % tmpV + " "
        return strInfo


class Protocol(object):
    # 每一包最大的数据长度(BT蓝牙最多支持1024)
    FWU_MAX_DATA_LEN = 960

    # FWU end packet and data header is 6 bytes
    FWU_MIN_READ_LEN = 6

    # Sync Byte ('B')
    SYNC_BYTE = 0x42

    # Command Packet ('C')
    PACK_CMD = 0x43

    # Data Packet('D')
    PACK_DATA = 0x44

    # Indication Packet ('I')
    PACK_IND = 0x49

    # Upgrade Control Commands (Major Id: 0x1B)
    ID_UPGRADE_CTRL_CMD = 0x1B

    # Minor Id
    CMD_UPGRADE_START = 0x00
    CMD_UPGRADE_DATA_TRANSFER_END = 0x01
    CMD_UPGRADE_RESERVED = 0x02
    CMD_HOST_READY_RESET = 0x03

    UPGRADE_TYPE_MAIN_FW = 0x00

    # Upgrade Indicator (Major Id: 0x1B)
    ID_UPGRADE_INDICATOR = 0x1B

    # Minor Id
    IND_UPGRADE_STATE_CHANGE = 0x00
    IND_UPGRADE_DATA_TRANSFER_END = 0x01
    IND_UPGRADE_ACK = 0x02

    # Upgrade State Change Indicator
    IND_UPGRADE_INIT_COMPLETE = 0x0
    IND_UPGRADIND = 0x1
    IND_UPGRADE_COMPLETE = 0x2
    IND_UPGRADE_FAIL = 0x3

    # Upgrade Data Transfer End Indicator
    IND_OK = 0x0
    IND_IMAGE_CHECKSUM_FAIL = 0x1
    IND_IMAGE_SIZE_FAIL = 0x2
    IND_IMAGE_VERIFY_FAIL = 0x3

    # Data Packet
    # Data Source Type
    DATA_SOURCE_SPP = 0x70
    DATA_SOURCE_OPP = 0x71
    DATA_SOURCE_UART = 0x72
    DATA_SOURCE_BLE = 0x73

    @classmethod
    def make_checksum(cls, dataLst: list, nLen: int):
        nChkSum = 0
        for i in range(nLen):
            nChkSum ^= dataLst[i]
        return nChkSum

    @classmethod
    def make_checksum_ex(cls, dataLst: bytes, nLen: int):
        nChkSum = 0
        for i in range(nLen):
            nChkSum ^= dataLst[i]
        return nChkSum

    @classmethod
    def bytesToList(cls, bts):
        rlt = []
        for tmpB in bts:
            rlt.append(tmpB)
        return rlt

    @classmethod
    def validateCheckSum(cls, src: list, checkSumValue: int):
        value = cls.make_checksum(src, len(src))
        return value, checkSumValue, value == checkSumValue

    @classmethod
    def validateCheckSumByPacket(cls, pckData: bytes):
        tmpLen = len(pckData)
        checkValue = pckData[tmpLen - 1]
        makeCheckSum = cls.make_checksum_ex(pckData[0: tmpLen - 1])
        return checkValue == makeCheckSum

    @classmethod
    def makeStartPacket(cls, fwLen: int, fwData: bytes):
        fwu_init_packet = Fwu_Init_Packet()

        fwu_init_packet.header.sync_byte = cls.SYNC_BYTE
        fwu_init_packet.header.pack_type = cls.PACK_CMD
        fwu_init_packet.header.major_id = cls.ID_UPGRADE_CTRL_CMD
        fwu_init_packet.header.minor_id = cls.CMD_UPGRADE_START
        fwu_init_packet.header.length = fwu_init_packet.getSize() - fwu_init_packet.header.getSize() - 1

        fwu_init_packet.fw_size[0] = (fwLen >> 16) & 0xff
        fwu_init_packet.fw_size[1] = (fwLen >> 8) & 0xff
        fwu_init_packet.fw_size[2] = fwLen & 0xff

        # 数据校验码(1位)
        # 固件文件 (~(data1 + data2 + data3 + ... + dataN) + 1) & 0xff
        sumV = 0
        for tmpV in fwData:
            sumV += tmpV
        fwDataCheckSum = (~sumV + 1) & 0xff
        fwu_init_packet.fw_checksum = fwDataCheckSum

        fwu_init_packet.data_len[0] = (cls.FWU_MAX_DATA_LEN >> 8) & 0xff
        fwu_init_packet.data_len[1] = cls.FWU_MAX_DATA_LEN & 0xff

        # 这里新增了添加升级类型:
        # fwu_init_packet.upgrade_type = cls.UPGRADE_TYPE_MAIN_FW
        fwu_init_packet.upgrade_type = Local_Data_Util.getUpgradeTypeValue()

        tmpBuffer = fwu_init_packet.getBuffer()
        fwu_init_packet.checksum = cls.make_checksum(tmpBuffer, len(tmpBuffer))
        tmpBuffer.append(fwu_init_packet.checksum)

        return tmpBuffer

    """
    固件数据包
    """
    @classmethod
    def makeUpgradingPacket(cls, fwSecData: bytes):
        data_packet = Fwu_Data_Packet()
        data_packet.header.sync_byte = cls.SYNC_BYTE
        data_packet.header.pack_type = cls.PACK_DATA
        data_packet.header.major_id = cls.DATA_SOURCE_UART
        data_packet.header.minor_id = 0x00

        # 数据长度（固件长度+2个预留位)
        fwLen = len(fwSecData) + 2
        data_packet.header.length[0] = (fwLen >> 8) & 0xff
        data_packet.header.length[1] = fwLen & 0xff

        data_packet.reserved[0] = 0
        data_packet.reserved[1] = 0

        for tmpV in fwSecData:
            data_packet.data.append(tmpV)

        tmpBuffer = data_packet.getBuffer()
        data_packet.checksum = cls.make_checksum(tmpBuffer, len(tmpBuffer))
        tmpBuffer.append(data_packet.checksum)

        return tmpBuffer

    """
    数据传送结束数据包
    """
    @classmethod
    def makeUpgradeEndPacket(cls):
        data_packet = Fwu_End_Packet()

        data_packet.header.sync_byte = cls.SYNC_BYTE
        data_packet.header.pack_type = cls.PACK_CMD
        data_packet.header.major_id = cls.ID_UPGRADE_CTRL_CMD
        data_packet.header.minor_id = cls.CMD_UPGRADE_DATA_TRANSFER_END
        data_packet.header.length = 0

        tmpBuffer = data_packet.getBuffer()
        data_packet.checksum = cls.make_checksum(tmpBuffer, len(tmpBuffer))
        tmpBuffer.append(data_packet.checksum)

        return tmpBuffer




