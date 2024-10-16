import random


class Config_Data:
    #Cur Vesion
    TOOL_VERSION = "4.5"

    # 共享内存数据块名字(警告:此数据不要清除)
    mMMShareName = ""

    # 是否使用C模块进行升级
    USE_C_MODULE_PROCESS = True

    MAIN_ICON = None

    # 用户名
    ADMIN_NAME = "1"

    # 密码
    ADMIN_PSW = "1"

    # 选择固件文件时,需要用户登陆才能设置
    mAuthorized = False

    # 串口类型
    mComNum : str = None

    # 固件文件路径
    mFwPath : str = None

    # 观查者对象
    mObserver = None

    # 是否是烧入状态
    mBurning = False

    # C模块相关状态数据
    mCModuleThread = None
    mCModuleStateThread = None
    mCModuleWaiting = False

    @classmethod
    def clear(cls):
        cls.mComNum = ""
        cls.mFwPath = ""
        cls.mObserver = None
        cls.mBurning = False

        cls.mCModuleThread = None
        cls.mCModuleStateThread = None
        cls.mCModuleWaiting = False

    @classmethod
    def generateShareMMName(cls):
        """
        生成共享内存数据块名字(为同时多个串口升级做适配)
        :return:
        """
        cls.mMMShareName = "MY_SHARE_%04d" % (random.randint(1, 1000))