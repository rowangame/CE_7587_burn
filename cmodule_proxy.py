"""
使用C模块进行升级(加快升级速度)
"""
import mmap
import os
import subprocess
import threading
import time

from config_data import Config_Data
from fw_manager import FW_Manager
from local_data_util import Local_Data_Util


class CModule_Proxy:
    C_TAG_START = "#<"
    C_TAG_END = ">"

    C_MSG_INFO = 1
    C_MSG_ERROR = 2
    C_MSG_EXCEPT = 3
    C_MSG_PROGRESS = 4
    C_MSG_BURN_STATE = 5

    C_BURN_STATE_INIT = 0
    C_BURN_STATE_START = 1
    C_BURN_STATE_REQ_BURN = 2
    C_BURN_STATE_DATA_TRANSFER = 3
    C_BURN_STATE_DATA_FINISH = 4
    C_BURN_STATE_REQ_END = 5
    C_BURN_STATE_END_SUCCESS = 6
    C_BURN_STATE_END_FAIL = 7

    # qt线程(信号量回调事件)
    qthread_obj = None

    Print_Mode = 1

    @classmethod
    def setQthreadObj(cls, qtObj):
        cls.qthread_obj = qtObj

    @classmethod
    def showInfo(cls, info: str, errorTag: str):
        if cls.Print_Mode != 0:
            print(info)

        # 警告,这里的信号对象只能是信号对象所有者调用。否则会出现emit属于不存在的问题
        if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
            cls.qthread_obj.call_fun_signal.emit(errorTag, [info])

    @classmethod
    def start_cmodule_proxy(cls, execPath: str, fwPath: str, comType: str, binTypeValue: int, mmShareName: str):
        """
        C协议升级
        :param execPath:
            C模块应用程序路径
        :param fwPath:
            bin文件路径
        :param comType:
            串口类型
        :param binTypeValue:
            升级类型数值 00:bt voice:02 demo:03
        :param mmShareName
            共享内存名
        :return:
        """
        process = None
        try:
            # 使用subprocess.Popen来启动程序并捕获输出
            process = subprocess.Popen(
                [execPath] + [comType, fwPath, str(binTypeValue), mmShareName],
                stdout=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏控制台窗口
            )

            # communicate() 用于与子进程交互，并获取完整的输出
            # 注意:stdout和stderr是字节字符串,可能需要解码成文本格式
            # stdout, stderr = process.communicate()

            # 等待进程结束并获取退出状态
            process.wait()

            # 等待结束
            Config_Data.mCModuleWaiting = False

            # 警告:
            # 这里由c++模块的内存共享机㓡实现实时读取数据,因些不再处理读取逻辑
            # allLines = stdout.split("\n")
            # print("-----------stdout----------------")
            # print(allLines)
            # for line in allLines:
            #     # 分析进行打印的提示值
            #     if line.startswith(cls.C_TAG_START):
            #         sIdx = len(cls.C_TAG_START)
            #         eIdx = line.find(cls.C_TAG_END)
            #         # 状态值
            #         tmpState = int(line[sIdx:eIdx])
            #         # 提示值
            #         tmpValue = line[eIdx + 1:len(line)]
            #         # print(f"tmpState={tmpState} tmpValue={tmpValue}")
            #         # 分析状态值
            #         if tmpState == cls.C_MSG_BURN_STATE:
            #             # 得到状态数值(#<5>state=x)
            #             burnState = tmpValue.split("=")[1]
            #             cls.analyzeBurnState(int(burnState))
            #         elif tmpState == cls.C_MSG_PROGRESS:
            #             # 得到进度数据 (#<4>Upgrading:<x%>)
            #             strProgressValue = tmpValue.split(":")[1]
            #             # 去掉左边的 "<" 和右边的 "%>" 得到数值
            #             strProgress = strProgressValue[1:len(strProgressValue) - 2]
            #             tmpProgress = int(strProgress)
            #             cls.handleProgress(tmpProgress)
            #         else:
            #             cls.handleMessage(tmpState, tmpValue)
            #         time.sleep(0.1)
        except FileNotFoundError:
            cls.showInfo(f"C模块未找到:{execPath}", FW_Manager.SI_TAG_ERROR)
        except Exception as e:
            cls.showInfo(f"执行过程中发生错误:{repr(e)}", FW_Manager.SI_TAG_ERROR)
        finally:
            # 等待结束
            Config_Data.mCModuleWaiting = False

            # 等待数据读取线程结束,防止状态混乱
            if Config_Data.mCModuleStateThread is not None:
                Config_Data.mCModuleStateThread.join()

            if process is not None:
                # 确保进程已结束并清理资源 (如果进程还在运行)
                if process.poll() is None:
                    # 终止进程
                    process.terminate()
                if process.stdout is not None:
                    process.stdout.close()
            # 通知ui结束事件
            cls.showInfo("end", FW_Manager.SI_TAG_END)

    @classmethod
    def showCModuleWaiting(cls):
        seconds = 0
        lastTickMs = 0
        while True:
            curTickMs = int(time.time() * 1000)
            if curTickMs - lastTickMs > 1000:
                lastTickMs = curTickMs
                seconds += 1
                if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
                    cls.qthread_obj.call_fun_signal.emit(FW_Manager.SI_TAG_CMODULE_WAIT, [seconds])
            if not Config_Data.mCModuleWaiting:
                break
            time.sleep(0.2)

    @classmethod
    def showCModuleState(cls):
        # 警告:
        # 用Python subprocess.open方法调用C++进程时,如果这个进行在创建共享内存对象时,
        # Python程序先创造一个内存访问对象,则C++进程无法创建共享对象,会出现错误代码(id:87)
        # Chat GPT4.0 给出的可能原因是权限不够，其实是访问冲突导致的，AI有局限性。必须认真分析问题
        # 否则，问题卡个几个月也是有可能
        # 因此这里等待了几秒钟的时间,让C++进程能成功创建共享内存
        SAFE_WAIT_TIME_SECS = 8
        seconds = 0
        lastTickMs = 0
        while True:
            curTickMs = int(time.time() * 1000)
            if curTickMs - lastTickMs > 1000:
                lastTickMs = curTickMs
                seconds += 1
                if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
                    cls.qthread_obj.call_fun_signal.emit(FW_Manager.SI_TAG_CMODULE_WAIT, [seconds])
            time.sleep(0.2)
            if seconds >= SAFE_WAIT_TIME_SECS:
                break

        # 与C模块共享内存一至大小
        SHARED_MEMORY_SIZE = 512 * 1024

        shared_memory = None
        try:
            readIndex = 0

            msgInfoSize = 4
            startIndex = msgInfoSize
            perSize = 128  # sizeof(unsigned short) + sizeof(unsigned char) + sizeof(char buffer[125])

            lastTick = time.time()
            max_retry_time = 20

            # 打开共享内存
            shared_memory = mmap.mmap(-1, SHARED_MEMORY_SIZE, tagname=Config_Data.mMMShareName, access=mmap.ACCESS_READ)
            while True:
                shared_memory.seek(0)

                btMsgInfo = shared_memory.read(msgInfoSize)
                curIndex = int.from_bytes(btMsgInfo[0:2], byteorder="little", signed=False)
                isEnd = int.from_bytes(btMsgInfo[2:3], byteorder="little", signed=False)
                reserved = int.from_bytes(btMsgInfo[3:4], byteorder="little", signed=False)

                if readIndex < curIndex:
                    # 移动到指定的起始位置
                    shared_memory.seek(startIndex)
                    # 从该位置读取指定长度的数据
                    data = shared_memory.read(perSize)
                    """
                    struct MyMsgData {
                            unsigned short index;       // 当前数据索引位
                            unsigned char len;          // 消息长度
                            char buffer[125];           // 消息内容
                    };
                    """
                    # 这里与c++模块内存共享数据内容一致
                    # idxMsgData = data[0:2]
                    # tmpReadIndex = int.from_bytes(idxMsgData, byteorder="little", signed=False)
                    tmpMsgLen = int(data[2:3][0])
                    line = ""
                    if tmpMsgLen > 0:
                        line = data[3:3 + tmpMsgLen].decode("GBK")
                    # print(f"tmpReadIndex={tmpReadIndex}, msgLen={tmpMsgLen} ctx={line}")
                    if len(line) > 0:
                        try:
                            # 分析进行打印的提示值
                            if line.startswith(cls.C_TAG_START):
                                sIdx = len(cls.C_TAG_START)
                                eIdx = line.find(cls.C_TAG_END)
                                # 状态值
                                tmpState = int(line[sIdx:eIdx])
                                # 提示值
                                tmpValue = line[eIdx + 1:len(line)]
                                # print(f"tmpState={tmpState} tmpValue={tmpValue}")
                                # 分析状态值
                                if tmpState == cls.C_MSG_BURN_STATE:
                                    # 得到状态数值(#<5>state=x)
                                    burnState = tmpValue.split("=")[1]
                                    cls.analyzeBurnState(int(burnState))
                                elif tmpState == cls.C_MSG_PROGRESS:
                                    # 得到进度数据 (#<4>Upgrading:<x%>\n)
                                    strProgressValue = tmpValue.split(":")[1]
                                    # 去掉左边的 "<" 和右边的 "%>" 得到数值
                                    strProgress = strProgressValue[1:len(strProgressValue) - 3]
                                    tmpProgress = int(strProgress)
                                    cls.handleProgress(tmpProgress)
                                else:
                                    cls.handleMessage(tmpState, tmpValue)
                        except Exception as e:
                            print("showCModuleState.read error?" + repr(e))

                    startIndex += perSize
                    readIndex += 1
                    lastTick = time.time()

                # 当共享数据缓冲区有数据时,直接读取(不需要判断结束标记,解决读取数据不完全的问题)
                if readIndex < curIndex:
                    time.sleep(0.2)
                    continue

                # 结束标记
                if isEnd > 0:
                    print(f"正常结束状态:{isEnd} totalIndex={curIndex}")
                    break

                curTick = time.time()
                dtime = curTick - lastTick
                if dtime > max_retry_time:
                    print(f"读取数据超时:dtime={dtime}>{max_retry_time}(s),关闭")
                    break
                if not Config_Data.mCModuleWaiting:
                    break
                time.sleep(0.2)
        except Exception as e:
            print("showCModuleState.process error?" + repr(e))
        finally:
            if shared_memory is not None:
                # 确保共享内存对象被正确关闭
                shared_memory.close()

    @classmethod
    def startBurn(cls, fwPath: str, comType: str):
        if FW_Manager.burn_state != FW_Manager.BS_FREE:
            cls.showInfo("当前不处于空闲状态,不能烧入!", FW_Manager.SI_TAG_ERROR)
            return
        FW_Manager.clearData()

        # 启动C模块进行升级
        execPath = os.getcwd() + "\\cmodule\\Burn_Tool.exe"
        cls.showInfo(f"C++模块目录:{execPath}", FW_Manager.SI_TAG_INFO)

        # 用子线程启动C模块(防止子界面被阻塞)
        # 警告: 这里只能使在主进程内创建子线程,启动c++模块,不能在QThread子线程启动c++模块
        # 否则使用subprocess.Popen无法正常启动c++模块
        Config_Data.generateShareMMName()
        binTypeValue = str(Local_Data_Util.getUpgradeTypeValue())
        mmShareName = Config_Data.mMMShareName
        cModuleThread = threading.Thread(target=cls.start_cmodule_proxy,
                                         args=([execPath, fwPath, comType, binTypeValue, mmShareName]))
        cModuleThread.start()
        Config_Data.mCModuleThread = cModuleThread

        # 因不好获取子线程模块实时打印的状态数据,所以需要开启提示等待
        Config_Data.mCModuleWaiting = True
        # cModuleStateThread = threading.Thread(target=cls.showCModuleWaiting)
        cModuleStateThread = threading.Thread(target=cls.showCModuleState)
        cModuleStateThread.start()
        Config_Data.mCModuleStateThread = cModuleStateThread

    @classmethod
    def analyzeBurnState(cls, bsState: int):
        if bsState == cls.C_BURN_STATE_INIT:
            FW_Manager.burn_state = FW_Manager.BS_REQUEST_SYNC
        elif bsState == cls.C_BURN_STATE_START:
            FW_Manager.burn_state = FW_Manager.BS_REQUEST_SYNC
        elif bsState == cls.C_BURN_STATE_REQ_BURN:
            FW_Manager.burn_state = FW_Manager.BS_REQUEST_SYNC
        elif bsState == cls.C_BURN_STATE_DATA_TRANSFER:
            FW_Manager.burn_state = FW_Manager.BS_DATA_TRANSFER
        elif bsState == cls.C_BURN_STATE_DATA_FINISH:
            FW_Manager.burn_state = FW_Manager.BS_DATA_TRANSFER_END
        elif bsState == cls.C_BURN_STATE_REQ_END:
            FW_Manager.burn_state = FW_Manager.BS_DATA_TRANSFER_END
        elif bsState == cls.C_BURN_STATE_END_SUCCESS:
            FW_Manager.burn_state = FW_Manager.BS_UPGRADE_SUCCESS
        elif bsState == cls.C_BURN_STATE_END_FAIL:
            FW_Manager.burn_state = FW_Manager.BS_UPGRADE_ERROR

        # 通知状态显示
        if (cls.qthread_obj is not None) and (cls.qthread_obj.call_fun_signal is not None):
            cls.qthread_obj.call_fun_signal.emit(FW_Manager.SI_TAG_CHSTATE, [bsState])

    @classmethod
    def handleProgress(cls, progress: int):
        FW_Manager.burn_progress = progress
        cls.showInfo(f"Upgrading:{progress}%", FW_Manager.SI_TAG_PROGRESS)

    @classmethod
    def handleMessage(cls, state: int, msg: str):
        if state == cls.C_MSG_INFO:
            cls.showInfo(msg, FW_Manager.SI_TAG_INFO)
        elif state == cls.C_MSG_ERROR:
            cls.showInfo(msg, FW_Manager.SI_TAG_ERROR)
        elif state == cls.C_MSG_EXCEPT:
            cls.showInfo(msg, FW_Manager.SI_TAG_EXCEPT)