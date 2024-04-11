import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QPushButton, QSpinBox, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,QLabel
from datetime import datetime
from threading import Timer
import ntplib
import pytz
import win32api

ISRUN = True

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        self.setWindowTitle("时间同步")

        # Create QListWidget and populate with strings
        self.list_widget = QComboBox()
        
        self.list_widget.addItems(["ntp.aliyun.com", "cn.ntp.org.cn", "ntp.ntsc.ac.cn", "ntp.sjtu.edu.cn", "ntp.tuna.tsinghua.edu.cn"])

        # Create QPushButton
        self.button = QPushButton("同步时间")
        self.button_auto = QPushButton("启动自动同步")

        self.interval_layout = QHBoxLayout()
        self.interval_label = QLabel("每隔多少秒同步一次时间")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(3600)
        self.interval_spinbox.setValue(180)
        self.interval_layout.addWidget(self.interval_label)
        self.interval_layout.addWidget(self.interval_spinbox)

        # Create QLineEdit
        self.line_edit = QLineEdit()
        self.label_last_sync = QLabel('上次同步时间为 00:00:00')

        self.label = QLabel("时间同步工具  by 梭哈是一种智慧")

        # Create QVBoxLayout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.button)
        layout.addWidget(self.line_edit)
        layout.addLayout(self.interval_layout)
        layout.addWidget(self.button_auto)
        layout.addWidget(self.label_last_sync)
        layout.addWidget(self.label)


        # Set layout for QWidget
        self.setLayout(layout)

        def get_time():
            try:
                ntp_client = ntplib.NTPClient()
                response = ntp_client.request(self.list_widget.currentText())
                return datetime.fromtimestamp(response.tx_time).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                QMessageBox.warning(self, "错误", "从服务器获取时间失败\n" + str(e))
                return ""

        def set_system_time():
            new_time = get_time()
            if new_time == "":
                QMessageBox.warning(self, "错误", "从服务器获取的时间为空")
                return

            datetime_object = datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')

            # 如果直接用服务器返回值修改时间, 会因为时区问题出现错误, 比如东八区时间比现实时间快8个小时
            # win32api.SetSystemTime(datetime_object.year, datetime_object.month, datetime_object.weekday(), datetime_object.day, datetime_object.hour, datetime_object.minute, datetime_object.second, 0)
            
            # Get the local time zone object
            local_tz = pytz.timezone('Asia/Shanghai')
            
            # Convert the local time to UTC time
            utc_time = local_tz.localize(datetime_object).astimezone(pytz.utc)
            
            # Set the system time using the UTC time
            win32api.SetSystemTime(utc_time.year, utc_time.month, utc_time.weekday(), utc_time.day, utc_time.hour, utc_time.minute, utc_time.second, 0)

            return new_time

        def start_auto_sync():
            new_time = set_system_time()

            global ISRUN
            if ISRUN == True:
                interval_seconds = self.interval_spinbox.value()
                Timer(interval_seconds, start_auto_sync).start()
            self.label_last_sync.setText("上次同步:  " + new_time)
            
        self.button.clicked.connect(lambda: self.line_edit.setText(get_time()))
        self.button.clicked.connect(set_system_time)
        self.button_auto.clicked.connect(start_auto_sync)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()

    appExit = app.exec_()
    ISRUN = False
    sys.exit( appExit)

# 生成可执行文件 pyinstaller --onefile C:\Users\Yolo\cursor-tutor\main.py
