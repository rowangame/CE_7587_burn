
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QHBoxLayout, QWidget
from PyQt5.QtGui import QIcon
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建工具栏
        toolbar = QToolBar(self)

        # 添加动作（图标按钮）
        toolbar.addAction(QAction(QIcon("./out/start_0.png"), "start_0", self))
        toolbar.addAction(QAction(QIcon("./out/stop_0.png"), "stop_0", self))
        toolbar.addAction(QAction(QIcon("./out/quit_0.png"), "quit_0", self))
        toolbar.addAction(QAction(QIcon("./out/file_0.png"), "file_0", self))
        toolbar.addAction(QAction(QIcon("./out/admin_0.png"), "admin_0", self))

        # 添加工具栏到窗口
        self.addToolBar(toolbar)

        # 设置窗口大小
        self.setGeometry(100, 100, 600, 100)

        styleSheet = """QToolBar {spacing: 5px;}"""
        toolbar.setStyleSheet(styleSheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())