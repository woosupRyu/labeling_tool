from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import sys
from PyQt5.QtGui import *
from PyQt5 import QtCore
import socket
import struct


class project_app(QWidget):
    def __init__(self, db):
        super().__init__()
        self.DB = db

    def augmentation(self):
        #그리드 리스트
        grid_frame = QFrame()
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        grid_frame.setFrameShape(QFrame.Box)
        grid_list_label = QLabel("그리드 리스트")
        self.grid_box = []
        grid_box_group = QGroupBox()
        grid_vbox = QVBoxLayout()
        grid_vbox.addWidget(grid_list_label)
        grid_table_list = self.DB.list_table("Grid")
        grid_list = []
        for i in grid_table_list:
            grid_list.append(str(i[1]) + "x" + str(i[2]))
        for i in grid_list:
            grid_btn = QRadioButton(i)
            grid_btn.clicked.connect(self.show_grid)
            self.grid_box.append(grid_btn)
            grid_vbox.addWidget(grid_btn)
        self.grid_box[0].toggle()
        grid_box_group.setLayout(grid_vbox)
        grid_frame.setLayout(grid_vbox)
        self.grid_scroll.setWidget(grid_frame)

        #오브젝트 리스트
        object_frame = QFrame()
        self.object_scroll = QScrollArea()
        self.object_scroll.setWidgetResizable(True)
        object_frame.setFrameShape(QFrame.Box)
        object_list_label = QLabel("오브젝트 리스트")
        self.object_box = []



        self.object_vbox = QVBoxLayout()
        self.object_vbox.addWidget(object_list_label)
        self.a = []
        category_table_list = self.DB.list_table("Category")
        for i in category_table_list:
            self.DB.get_table(str(i[0]), "SuperCategory")[1]
        for i in ["a", "b", "c", "d", "e", "f"]:
            self.a.append(QCheckBox(i))
            self.object_vbox.addWidget(self.a[ad])
            ad = ad + 1

        object_frame.setLayout(self.object_vbox)
        self.object_scroll.setWidget(object_frame)

        self.grid_setting_frame = QFrame()
        self.grid_setting = QScrollArea()
        self.grid_setting.setWidgetResizable(True)
        self.grid_setting_frame.setFrameShape(QFrame.Box)
        self.grid_setting_label = QLabel("물품 별 \n그리드 설정")
        self.grid_setting_btn = []
        self.grid_setting_layout = QGridLayout()
        self.grid_setting_layout.addWidget(self.grid_setting_label, 0, 1)
        for i in range(len(self.grid_box)):
            if self.grid_box[i].isChecked():
                grid_x = self.grid_box[i].text().split("x")[0]
                grid_y = self.grid_box[i].text().split("x")[1]
        for i in range(1, int(grid_x) + 1):
            for j in range(1, int(grid_y) + 1):
                grid_setting_btn = QPushButton(str(i) + "x" + str(j))
                grid_setting_btn.setCheckable(True)
                self.grid_setting_btn.append(grid_setting_btn)
                self.grid_setting_layout.addWidget(grid_setting_btn, i, j)
        self.grid_setting_frame.setLayout(self.grid_setting_layout)

        #3가지 묶는 레이아웃
        self.h_box1 = QHBoxLayout()
        self.h_box1.addWidget(self.grid_scroll)
        self.h_box1.addWidget(self.object_scroll)
        self.h_box1.addWidget(self.grid_setting_frame)

        self.augmentation_filename = QLineEdit()
        self.augmentation_option_btn  = QPushButton("Augment 옵션")
        self.augmentation_option_btn.clicked.connect(self.augmentation_option)
        self.augmentation = QPushButton("합성하기")
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.augmentation_filename)
        self.h_box2.addWidget(self.augmentation_option_btn)

        self.v_box = QVBoxLayout()
        self.v_box.addLayout(self.h_box1)
        self.v_box.addLayout(self.h_box2)
        self.v_box.addWidget(self.augmentation)

        self.setLayout(self.v_box)
        self.project_name = self.sender()

        self.resize(800, 500)
        self.setWindowTitle(self.project_name.text())
        self.show()

    def augmentation_option(self):
        self.augmentation_option_window = QWidget()
        aug_option_label = QLabel("Augment 옵션")
        aug_num_label = QLabel("물품 당 augment 개수")
        aug_num_edit = QLineEdit()
        augment_method1 = QLabel("열 별 단일")
        method1_rate = QLineEdit()
        augment_method2 = QLabel("열 별 랜덤")
        method2_rate = QLineEdit()
        augment_method3 = QLabel("전체 랜덤")
        method3_rate = QLineEdit()
        Shadow_option = QCheckBox("그림자 옵션 추가")
        check_btn = QPushButton("확인")
        check_btn.clicked.connect(self.check)

        vbox = QGridLayout()
        vbox.addWidget(aug_option_label, 0, 0)
        vbox.addWidget(aug_num_label, 1, 0)
        vbox.addWidget(aug_num_edit, 1, 1)
        vbox.addWidget(augment_method1, 2, 0)
        vbox.addWidget(method1_rate, 2, 1)
        vbox.addWidget(augment_method2, 3, 0)
        vbox.addWidget(method2_rate, 3, 1)
        vbox.addWidget(augment_method3, 4, 0)
        vbox.addWidget(method3_rate, 4, 1)
        vbox.addWidget(Shadow_option, 5, 0)
        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(check_btn)
        self.augmentation_option_window.setLayout(hbox)
        self.augmentation_option_window.setWindowTitle("Augment 옵션")
        self.augmentation_option_window.show()

    def check(self):
        self.augmentation_option_window.close()

    def show_grid(self):
        self.grid_setting_btn = []
        for i in reversed(range(self.grid_setting_layout.count())):
            self.grid_setting_layout.itemAt(i).widget().deleteLater()

        self.grid_setting_label = QLabel("물품 별 \n그리드 설정")
        self.grid_setting_layout.addWidget(self.grid_setting_label, 0, 1)

        for i in range(len(self.grid_box)):
            if self.grid_box[i].isChecked():
                grid_x = self.grid_box[i].text().split("x")[0]
                grid_y = self.grid_box[i].text().split("x")[1]
        for i in range(1, int(grid_x) + 1):
            for j in range(1, int(grid_y) + 1):
                grid_setting_btn = QPushButton(str(i) + "x" + str(j))
                grid_setting_btn.setCheckable(True)
                self.grid_setting_btn.append(grid_setting_btn)
                self.grid_setting_layout.addWidget(grid_setting_btn, i, j)
        self.grid_setting_frame.setLayout(self.grid_setting_layout)

        self.update()

        self.show()

