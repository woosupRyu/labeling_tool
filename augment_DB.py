from PyQt5.QtWidgets import *
from io import BytesIO
from PIL import Image
import numpy as np
import augment_v3
from DCD_DB_API_master.db_api import DB

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

        grid_label_box = QVBoxLayout()
        grid_label_box.addWidget(grid_list_label)

        grid_box_group = QGroupBox()
        grid_vbox = QVBoxLayout()
        grid_vbox.addWidget(grid_list_label)
        grid_table_list = self.DB.list_table("Grid")
        grid_list = []
        for i in grid_table_list:
            if i[1] != 0 and not(i[1] == 1 and i[2] == 1):
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
        grid_label_box.addWidget(self.grid_scroll)

        #오브젝트 리스트
        object_frame = QFrame()
        self.object_scroll = QScrollArea()
        self.object_scroll.setWidgetResizable(True)
        object_frame.setFrameShape(QFrame.Box)
        object_list_label = QLabel("오브젝트 리스트")
        self.object_box = []

        label_box = QVBoxLayout()
        label_box.addWidget(object_list_label)

        self.object_vbox = QVBoxLayout()
        self.a = []
        category_table_list = self.DB.list_table("Category")
        for i in category_table_list:
            mix_or_not = self.DB.get_table(str(i[0]), "SuperCategory")[1]

            if DB.process_check(self.DB, str(i[1])):
                if mix_or_not != "mix" and mix_or_not != "background":
                    product_name = i[2] + "/" + mix_or_not
                    ad = QCheckBox(product_name)
                    self.a.append(ad)
                    self.object_vbox.addWidget(ad)
        object_frame.setLayout(self.object_vbox)
        self.object_scroll.setWidget(object_frame)
        label_box.addWidget(self.object_scroll)
        # 백그라운트 리스트

        background_frame = QFrame()
        self.background_scroll = QScrollArea()
        self.background_scroll.setWidgetResizable(True)
        background_frame.setFrameShape(QFrame.Box)
        background_list_label = QLabel("배경 리스트")
        self.background_box = []

        background_label_box = QVBoxLayout()
        background_label_box.addWidget(background_list_label)
        self.background_vbox = QVBoxLayout()
        self.background_vbox.addWidget(background_list_label)
        self.background = []
        category_table_list = self.DB.list_table("Category")
        for i in category_table_list:
            background_or_not = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if background_or_not == "background":
                ad = QRadioButton(i[2] + "/background")
                ad.clicked.connect(self.current_back)
                self.background.append(ad)
                self.background_vbox.addWidget(ad)
        self.background[0].click()

        background_frame.setLayout(self.background_vbox)
        self.background_scroll.setWidget(background_frame)
        background_label_box.addWidget(self.background_scroll)


        # 그리드 레이아웃 표시
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
                self.current_grid = (int(grid_x), int(grid_y))
        for i in range(1, int(grid_x) + 1):
            for j in range(1, int(grid_y) + 1):
                grid_setting_btn = QPushButton(str(i) + "x" + str(j))
                grid_setting_btn.setCheckable(True)
                self.grid_setting_btn.append(grid_setting_btn)
                self.grid_setting_layout.addWidget(grid_setting_btn, i, j)
        self.grid_setting_frame.setLayout(self.grid_setting_layout)

        #3가지 묶는 레이아웃
        self.h_box1 = QHBoxLayout()
        self.h_box1.addLayout(grid_label_box)
        self.h_box1.addLayout(label_box)
        self.h_box1.addLayout(background_label_box)
        self.h_box1.addWidget(self.grid_setting_frame)

        self.augmentation_filename = QLineEdit()
        self.augmentation_option_btn  = QPushButton("Augment 옵션")
        self.augmentation_option_btn.clicked.connect(self.augmentation_option)
        self.augmentation = QPushButton("합성하기")
        self.augmentation.clicked.connect(self.augment)
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.augmentation_filename)
        self.h_box2.addWidget(self.augmentation_option_btn)

        self.v_box = QVBoxLayout()
        self.v_box.addLayout(self.h_box1)
        self.v_box.addLayout(self.h_box2)
        self.v_box.addWidget(self.augmentation)

        self.setLayout(self.v_box)
        self.project_name = self.sender()

        self.resize(1000, 500)
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
                self.current_grid = (int(grid_x), int(grid_y))
        for i in range(1, int(grid_x) + 1):
            for j in range(1, int(grid_y) + 1):
                grid_setting_btn = QPushButton(str(i) + "x" + str(j))
                grid_setting_btn.setCheckable(True)
                self.grid_setting_btn.append(grid_setting_btn)
                self.grid_setting_layout.addWidget(grid_setting_btn, i, j)
        self.grid_setting_frame.setLayout(self.grid_setting_layout)

        self.update()

        self.show()
    def current_back(self):
        self.current_background = self.sender().text()

    def augment(self):
        grid = self.current_grid
        category_name = []
        category_id = []
        for i in self.a:
            if i.isChecked():
                category_name.append(i.text())

        for i in category_name:
            name = i.split("/")
            super_id = self.DB.get_supercategory_id_from_args(name[1])
            cate_id = self.DB.get_category_id_from_args(str(super_id), name[0])
            category_id.append(cate_id)

        batch_method = 3
        back_name = self.current_background.split("/")
        back_super_id = self.DB.get_supercategory_id_from_args(back_name[1])
        back_cate_id = self.DB.get_category_id_from_args(str(back_super_id), back_name[0])
        grid_id = self.DB.get_grid_id_from_args("1x1")
        loc_id = self.DB.get_location_id_from_args(str(grid_id), "1x1")
        object_id = self.DB.get_obj_id_from_args(loc_id, back_cate_id, "1", "-1")
        obj = self.DB.get_table(str(object_id), "Object")
        background = self.DB.get_table(str(obj[0]), "Image")[2]
        background_image = np.array(Image.open(BytesIO(background)).convert("RGB"))


        # 실제 사용함수

        aug1 = augment_v3.augment(grid, category_id, batch_method, background_image)
        aug1.compose_batch()
        aug1.load_DB()
        aug1.make_background()
        aug1.make_maskmap()
        aug1.augment_image()
        aug1.re_segmentation()
        result = aug1.save_DB()

        print("finish")


