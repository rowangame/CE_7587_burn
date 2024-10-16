
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QWidget
from PyQt5.QtGui import QIcon
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建工具栏
        toolbar = QToolBar(self)

        # 创建QAction按钮
        play_action = QAction(QIcon("./out/start_0.png"), "Play", self)
        stop_action = QAction(QIcon("./out/stop_0.png"), "Stop", self)

        # 将QAction添加到工具栏
        toolbar.addAction(play_action)

        # 添加间距
        spacer = QWidget()
        spacer.setFixedWidth(10)
        toolbar.addWidget(spacer)

        # 将另一个QAction添加到工具栏
        toolbar.addAction(stop_action)

        # 固定工具栏的大小
        size_hint = toolbar.sizeHint()
        toolbar.setFixedSize(size_hint)

        # 禁止工具栏浮动和移动
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        # 添加工具栏到窗口
        self.addToolBar(toolbar)

        # 连接动作到槽函数
        play_action.triggered.connect(self.on_action_triggered)
        stop_action.triggered.connect(self.on_action_triggered)

        # 设置窗口大小
        self.setGeometry(100, 100, 600, 100)

    # 槽函数：处理 QAction 的 triggered 信号
    def on_action_triggered(self):
        action = self.sender()  # 获取触发信号的 QAction 对象
        if action:
            print(f"{action.text()} button clicked")  # 输出动作的文本

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())