import time

import serial


class Serial_Manager:
    baud_rate = 921600
    data_bit = 8
    parity = None
    stop_bit = 1
    flow_control = None
    time_out = 0.05

    serial_obj: serial.Serial = None
    over_time = 3000
    comType = ""

    WAIT_ACK_TIMEOUT = 1000
    READ_WRITE_TIMEOUT = 1000
    WAIT_RETRY_TIME = 0.1
    DEBUG_MODE = 0

    @classmethod
    def openSerial(cls, com: str):
        try:
            cls.comType = com
            cls.serial_obj = serial.Serial()
            cls.serial_obj.port = com
            cls.serial_obj.baudrate = cls.baud_rate
            cls.serial_obj.stopbits = serial.STOPBITS_ONE
            cls.serial_obj.bytesize = serial.EIGHTBITS
            cls.serial_obj.parity = serial.PARITY_NONE
            cls.serial_obj.timeout = cls.time_out
            cls.serial_obj.open()
            return True
        except Exception as e:
            print(repr(e))
            return False

    @classmethod
    def sendPacket(cls, packet: list):
        if cls.serial_obj is None:
            return False, []
        try:
            cls.showHexData(packet, 0)
            tmpBuf = bytes(packet)

            cls.serial_obj.write(tmpBuf)
            cls.serial_obj.flush()

            resBuffer = []
            last_ms = time.time() * 1000
            while True:
                count = cls.serial_obj.inWaiting()
                if count > 0:
                    tmpRdBuffer = cls.serial_obj.read(count)
                    for tmpV in tmpRdBuffer:
                        resBuffer.append(tmpV)
                    # 警告: 这里有小概率读取数据不完全的问题。需要对一个包进行校验才行
                    break
                dtime = time.time() * 1000 - last_ms
                if dtime > cls.over_time:
                    print("读取数据超时")
                    break
                # 防止程序占用主线程时间过长
                time.sleep(cls.WAIT_RETRY_TIME)
            cls.showHexData(resBuffer, 1)
            return len(resBuffer) > 0, resBuffer
        except Exception as e:
            print(repr(e))
            return False, []

    @classmethod
    def sendPacketAck(cls, packet: list, ackCnt: int, addTime: int = 0):
        if cls.serial_obj is None:
            return False, []
        try:
            cls.showHexData(packet, 0)
            tmpWtBuf = bytes(packet)

            cls.serial_obj.write(tmpWtBuf)
            cls.serial_obj.flush()

            resBuffer = []
            last_ms = time.time() * 1000
            while True:
                count = cls.serial_obj.inWaiting()
                if count > 0:
                    tmpRdBuffer = cls.serial_obj.read(ackCnt)
                    readSize = len(tmpRdBuffer)
                    if readSize != ackCnt:
                        print(f"读取数据长度:{readSize}与要求的:{ackCnt},不符合")
                        return False, []
                    else:
                        for tmpV in tmpRdBuffer:
                            resBuffer.append(tmpV)
                        # 警告: 这里有小概率读取数据不完全的问题。需要对一个包进行校验才行
                        break
                dtime = time.time() * 1000 - last_ms
                if dtime > cls.over_time + addTime:
                    print("读取数据超时")
                    break
                time.sleep(cls.WAIT_RETRY_TIME)
            cls.showHexData(resBuffer, 1)
            return len(resBuffer) > 0, resBuffer
        except Exception as e:
            print(repr(e))
            return False, []

    @classmethod
    def sendATCommand(cls, command: str):
        if cls.serial_obj is None:
            return False, []
        try:
            tmpBuf = command.encode("utf-8")
            print("send->", tmpBuf)
            cls.serial_obj.write(tmpBuf)
            cls.serial_obj.flush()

            resBuffer = []
            last_ms = time.time() * 1000
            while True:
                count = cls.serial_obj.inWaiting()
                if count > 0:
                    tmpRdBuf = cls.serial_obj.read(count)
                    tmpResInfo = tmpRdBuf.decode("utf-8")
                    print("rec->", tmpResInfo)
                    resBuffer.append(tmpResInfo)
                    break
                dtime = time.time() * 1000 - last_ms
                if dtime > cls.over_time:
                    print("读取数据超时")
                    break
                time.sleep(cls.WAIT_RETRY_TIME)
            return len(resBuffer) > 0, resBuffer
        except Exception as e:
            print(repr(e))
            return False, []

    @classmethod
    def readData(cls, readCnt: int, timeOut: int):
        if cls.serial_obj is None:
            return False, []
        try:
            resBuffer = []
            last_ms = time.time() * 1000
            while True:
                count = cls.serial_obj.inWaiting()
                if count > 0:
                    tmpRdBuffer = cls.serial_obj.read(readCnt)
                    readSize = len(tmpRdBuffer)
                    if readSize != readCnt:
                        print(f"读取数据长度:{readSize}与要求的:{readCnt},不符合")
                        return False, []
                    else:
                        for tmpV in tmpRdBuffer:
                            resBuffer.append(tmpV)
                        # 警告: 这里有小概率读取数据不完全的问题。需要对一个包进行校验才行
                        break
                dtime = time.time() * 1000 - last_ms
                if dtime > timeOut:
                    print("读取数据超时")
                    break
                time.sleep(cls.WAIT_RETRY_TIME)
            return len(resBuffer) > 0, resBuffer
        except Exception as e:
            print(repr(e))
            return False, []

    @classmethod
    def closeSerial(cls):
        if cls.serial_obj is not None:
            cls.serial_obj.close()
            cls.serial_obj = None

    @classmethod
    def showHexData(cls, data: list, typeTag: int = 0):
        if cls.DEBUG_MODE == 0:
            return

        if len(data) == 0:
            return

        max_size_show = 40
        if typeTag == 0:
            count = 0
            strInfo = ""
            for tmpV in data:
                strInfo = strInfo + ("0x%02x" % tmpV) + ","
                count = count + 1
                if count > max_size_show:
                    strInfo = strInfo + "..."
                    break
            print("send->", strInfo)
        else:
            count = 0
            strInfo = ""
            for tmpV in data:
                strInfo = strInfo + ("0x%02x" % tmpV) + ","
                count = count + 1
                if count > max_size_show:
                    strInfo = strInfo + "..."
                    break
            print("receive->", strInfo)

    @classmethod
    def enterDfuMode(cls):
        """
        进行烧入之前，需要向耳机发送进入Dfu命令指令
        警告：进入Dfu模式(升级模式)后,发送其它AT指令无效,需要按设备Power键,关机开机才能恢复功能
        """
        enterDfuCmd = "TL_DFU_IN\n"
        boOK, rlts = cls.sendATCommand(enterDfuCmd)
        print(boOK, rlts)
        return boOK and ("SUCCESS" in rlts[0])