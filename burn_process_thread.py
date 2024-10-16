# 因子线程会阻塞UI主线程,导致UI程序卡死,因止使用QThread线程来执行费时间的逻辑
# 此线程只能关联在Pyqt5内使用,否则不起用
from PyQt5.QtCore import QThread, pyqtSignal

from cmodule_proxy import CModule_Proxy
from config_data import Config_Data
from fw_manager import FW_Manager


class MyProcessThread(QThread):
    # 信号类型:str, list
    call_fun_signal = pyqtSignal(str, list)

    def __init__(self, parent=None):
        super(MyProcessThread, self).__init__(parent)

    def run(self):
        # 更新状态
        Config_Data.mBurning = True

        # 采用Python方案进行烧入操作
        if not Config_Data.USE_C_MODULE_PROCESS:
            try:
                FW_Manager.setQthreadObj(self)
                FW_Manager.startFwBurn(Config_Data.mFwPath, Config_Data.mComNum)
            except Exception as e:
                self.call_fun_signal.emit(FW_Manager.SI_TAG_EXCEPT, [repr(e)])
            finally:
                self.call_fun_signal.emit(FW_Manager.SI_TAG_END, [""])
        else:
            # C模块进行烧入操作
            CModule_Proxy.setQthreadObj(self)
            """
            警告：在使用QThread线程内使用subprocess.Popen函数,调用c模块会失败。可能是
            线程上下文差异:
                在 PyQt5 中，QThread 的运行环境与主线程有所不同。subprocess.Popen 可能依赖于一些仅在主线程中可用的资源或环境变量，
                例如 GUI 线程中的某些资源，可能会导致子进程在 QThread 中无法正确启动
            信号与槽机制:
                QThread 和主线程的交互可能存在竞态条件，尤其是涉及信号与槽的异步操作时。
                某些资源或对象可能在 QThread 中不可用，或者在你启动子进程之前还未初始化完成。
            线程安全问题:
                subprocess.Popen 本身是线程安全的，但如果你的 C++ 模块或其他依赖项不是线程安全的，在不同线程中调用它们可能会导致异常行为。
            资源锁定:
                如果你的 C++ 模块需要访问某些系统资源，如文件、设备或网络端口，这些资源可能会被主线程锁定，从而在子线程中无法访问
            环境变量和工作目录:
                当你在子线程中调用 subprocess.Popen 时，默认的工作目录和环境变量可能会有所不同。
                你可以在 subprocess.Popen 调用中显式指定 cwd（当前工作目录）和 env（环境变量）来确保一致性
            GIL（全局解释器锁）:
                Python 的全局解释器锁（GIL）可能在多线程环境中影响某些操作。
                虽然 GIL 不直接影响 C++ 模块的执行，但可能影响到 Python 与 C++ 之间的某些交互  
            """
            # CModule_Proxy.startBurn(Config_Data.mFwPath, Config_Data.mComNum)
            # 使用信号机㓡,在主线程内启动C模块
            self.call_fun_signal.emit(FW_Manager.SI_TAG_COPEN, [""])