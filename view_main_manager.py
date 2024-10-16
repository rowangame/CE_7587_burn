import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPalette, QFont, QStandardItemModel, QStandardItem, QBrush, QColor, QIcon
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QAction, QActionGroup, QLabel

from burn_process_thread import MyProcessThread
from center_delegate import CenterDelegate
from cmodule_proxy import CModule_Proxy
from config_data import Config_Data
from device_csv_util import Device_Csv_Util
from device_info_util import Dev_Info_Util
from fw_manager import FW_Manager
from local_data_util import Local_Data_Util
from qadmin_dialog import QAdmin_Dialog
from qbinfile_dialog import QBinFile_Dialog
from qcom_dialog import ComSelectDialog
from qhelp_dialog import QMyHelpDialog
from view_main import Ui_main_view


class View_Main_Manager(object):
    # ui界面对象
    mView = Ui_main_view()
    mMainWindow: QMainWindow = None

    mTitles = ["序号", "当前串口", "烧入类型", "开始时间", "结束时间", "当前进度", "状态"]
    mCellValues = ["0", "None", "None", "None", "None", "None", "None"]
    mSeqId = 0
    mCurComId = 1
    mCurFileId = 2
    mStartTimeId = 3
    mEndTimeId = 4
    mProgressId = 5
    mBurnStateId = 6

    # 工具按钮对象
    m_icons_key = ["start", "stop", "quit", "file", "admin"]
    mToolBarDict = {}

    # 查询设备信息的上次时间
    mQueryDevInfoLastTick = 0

    @classmethod
    def solveUiProcess(cls, fname, params):
        try:
            if fname == FW_Manager.SI_TAG_INFO:
                sText = cls.getInfoStyle(params[0])
                cls.addTextHint(sText)
            elif fname == FW_Manager.SI_TAG_ERROR:
                sText = cls.getErrorStyle(params[0])
                cls.addTextHint(sText)
            elif fname == FW_Manager.SI_TAG_EXCEPT:
                sText = cls.getExceptStyle(params[0])
                cls.addTextHint(sText)
            elif fname == FW_Manager.SI_TAG_PROGRESS:
                cls.refresh_progress_value(FW_Manager.burn_progress)
                if (FW_Manager.burn_progress % 10) == 0:
                    sText = cls.getProgressStyle(params[0])
                    cls.addTextHint(sText)
            elif fname == FW_Manager.SI_TAG_SUCCESS:
                sText = cls.getSuccessStyle(params[0])
                cls.addTextHint(sText)
            elif fname == FW_Manager.SI_TAG_END:
                cls.burnEnd()
            elif fname == FW_Manager.SI_TAG_COPEN:
                CModule_Proxy.startBurn(Config_Data.mFwPath, Config_Data.mComNum)
            elif fname == FW_Manager.SI_TAG_CHSTATE:
                cls.update_burn_state_value(params[0])
            elif fname == FW_Manager.SI_TAG_CMODULE_WAIT:
                cls.update_cmodule_wait(params[0])
        except Exception as e:
            sText = cls.getExceptStyle("solveUiProcess.error?" + repr(e))
            cls.addTextHint(sText)

    @classmethod
    def burnEnd(cls):
        # 恢复菜单项(可点击)
        cls.enableMenuTypeButtons(True)

        wndMain = cls.getView()
        tmpTableView = wndMain.tblStateView

        # 将升级结果写入到csv文件中
        upgradeSuccess = FW_Manager.burn_state == FW_Manager.BS_UPGRADE_SUCCESS
        try:
            tmpCsvFile = Device_Csv_Util.getFileNameByVersion(Dev_Info_Util.cur_dev_version)
            tmpMac = Dev_Info_Util.cur_dev_mac
            tmpVer = Dev_Info_Util.cur_dev_version
            # 赋值不同类型的升级状态
            if Dev_Info_Util.cur_dev_record is None:
                tmpBt = "None"
                tmpVoice = "None"
                tmpDemo = "None"
            else:
                tmpBt = Dev_Info_Util.cur_dev_record["BT"]
                tmpVoice = Dev_Info_Util.cur_dev_record["Voice"]
                tmpDemo = Dev_Info_Util.cur_dev_record["Demo"]
            if Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
                if upgradeSuccess:
                    tmpBt = f"{Local_Data_Util.fwSharedData['btPath']}#{Device_Csv_Util.BURN_STATE_PASS}"
                else:
                    tmpBt = f"{Local_Data_Util.fwSharedData['btPath']}#{Device_Csv_Util.BURN_STATE_FAIL}"
            elif Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
                if upgradeSuccess:
                    tmpVoice = f"{Local_Data_Util.fwSharedData['voicePath']}#{Device_Csv_Util.BURN_STATE_PASS}"
                else:
                    tmpVoice = f"{Local_Data_Util.fwSharedData['voicePath']}#{Device_Csv_Util.BURN_STATE_FAIL}"
            else:
                if upgradeSuccess:
                    tmpDemo = f"{Local_Data_Util.fwSharedData['demoPath']}#{Device_Csv_Util.BURN_STATE_PASS}"
                else:
                    tmpDemo = f"{Local_Data_Util.fwSharedData['demoPath']}#{Device_Csv_Util.BURN_STATE_FAIL}"
            # 写入到csv文件中
            Device_Csv_Util.add_or_update_record(tmpCsvFile, tmpMac, tmpVer, tmpBt, tmpVoice, tmpDemo)
        except Exception as e:
            print("burnEnd: save csv file error?" + repr(e))

        # 更新状态显示
        if FW_Manager.burn_state == FW_Manager.BS_UPGRADE_SUCCESS:
            tmpIndex = tmpTableView.model().index(1, cls.mBurnStateId)
            tmpTableView.model().setData(tmpIndex, "烧入成功...")
            tmpItem = tmpTableView.model().item(1, cls.mBurnStateId)
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            tmpItem.setBackground(QBrush(QColor(0, 255, 0)))
        else:
            tmpIndex = tmpTableView.model().index(1, cls.mBurnStateId)
            tmpTableView.model().setData(tmpIndex, "烧入失败...")
            tmpItem = tmpTableView.model().item(1, cls.mBurnStateId)
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            tmpItem.setBackground(QBrush(QColor(255, 0, 0)))

        # 更新结束时间
        sTimeInfo = time.strftime("%H:%M:%S", time.localtime())
        tmpIndex = tmpTableView.model().index(1, cls.mEndTimeId)
        tmpTableView.model().setData(tmpIndex, sTimeInfo)

        sText = cls.getInfoStyle("烧入结束!")
        cls.addTextHint(sText)

        # 可重新开始烧入
        cls.mToolBarDict["start"].setEnabled(True)

        # 执行烧入结束逻辑
        FW_Manager.endBurnProcess()

        # 更新状态
        Config_Data.mBurning = False

    @classmethod
    def update_burn_state_value(cls, bsState: int):
        try:
            print(f"bsState={bsState}")

            wndMain = cls.getView()
            tmpTableView = wndMain.tblStateView
            tmpIndex = tmpTableView.model().index(1, cls.mBurnStateId)

            if FW_Manager.burn_state == FW_Manager.BS_FREE:
                tmpTableView.model().setData(tmpIndex, "空闲...")
            elif FW_Manager.burn_state == FW_Manager.BS_REQUEST_SYNC:
                tmpTableView.model().setData(tmpIndex, "请求烧入...")
            elif FW_Manager.burn_state == FW_Manager.BS_DATA_TRANSFER:
                tmpTableView.model().setData(tmpIndex, "数据传输...")
            elif FW_Manager.burn_state == FW_Manager.BS_DATA_TRANSFER_END:
                tmpTableView.model().setData(tmpIndex, "传输结束...")
            elif FW_Manager.burn_state == FW_Manager.BS_UPGRADE_SUCCESS:
                tmpTableView.model().setData(tmpIndex, "烧入成功...")
            elif FW_Manager.burn_state == FW_Manager.BS_UPGRADE_ERROR:
                tmpTableView.model().setData(tmpIndex, "烧入失败...")
        except Exception as e:
            print(repr(e))

    @classmethod
    def update_cmodule_wait(cls, secs):
        # print(f"secs={secs}")
        try:
            tmpTableView = cls.getView().tblStateView
            tmpIndex = tmpTableView.model().index(1, cls.mBurnStateId)
            tmpTableView.model().setData(tmpIndex, f"等待中({secs})s")
        except Exception as e:
            print(repr(e))

    @classmethod
    def refresh_burn_state_value(cls):
        try:
            wndMain = cls.getView()
            tmpTableView = wndMain.tblStateView

            # 串口编号显示
            tmpIndex = tmpTableView.model().index(1, cls.mSeqId)
            sNumber = Config_Data.mComNum[3:]
            tmpTableView.model().setData(tmpIndex, sNumber)

            # 串口号
            tmpIndex = tmpTableView.model().index(1, cls.mCurComId)
            tmpTableView.model().setData(tmpIndex, Config_Data.mComNum)

            # 烧入类型
            tmpIndex = tmpTableView.model().index(1, cls.mCurFileId)
            if Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
                curBurnType = "BT"
            elif Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
                curBurnType = "Voice"
            else:
                curBurnType = "Demo"
            tmpTableView.model().setData(tmpIndex, curBurnType)

            # 开始时间
            sTimeInfo = time.strftime("%H:%M:%S", time.localtime())
            tmpIndex = tmpTableView.model().index(1, cls.mStartTimeId)
            tmpTableView.model().setData(tmpIndex, sTimeInfo)

            # 结束时间
            tmpIndex = tmpTableView.model().index(1, cls.mEndTimeId)
            tmpTableView.model().setData(tmpIndex, "None")

            # 当前进度
            tmpIndex = tmpTableView.model().index(1, cls.mProgressId)
            tmpTableView.model().setData(tmpIndex, "0%")
            # 设置背景颜色(当前进度)
            tmpItem = tmpTableView.model().item(1, cls.mProgressId)
            # 设置显示颜色
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            # 设置字体加粗和颜色
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            # 设置背景颜色
            tmpItem.setBackground(QBrush(QColor(255, 255, 0)))

            # 当前状态
            tmpIndex = tmpTableView.model().index(1, cls.mBurnStateId)
            tmpTableView.model().setData(tmpIndex, "开始...")
            tmpItem = tmpTableView.model().item(1, cls.mBurnStateId)
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            tmpItem.setBackground(QBrush(QColor(255, 255, 0)))
        except Exception as e:
            print(repr(e))

    @classmethod
    def refresh_progress_value(cls, progress):
        try:
            wndMain = cls.getView()
            tmpTableView = wndMain.tblStateView

            # 当前进度
            tmpIndex = tmpTableView.model().index(1, cls.mProgressId)
            tmpTableView.model().setData(tmpIndex, "%d%%" % progress)
        except Exception as e:
            print(repr(e))

    @classmethod
    def on_burn_start(cls):
        wndMain = cls.getView()
        # 分析串口类型
        if len(Config_Data.mComNum) == 0:
            cls.showWarningInfo("请选择串口类型!")
            return

        if len(Config_Data.mFwPath) == 0:
            cls.showWarningInfo("请选择要烧入的文件!")
            return

        Dev_Info_Util.clearCurDevInfo()
        # 先获得设备信息(如果获取设备信息失败,则不能烧入)
        boState, lstValue, strMsg = Dev_Info_Util.getDevInfo(Config_Data.mComNum)
        if not boState:
            cls.showWarningInfo(strMsg)
            return
        Dev_Info_Util.cur_dev_version = lstValue[0]
        Dev_Info_Util.cur_dev_mac = lstValue[1]
        csvFileName = Device_Csv_Util.getFileNameByVersion(Dev_Info_Util.cur_dev_version)
        devRecord = Device_Csv_Util.find_record_by_mac(csvFileName, Dev_Info_Util.cur_dev_mac)
        Dev_Info_Util.cur_dev_record = devRecord

        # 清空内容
        wndMain.edtMsg.setText("")
        # 防止重复点击
        cls.mToolBarDict["start"].setEnabled(False)
        # 进度清零
        wndMain.edtMsg.setText("")

        # 显示设备信息
        cls.showDevStateInfo(Dev_Info_Util.cur_dev_version, Dev_Info_Util.cur_dev_mac, Dev_Info_Util.cur_dev_record)

        # 更新烧入状态显示
        cls.refresh_burn_state_value()

        print("开启烧入线程...")
        Config_Data.mObserver = cls
        Config_Data.mTestThread = MyProcessThread()
        Config_Data.mTestThread.call_fun_signal.connect(cls.solveUiProcess)
        Config_Data.mTestThread.start()

        # 禁用菜单项(防止误操作)
        cls.enableMenuTypeButtons(False)

    @classmethod
    def on_action_quit(cls):
        cls.mMainWindow.close()

    @classmethod
    def on_action_com_list(cls):
        # 创建并显示对话框
        dialog = ComSelectDialog()
        dialog.exec_()
        cls.showStatusInfo()

    @classmethod
    def on_binfile_result_event(cls):
        cls.showStatusInfo()

    @classmethod
    def do_open_binfile_dialog_event(cls):
        dialog = QBinFile_Dialog()
        dialog.setParentWindow(cls.mMainWindow)
        dialog.setCallBack(cls.on_binfile_result_event)
        dialog.exec_()

    @classmethod
    def on_action_fwfile_select(cls):
        # 每次选择bin文件都要授权验证(防止误操作)
        dialog = QAdmin_Dialog()
        dialog.setCallBack(cls.do_open_binfile_dialog_event)
        dialog.exec_()

    @classmethod
    def on_action_help_select(cls):
        dialog = QMyHelpDialog()
        dialog.exec_()

    @classmethod
    def on_action_version(cls):
        strVersion = f"1.当前版本:{Config_Data.TOOL_VERSION} \n 2.建议请联系:\n xielunguo@cosonic.net"
        cls.showInformationInfo(strVersion)

    @classmethod
    def on_action_query_dev_info(cls):
        # 分析串口类型
        if len(Config_Data.mComNum) == 0:
            cls.showWarningInfo("请选择一个串口类型!")
            return

        MIN_QUERY_WAIT_TIME = 6000
        curTick = int(time.time() * 1000)
        deltaTick = curTick - cls.mQueryDevInfoLastTick
        if deltaTick < MIN_QUERY_WAIT_TIME:
            cls.showWarningInfo("查询速度太快,请等待几秒钟!")
            return
        cls.mQueryDevInfoLastTick = curTick

        Dev_Info_Util.clearCurDevInfo()
        # 先获得设备信息(如果获取设备信息失败,则不能显示设备信息结果)
        boState, lstValue, strMsg = Dev_Info_Util.getDevInfo(Config_Data.mComNum)
        if not boState:
            cls.showWarningInfo(strMsg)
            return
        Dev_Info_Util.cur_dev_version = lstValue[0]
        Dev_Info_Util.cur_dev_mac = lstValue[1]
        csvFileName = Device_Csv_Util.getFileNameByVersion(Dev_Info_Util.cur_dev_version)
        devRecord = Device_Csv_Util.find_record_by_mac(csvFileName, Dev_Info_Util.cur_dev_mac)
        Dev_Info_Util.cur_dev_record = devRecord

        # 显示设备信息
        cls.showDevStateInfo(Dev_Info_Util.cur_dev_version,
                             Dev_Info_Util.cur_dev_mac,
                             Dev_Info_Util.cur_dev_record, True)

    @classmethod
    def showWarningInfo(cls, info):
        wndMain = cls.mView
        wndMain.mWarning = QMessageBox(QMessageBox.Warning, '警告', info)
        wndMain.mWarning.setWindowIcon(Config_Data.MAIN_ICON)
        wndMain.mWarning.show()

    @classmethod
    def showInformationInfo(cls, info):
        wndMain = cls.mView
        wndMain.mWarning = QMessageBox(QMessageBox.Information, '提示', info)
        wndMain.mWarning.setWindowIcon(Config_Data.MAIN_ICON)
        wndMain.mWarning.show()

    @classmethod
    def onActionMnuCModule(cls):
        # print("onActionMnuCModule...")
        Config_Data.USE_C_MODULE_PROCESS = True

        if Local_Data_Util.fwSharedData["moduleType"] != Local_Data_Util.MODULE_TYPE_C:
            Local_Data_Util.fwSharedData["moduleType"] = Local_Data_Util.MODULE_TYPE_C
            Local_Data_Util.saveData()

    @classmethod
    def onActionPyModule(cls):
        # print("onActionPyModule...")
        Config_Data.USE_C_MODULE_PROCESS = False

        if Local_Data_Util.fwSharedData["moduleType"] != Local_Data_Util.MODULE_TYPE_PY:
            Local_Data_Util.fwSharedData["moduleType"] = Local_Data_Util.MODULE_TYPE_PY
            Local_Data_Util.saveData()

    @classmethod
    def onBinTypeBt(cls):
        if Local_Data_Util.fwSharedData["sltType"] != Local_Data_Util.FW_TYPE_BT:
            Local_Data_Util.fwSharedData["sltType"] = Local_Data_Util.FW_TYPE_BT
            Local_Data_Util.saveData()
        Config_Data.mFwPath = Local_Data_Util.fwSharedData["btPath"]
        cls.showStatusInfo()

    @classmethod
    def onBinTypeVoice(cls):
        if Local_Data_Util.fwSharedData["sltType"] != Local_Data_Util.FW_TYPE_VOICE:
            Local_Data_Util.fwSharedData["sltType"] = Local_Data_Util.FW_TYPE_VOICE
            Local_Data_Util.saveData()
        Config_Data.mFwPath = Local_Data_Util.fwSharedData["voicePath"]
        cls.showStatusInfo()

    @classmethod
    def onBinTypeDemo(cls):
        if Local_Data_Util.fwSharedData["sltType"] != Local_Data_Util.FW_TYPE_DEMO:
            Local_Data_Util.fwSharedData["sltType"] = Local_Data_Util.FW_TYPE_DEMO
            Local_Data_Util.saveData()
        Config_Data.mFwPath = Local_Data_Util.fwSharedData["demoPath"]
        cls.showStatusInfo()

    @classmethod
    def setCtxWidgets(cls):
        # 添加按键事件
        wndMain = cls.getView()
        # 设置垂直布局
        qvlayout = QtWidgets.QVBoxLayout(wndMain.centralwidget)

        wndMain.edtMsg = QtWidgets.QTextEdit()
        wndMain.edtMsg.setGeometry(QtCore.QRect(11, 260, 1001, 411))
        wndMain.edtMsg.setObjectName("edtMsg")

        wndMain.tblStateView = QtWidgets.QTableView()
        wndMain.tblStateView.setGeometry(QtCore.QRect(10, 22, 1001, 231))
        wndMain.tblStateView.setObjectName("tblStateView")

        qvlayout.addWidget(wndMain.tblStateView)
        qvlayout.addWidget(wndMain.edtMsg)
        # 设置布局伸缩性
        qvlayout.setStretch(0, 2)  # QTableView 占用空间
        qvlayout.setStretch(1, 3)  # QTextEdit 也占用空间

    @classmethod
    def addBurnTypeSubMenu(cls):
        # 添加按键事件
        wndMain = cls.getView()

        # 创建一个QActionGroup对象
        group = QActionGroup(cls.mMainWindow)
        # 设置为True，确保只能选择一个
        group.setExclusive(True)

        # 创建两个QAction对象，它们属于同一个QActionGroup
        mnuCModel = QAction("C模块协议", cls.mMainWindow, checkable=True)
        # 将QAction对象添加到QActionGroup
        group.addAction(mnuCModel)
        # 将QAction对象添加到菜单
        wndMain.mnuType.addAction(mnuCModel)

        # 添加分隔符
        wndMain.mnuType.addSeparator()

        mnuPyModel = QAction("Python协议", cls.mMainWindow, checkable=True)
        group.addAction(mnuPyModel)
        wndMain.mnuType.addAction(mnuPyModel)

        # 添加事件
        mnuCModel.triggered.connect(cls.onActionMnuCModule)
        mnuPyModel.triggered.connect(cls.onActionPyModule)

        # 设置默认选项
        if Local_Data_Util.fwSharedData["moduleType"] == Local_Data_Util.MODULE_TYPE_C:
            Config_Data.USE_C_MODULE_PROCESS = True
            mnuCModel.setChecked(True)
        else:
            Config_Data.USE_C_MODULE_PROCESS = False
            mnuPyModel.setChecked(True)

    @classmethod
    def addStatusLabel(cls):
        tmpView = cls.getView()
        tmpView.lblStatus = QLabel("")
        tmpView.lblStatus.setStyleSheet("color:blue")
        tmpView.statusbar.addWidget(tmpView.lblStatus)

    @classmethod
    def addBinTypeSubMenu(cls):
        # 添加按键事件
        wndMain = cls.getView()

        # 创建一个QActionGroup对象
        group = QActionGroup(cls.mMainWindow)
        # 设置为True，确保只能选择一个
        group.setExclusive(True)

        # 创建三个QAction对象，它们属于同一个QActionGroup
        mnuBinBT = QAction("BT类型", cls.mMainWindow, checkable=True)
        # 将QAction对象添加到QActionGroup
        group.addAction(mnuBinBT)
        # 将QAction对象添加到菜单
        wndMain.mnuBinType.addAction(mnuBinBT)
        # 添加分隔符
        wndMain.mnuBinType.addSeparator()

        mnuBinVoice = QAction("Voice类型", cls.mMainWindow, checkable=True)
        group.addAction(mnuBinVoice)
        wndMain.mnuBinType.addAction(mnuBinVoice)
        # 添加分隔符
        wndMain.mnuBinType.addSeparator()

        mnuBinDemo = QAction("Demo类型", cls.mMainWindow, checkable=True)
        group.addAction(mnuBinDemo)
        wndMain.mnuBinType.addAction(mnuBinDemo)

        # 添加事件
        mnuBinBT.triggered.connect(cls.onBinTypeBt)
        mnuBinVoice.triggered.connect(cls.onBinTypeVoice)
        mnuBinDemo.triggered.connect(cls.onBinTypeDemo)

        # 设置默认选项
        if Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
            mnuBinBT.setChecked(True)
            Config_Data.mFwPath = Local_Data_Util.fwSharedData["btPath"]
        elif Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
            mnuBinVoice.setChecked(True)
            Config_Data.mFwPath = Local_Data_Util.fwSharedData["voicePath"]
        else:
            mnuBinDemo.setChecked(True)
            Config_Data.mFwPath = Local_Data_Util.fwSharedData["demoPath"]

    # 初始化按钮事件
    @classmethod
    def initEvents(cls):
        # 清除配置文件数据
        Config_Data.clear()

        # 加载共享数据对象
        Local_Data_Util.loadData()

        cls.setCtxWidgets()
        cls.addBurnTypeSubMenu()
        cls.addBinTypeSubMenu()
        cls.addStatusLabel()

        # 添加按键事件
        wndMain = cls.getView()

        wndMain.actionQuit.triggered.connect(cls.on_action_quit)
        wndMain.actionList.triggered.connect(cls.on_action_com_list)
        wndMain.actionBinFile.triggered.connect(cls.on_action_fwfile_select)
        wndMain.actionHelp.triggered.connect(cls.on_action_help_select)
        wndMain.actionVersion.triggered.connect(cls.on_action_version)
        wndMain.actionQueryDevInfo.triggered.connect(cls.on_action_query_dev_info)

        wndMain.edtMsg.setText("")

        # pgb = wndMain.progressBar
        # pgb.setMinimum(0)
        # pgb.setMaximum(100)
        # pgb.setValue(0)
        # styleSheet = "QProgressBar { border: 1px solid grey; color: rgb(20,20,20); background-color: #CCCCCC; " \
        #              "text-align: center;}QProgressBar::chunk {background-color: rgb(100,200,200); margin: 0.1px;  " \
        #              "width: 1px;} "
        # pgb.setStyleSheet(styleSheet)
        # pgb.setFormat('%p%'.format(pgb.value() - pgb.minimum()))

        max_row = 5
        max_col = len(cls.mTitles)
        cls.model = QStandardItemModel(max_row, max_col)
        for tmpCol in range(0, max_col):
            cls.model.setItem(0, tmpCol, QStandardItem(cls.mTitles[tmpCol]))
        for tmpCol in range(0, max_col):
            cls.model.setItem(1, tmpCol, QStandardItem(cls.mCellValues[tmpCol]))

        wndMain.tblStateView.setModel(cls.model)
        # 标题高亮显示
        for i in range(max_col):
            # 设置标题加粗显示
            tmpItem = cls.model.item(0, i)
            # 设置字体颜色
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            # 设置字体加粗
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            # 设置背景颜色
            tmpItem.setBackground(QBrush(QColor(0, 200, 0)))

        # 设置自定义的委托(目的:单元格居中显示)
        delegate = CenterDelegate()
        wndMain.tblStateView.setItemDelegate(delegate)

        # 初始化工具栏按钮
        cls.initToolbar()
        # 显示本地加载的默认路径(bin文件)
        cls.showStatusInfo()

    @classmethod
    def on_tool_bar_event(cls):
        # print("on_tool_bar_event...")
        action = cls.mMainWindow.sender()
        sText = action.text()
        # print(f"{sText} button clicked")
        if sText == "start":
            cls.on_burn_start()
        elif sText == "stop":
            print("stop...")
        elif sText == "quit":
            cls.mMainWindow.close()
        elif sText == "file":
            cls.on_action_com_list()
        elif sText == "admin":
            # 每次选择bin文件都要验证(防止误操作)
            dialog = QAdmin_Dialog()
            dialog.setCallBack(cls.do_open_binfile_dialog_event)
            dialog.exec_()

    @classmethod
    def initToolbar(cls):
        wndMain = cls.getView()

        # 创建动作(图标按钮)
        for i in range(len(cls.m_icons_key)):
            tmpFile = "./resources/%s_0.png" % (cls.m_icons_key[i])
            tmp_action = QAction(QIcon(tmpFile), cls.m_icons_key[i], cls.mMainWindow)
            wndMain.toolBar.addAction(tmp_action)
            tmp_action.triggered.connect(cls.on_tool_bar_event)
            cls.mToolBarDict[cls.m_icons_key[i]] = tmp_action

        # 设置按钮之间的间距
        styleSheet = """QToolBar {spacing: 5px;}"""
        wndMain.toolBar.setStyleSheet(styleSheet)

        # 禁止工具栏的浮动功能
        wndMain.toolBar.setFloatable(False)
        wndMain.toolBar.setMovable(False)

        # # 显示按钮对象(key)
        # print(cls.mToolBarDict.keys())

    @classmethod
    def onWindowCloseEvent(cls, event):
        if Config_Data.mBurning:
            info = "固件烧入中，不能退出!"
            cls.showWarningInfo(info)
            event.ignore()
        else:
            event.accept()

    @classmethod
    def getView(cls):
        return View_Main_Manager.mView

    @classmethod
    def setMainWindow(cls, mainWnd: QMainWindow):
        cls.mMainWindow = mainWnd

    @classmethod
    def getInfoStyle(cls, sInfo):
        titleFormat = '<b><font color="#000000" size="4">{}</font></b>'
        return titleFormat.format(sInfo)

    @classmethod
    def getErrorStyle(cls, sInfo):
        titleFormat = '<b><font color="#FF0000" size="4">{}</font></b>'
        return titleFormat.format(sInfo)

    @classmethod
    def getProgressStyle(cls, sInfo):
        titleFormat = '<b><font color="#0000FF" size="4">{}</font></b>'
        return titleFormat.format(sInfo)

    @classmethod
    def getExceptStyle(cls, sInfo):
        titleFormat = '<b><font color="#FF0000" size="4">{}</font></b>'
        return titleFormat.format(sInfo)

    @classmethod
    def getSuccessStyle(cls, sInfo):
        titleFormat = '<b><font color="#00FF00" size="4">{}</font></b>'
        return titleFormat.format(sInfo)

    @classmethod
    def getDevInfoStyle(cls, sInfo: str, sColor: str):
        titleFormat = '<b><font color="%s" size="4">{}</font></b>' % sColor
        return titleFormat.format(sInfo)

    @classmethod
    def addTextHint(cls, sText):
        wndMain = cls.getView()
        wndMain.edtMsg.append(sText)

        # 滑动到最低端显示
        hVerticalBar = wndMain.edtMsg.verticalScrollBar()
        if hVerticalBar:
            curValue = hVerticalBar.value()
            # minValue = hVerticalBar.minimum()
            maxValue = hVerticalBar.maximum()
            # print(f"cValue={curValue} minValue={minValue}, maxValue={maxValue}")
            if curValue < maxValue:
                hVerticalBar.setValue(maxValue)

    @classmethod
    def addTextHintEx(cls, sText: str, dropDown: bool = False):
        wndMain = cls.getView()
        wndMain.edtMsg.append(sText)
        if dropDown:
            # 滑动到最低端显示
            hVerticalBar = wndMain.edtMsg.verticalScrollBar()
            if hVerticalBar:
                curValue = hVerticalBar.value()
                # minValue = hVerticalBar.minimum()
                maxValue = hVerticalBar.maximum()
                # print(f"cValue={curValue} minValue={minValue}, maxValue={maxValue}")
                if curValue < maxValue:
                    hVerticalBar.setValue(maxValue)

    @classmethod
    def showStatusInfo(cls):
        sComInfo = "  串口类型:None "
        sFileInfo = " 文件路径:None"
        if len(Config_Data.mComNum) > 0:
            sComInfo = f"  串口:{Config_Data.mComNum} "
        if len(Config_Data.mFwPath) > 0:
            sFileInfo = f" 文件路径:{Config_Data.mFwPath}"
        if Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
            sFileType = " 升级类型:BT"
        elif Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
            sFileType = " 升级类型:Voice"
        else:
            sFileType = " 升级类型:Demo"
        sInfo = sComInfo + sFileInfo + sFileType
        cls.getView().lblStatus.setText(sInfo)

    @classmethod
    def showDevStateInfo(cls, ver: str, mac: str, record: dict, isQuery: bool = False):
        try:
            SPAN_TAG = "----------------"
            lineStartTag = SPAN_TAG * 4
            lineDeviceInfoTitle = "设备信息:"
            lineVer = "版本号:" + ver
            lineMac = "Mac地址:" + mac

            ctSpan = 8
            csSpan = 8
            cfSpan = 64
            cFill = "-"
            lineCsvInfoTitle = f"{'类型'.center(ctSpan, cFill)}|{'状态'.center(csSpan, cFill)}|{'文件'.center(cfSpan, cFill)}"

            tmpType = "BT".center(ctSpan, cFill)
            tmpState = "None".center(csSpan, cFill)
            tmpFile = "None".center(cfSpan, cFill)
            lineStateBt = f"{tmpType}|{tmpState}|{tmpFile}"

            tmpType = "Voice".center(ctSpan, cFill)
            tmpState = "None".center(csSpan, cFill)
            tmpFile = "None".center(cfSpan, cFill)
            lineStateVoice = f"{tmpType}|{tmpState}|{tmpFile}"

            tmpType = "Demo".center(ctSpan, cFill)
            tmpState = "None".center(csSpan, cFill)
            tmpFile = "None".center(cfSpan, cFill)
            lineStateDemo = f"{tmpType}|{tmpState}|{tmpFile}"

            if record is not None:
                tmpLine = record["BT"]
                lstLine = tmpLine.split("#")
                # 只有带 binPath#Pass的值才会分析,带None状态的值不能处理,否则异常
                if len(lstLine) == 2:
                    tmpType = "BT".center(ctSpan, cFill)
                    tmpState = lstLine[1].center(csSpan, cFill)
                    tmpFile = lstLine[0].center(cfSpan, cFill)
                    lineStateBt = f"{tmpType}|{tmpState}|{tmpFile}"

                tmpLine = record["Voice"]
                lstLine = tmpLine.split("#")
                if len(lstLine) == 2:
                    tmpType = "Voice".center(ctSpan, cFill)
                    tmpState = lstLine[1].center(csSpan, cFill)
                    tmpFile = lstLine[0].center(cfSpan, cFill)
                    lineStateVoice = f"{tmpType}|{tmpState}|{tmpFile}"

                tmpLine = record["Demo"]
                lstLine = tmpLine.split("#")
                if len(lstLine) == 2:
                    tmpType = "Demo".center(ctSpan, cFill)
                    tmpState = lstLine[1].center(csSpan, cFill)
                    tmpFile = lstLine[0].center(cfSpan, cFill)
                    lineStateDemo = f"{tmpType}|{tmpState}|{tmpFile}"

            # 如果是查询结果状态显示,则不显示当前烧入的类型状态
            if not isQuery:
                # 更新当前要烧入的状态显示
                if Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_BT:
                    tmpType = "BT".center(ctSpan, cFill)
                    tmpState = "烧入中...".center(csSpan, cFill)
                    tmpFile = Local_Data_Util.fwSharedData["btPath"].center(cfSpan, cFill)
                    lineStateBt = f"{tmpType}|{tmpState}|{tmpFile}"
                elif Local_Data_Util.fwSharedData["sltType"] == Local_Data_Util.FW_TYPE_VOICE:
                    tmpType = "Voice".center(ctSpan, cFill)
                    tmpState = "烧入中...".center(csSpan, cFill)
                    tmpFile = Local_Data_Util.fwSharedData["voicePath"].center(cfSpan, cFill)
                    lineStateVoice = f"{tmpType}|{tmpState}|{tmpFile}"
                else:
                    tmpType = "Demo".center(ctSpan, cFill)
                    tmpState = "烧入中...".center(csSpan, cFill)
                    tmpFile = Local_Data_Util.fwSharedData["demoPath"].center(cfSpan, cFill)
                    lineStateDemo = f"{tmpType}|{tmpState}|{tmpFile}"

            lineEndTag = lineStartTag

            sTagColor = "#000000"
            sCtxColor = "#00AA00"

            cls.addTextHintEx(cls.getDevInfoStyle(lineStartTag,sTagColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineDeviceInfoTitle, sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineVer,sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineMac,sCtxColor))

            cls.addTextHintEx(cls.getDevInfoStyle(lineCsvInfoTitle, sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineStateBt,sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineStateVoice,sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineStateDemo,sCtxColor))
            cls.addTextHintEx(cls.getDevInfoStyle(lineEndTag, sTagColor), True)
        except Exception as e:
            print("showDevStateInfo.error?" + repr(e))

    @classmethod
    def enableMenuTypeButtons(cls, enabled: bool):
        wndMain = cls.getView()
        # 配置
        wndMain.mnuSerial.setEnabled(enabled)
        # 协议
        wndMain.mnuType.setEnabled(enabled)
        # 类型
        wndMain.mnuBinType.setEnabled(enabled)
        # 查询
        wndMain.menuQueryDev.setEnabled(enabled)