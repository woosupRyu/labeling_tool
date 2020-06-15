import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import cv2
import numpy as np
import random
from io import BytesIO
from PIL import Image
import DB
# 그래픽스 클래스에서도 참조해야할 변수들 글로벌로 선언

global view  # 이미지 보여주는 공간
global scale_factor_w  # 이미지 확대, 축소 배율
global edit_btn  # 수정 버튼
global draggin_idx  # 드래그 작업 참조 변수

global minimum_mask  #
global mask_btn  # 마스킹 버튼
global qp  # QPainter
global scene  # 이미지 보여주는 공간
global im  # 마스크를 포함한 이미지
global pen  # 마스크 포인트 그리는 펜
global brush  # 마스크 채우는 붓
global mask_num  # 선택된 마스크의 순서

global label_color  # pen 색
global fill_color  # brush 색
global qim  # 마스크 없는 원 이미지
global line_pen  # 마스크 선 그리는 펜
global label_line_color  # line_pen 색
global label_name  # 라벨 이름
global current_label  # 선택된 마스크의 라벨
global color_value  # 색의 실제 값
global coordinates
global category_box
global left_vboxx
global current_object
global label_list
global category_id_list

class mix(QWidget):
    # 라벨들을 입력으로 받아서 라벨의 고유 색을 설정
    def __init__(self,  db):
        super().__init__()

        self.DB = db
        global scale_factor_w
        global draggin_idx
        global mask_num
        global fill_color
        global label_color
        global label_line_color
        global label_name
        global color_value
        global coordinates
        global label_list
        global qim

        scale_factor_w = 1  # 이미지 사이즈의 배율이므로 1로 초기화
        mask_num = 1000000  # 마스크 개수의 초기값
        draggin_idx = -1
        coordinates = []
        color_value = []
        label_color = []
        label_line_color = []
        fill_color = []
        label_list = []
        qim = []

    def mix_bboxing(self):

        global view
        global edit_btn
        global scene
        global im
        global mask_btn
        global qim
        global current_label
        global category_box
        global left_vboxx
        global line_pen
        global pen
        global brush
        global left_vboxx
        global current_object
        global coordinates
        global label_list

        progress = 0
        # 이미지를 보여줄 그래픽스 공간 생성
        scene = QGraphicsScene()
        view = tracking_screen(scene)
        view.setMouseTracking(True)

        # 편의 기능들 생성
        self.btn_group = QButtonGroup()
        self.label_group = QButtonGroup()

        edit_btn = QPushButton("수정")
        edit_btn.setCheckable(True)
        edit_btn.setShortcut("E")
        edit_btn.setToolTip("E")
        mask_btn = QPushButton("비박싱")
        mask_btn.setCheckable(True)
        mask_btn.setShortcut("B")
        mask_btn.setToolTip("B")
        mask_btn.toggle()
        original_size_btn = QPushButton("기본크기")
        original_size_btn.setShortcut("G")
        original_size_btn.setToolTip("G")
        original_size_btn.clicked.connect(self.set_original_size)
        save_btn = QPushButton("저장")
        save_btn.setShortcut("Ctrl+S")
        save_btn.setToolTip("Ctrl+S")
        save_btn.clicked.connect(self.save_info)
        next_btn = QPushButton(">")
        next_btn.clicked.connect(self.move_image)
        next_btn.setShortcut("D")
        next_btn.setToolTip("D")
        before_btn = QPushButton("<")
        before_btn.clicked.connect(self.move_image)
        before_btn.setShortcut("A")
        before_btn.setToolTip("A")
        #label_label = QLabel("선택 마스크의 라벨")
        current_label = QLineEdit()
        category_box = QComboBox()

        label_frame = QFrame()
        label_frame.setFrameShape(QFrame.Box)
        ver_box = QVBoxLayout()

        self.label_name_list = []
        category_name_list = self.category_list2name(self.DB.list_table("Category"))
        num = 0
        print(category_name_list)
        for i in category_name_list:
            label_box = QCheckBox(i)
            label_box.clicked.connect(self.addlabel)
            self.label_name_list.append(label_box)
            ver_box.addWidget(label_box)
            num = num + 1
        label_frame.setLayout(ver_box)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(label_frame)


        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if super_name == "mix":
                category_box.addItem(i[2] + "/" + super_name)

        self.a = []
        self.b = []
        count = 0

        cate_info = category_box.currentText().split("/")
        super_id = self.DB.get_supercategory_id_from_args(cate_info[1])
        self.current_category = str(self.DB.get_category_id_from_args(str(super_id), cate_info[0]))

        objects = []
        for i in self.DB.list_table("Grid"):
            # print("category : " + self.current_category)
            # print("grid : " + str(i[0]))
            obj = list(DB.list_object_check_num(self.DB, self.current_category, str(i[0]), "0"))
            if len(obj) != 0:
                objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)

        for i in btn_names:
            temp_btn = QPushButton(i)
            temp_btn.setCheckable(True)
            if count == 0:
                temp_btn.toggle()
                current_object = temp_btn.text()
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if len(self.DB.bbox_info(self.obj_name2id(i))) != 0:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1
        obj_id = self.obj_name2id(current_object)
        exist_bbox = DB.get_bbox_from_img_id(self.DB, str(self.DB.get_table(obj_id, "Object")[0]))
        category_name = category_box.currentText()
        if len(exist_bbox) == 0:
            RGB = random.sample(range(0, 255), 3)
            back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
            label_list = QRadioButton(category_name)
            label_list.clicked.connect(self.color_select)
            label_list.setStyleSheet(back_label_color)
            label_list.toggle()
            pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 6)
            line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 2)
            brush = QBrush(QColor(RGB[0], RGB[1], RGB[2]), Qt.Dense2Pattern)
            print("yo")
        else:
            print(exist_bbox)

        len_a = len(self.a)
        self.progress_state = QLabel("진행도 : " + str(progress) + "/" + str(len_a))

        left_frame = QFrame()

        left_vboxx = QVBoxLayout()
        left_vboxp = QVBoxLayout()
        #left_vboxp.addWidget(label_label)
        left_vboxp.addWidget(next_btn)
        left_vboxp.addWidget(before_btn)
        left_vboxp.addWidget(current_label)
        left_vboxp.addWidget(category_box)
        left_vboxp.addWidget(self.scroll_area)
        left_vboxp.addWidget(self.progress_state)
        left_vboxx.addLayout(left_vboxp)
        category_box.currentIndexChanged.connect(self.list_change)


        for i in range(len(self.a)):
            left_hbox = QHBoxLayout()
            self.a[i].clicked.connect(self.image_state)
            self.b[i].stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(self.b[i])
            left_vboxx.addLayout(left_hbox)

        left_frame.setLayout(left_vboxx)

        self.btn_group.addButton(edit_btn)
        self.btn_group.addButton(mask_btn)

        self.label_vbox = QVBoxLayout()
        self.label_box = QGroupBox()
        self.label_vbox.addWidget(label_list)
        self.label_box.setLayout(self.label_vbox)

        if len(objects) >= 1:
            img_obj_id = self.obj_name2id(current_object)

            imgd = self.DB.get_table(self.DB.get_table(str(img_obj_id), "Object")[0], "Image")[2]
            self.img_data = np.array(Image.open(BytesIO(imgd)).convert("RGB"))

            qim = QImage(self.img_data, self.img_data.shape[1], self.img_data.shape[0], self.img_data.strides[0],
                         QImage.Format_RGB888)
            w = qim.width()
            h = qim.height()
            im = QPixmap.fromImage(qim)

            qp = QPainter()
            im.setDevicePixelRatio(scale_factor_w)
            qp.begin(im)

            if len(sum(self.DB.bbox_info(img_obj_id), ())) != 0:
                coordinates = self.bbox2coordinate(self.DB.get_table(str(self.DB.get_bbox_id_from_args(img_obj_id)), "Bbox"))
                qp.setPen(line_pen)
                qp.setBrush(QBrush(Qt.transparent))
                qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))

            qp.end()
            scene.clear()
            scene.addPixmap(im)
            view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
            scene.update()

        vbox = QVBoxLayout()
        vbox.addWidget(edit_btn)
        vbox.addWidget(mask_btn)
        vbox.addWidget(original_size_btn)
        vbox.addWidget(save_btn)
        vbox.addWidget(self.label_box)
        right_frame = QFrame()
        right_frame.setLayout(vbox)

        hbox = QHBoxLayout()
        left_splitter = QSplitter(Qt.Horizontal)
        left_splitter.addWidget(left_frame)
        left_splitter.addWidget(view)
        left_splitter.addWidget(right_frame)
        left_splitter.setStretchFactor(1, 5)
        hbox.addWidget(left_splitter)

        self.resize(1300, 1000)
        self.setWindowTitle("비박싱")
        self.setLayout(hbox)
        self.show()

    def color_select(self):
        k = 0
        global pen
        global brush
        global line_pen
        global color_value
        global label_list

        # print(self.sender().text())
        # print(label_list[0].style())
        # print(label_list[0].style())

        for i in label_list:
            if i.isChecked():
                pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 6)
                line_pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 2)
                brush = QBrush(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), Qt.Dense2Pattern)
            k = k + 1


    def set_original_size(self):
        # 이미지를 원래 크기로 되돌리는 버튼과 연결된 함수
        global scale_factor_w
        global qp
        global mask_num
        global scene
        global im
        global fill_color
        global label_color
        global coordinates

        scale_factor_w = 1
        qp = QPainter()
        im.setDevicePixelRatio(scale_factor_w)
        qp.begin(im)
        iter_num = 0
        for i in coordinates:
            qp.setPen(label_line_color[iter_num])
            if mask_num == iter_num:
                qp.setBrush(fill_color[iter_num])
            else:
                qp.setBrush(QBrush(Qt.transparent))
            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
            iter_num = iter_num + 1


        w = im.width()
        h = im.height()
        qp.end()
        scene.clear()
        scene.addPixmap(im)
        view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        scene.update()


    def save_state(self):
        # 현재 진행도(체크박스의 체크 개수)를 보여주는 함수
        a = 0
        b = len(self.b)
        for i in range(b):
            if self.b[i].isChecked():
                a = a + 1
        self.progress_state.setText("진행도 : " + str(a) + "/" + str(b))

    def image_state(self):
        # 이미지이름을 누르면 해당 이미지가 보이도록 해주는 함수
        global scale_factor_w
        global draggin_idx
        global mask_num
        global fill_color
        global label_color
        global label_line_color
        global im
        global qim
        global coordinates
        global current_object
        global label_list

        scale_factor_w = 1
        mask_num = 1000000
        draggin_idx = -1


        label_color = []
        label_line_color = []
        fill_color = []
        coordinates = []
        current_object = self.sender().text()
        print("현재 오브젝트 이미지 이름 : " + current_object)
        img_obj_id = self.obj_name2id(current_object)

        imgd = self.DB.get_table(self.DB.get_table(str(img_obj_id), "Object")[0], "Image")[2]
        self.img_data = np.array(Image.open(BytesIO(imgd)).convert("RGB"))

        qim = QImage(self.img_data, self.img_data.shape[1], self.img_data.shape[0], self.img_data.strides[0],
                     QImage.Format_RGB888)
        w = qim.width()
        h = qim.height()
        im = QPixmap.fromImage(qim)

        qp = QPainter()
        im.setDevicePixelRatio(scale_factor_w)
        qp.begin(im)

        if len(sum(self.DB.bbox_info(img_obj_id), ())) != 0:

            coordinates = self.bbox2coordinate(self.DB.get_table(str(self.DB.get_bbox_id_from_args(img_obj_id)), "Bbox"))
            qp.setPen(line_pen)
            qp.setBrush(QBrush(Qt.transparent))
            qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
        qp.end()
        scene.clear()
        scene.addPixmap(im)
        view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        scene.update()

    def save_info(self):
        # 저장버튼과 연결된 함수, 마스크값을 저장하고, 해당 이미지에 작업이 완료됬다는 체크표시를 해줌
        global current_object
        global coordinates
        global label_line_color
        global label_color
        global fill_color
        global category_id_list

        #라벨색이름에 해당하는 색 추가
        #label_list[0].palette().color(10).rgb()

        img_obj_id = self.obj_name2id(current_object)
        img_id = str(self.DB.get_table(img_obj_id, "Object")[0])
        loc_id = str(self.DB.get_location_id_from_args(str(self.DB.get_grid_id_from_args("0x0")), '0x0'))
        category_id_list = sorted(category_id_list)
        iteration = current_object.split("_")[2]

        self.DB.delete_object_from_image(img_id)

        if len(coordinates) != 0:
            label_count = np.zeros((len(category_id_list)))
            for i in range(len(category_id_list)):
                for j in coordinates:
                    if j[4] == j[category_id_list[i]]:
                        self.DB.set_object(img_id, loc_id, str(j[4]), iteration, str(label_count[i]))
                        box_info = self.coordinate2bbox(j)
                        self.DB.set_bbox(str(str(self.DB.last_id_table("Object"))[2:-3]), box_info[0], box_info[1], box_info[2], box_info[3])
                        label_count[i] = label_count[i] + 1
            for i in range(len(self.a)):
                if self.a[i].isChecked():
                    self.b[i].setCheckState(Qt.Checked)

        # print(coordinates)
        # for i in range(len(label_line_color)):
        #     print(label_line_color[i].color().rgb())
        # obj_id = self.obj_name2id(current_object)
        # img_id = self.DB.get_table(obj_id, "Object")[0]
        # self.delete_bbox_from_image(self.DB, img_id)
        #
        # if len(coordinates) != 0:
        #     for i in range(len(coordinates)):
        #         box_info = self.coordinate2bbox(coordinates[i])
        #     self.DB.set_object(coordinates[i][4])
        # if len(coordinates) != 0:
        #     for i in range(len(coordinates)):
        #         box_info = self.coordinate2bbox(coordinates[i])
        #
        #
        #         self.DB.set_bbox(obj_id, box_info[0], box_info[1], box_info[2], box_info[3])
        #
        #     for i in range(len(self.a)):
        #         if self.a[i].isChecked():
        #             self.b[i].setCheckState(Qt.Checked)

    def move_image(self):
        len_a = len(self.a)
        sender = self.sender().text()
        if sender == "<":
            for i in range(len_a):
                if self.a[i].isChecked():
                    if i > 0:
                        self.a[i - 1].click()
                        break
        elif sender == ">":
            for i in range(len_a):
                if self.a[i].isChecked():
                    if i < (len_a - 1):
                        self.a[i + 1].click()
                        break

    def list_change(self):
        global category_box
        global left_vboxx
        global pen
        global brush
        global line_pen
        global im
        global qim
        global current_object
        global coordinates
        global label_list
        progress = 0
        self.a = []
        self.b = []
        count = 0

        cate_info = category_box.currentText().split("/")


        RGB = random.sample(range(0, 255), 3)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        label_list = QRadioButton(category_box.currentText())
        label_list.clicked.connect(self.color_select)
        label_list.setStyleSheet(back_label_color)
        label_list.toggle()
        pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 6)
        line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 2)
        brush = QBrush(QColor(RGB[0], RGB[1], RGB[2]), Qt.Dense2Pattern)
        for i in reversed(range(self.label_vbox.count())):
            self.label_vbox.itemAt(i).widget().deleteLater()
        self.label_vbox.addWidget(label_list)

        super_id = self.DB.get_supercategory_id_from_args(cate_info[1])
        self.current_category = str(self.DB.get_category_id_from_args(str(super_id), cate_info[0]))

        objects = []
        for i in self.DB.list_table("Grid"):
            print("category : " + self.current_category)
            print("grid : " + str(i[0]))
            obj = list(DB.list_object_check_num(self.DB, self.current_category, str(i[0]), "0"))
            if len(obj) != 0:
                objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)
        if len(btn_names) > 0:
            current_object = btn_names[0]
        for i in btn_names:
            temp_btn = QPushButton(i)
            temp_btn.setCheckable(True)
            if count == 0:
                temp_btn.toggle()
                current_object = temp_btn.text()
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if len(self.DB.bbox_info(self.obj_name2id(i))) != 0:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1
        len_a = len(self.a)
        self.progress_state.setText("진행도 : " + str(progress) + "/" + str(len_a))

        for i in reversed(range(1, left_vboxx.count())):
            left_vboxx.itemAt(i).layout().itemAt(1).widget().deleteLater()
            left_vboxx.itemAt(i).layout().itemAt(0).widget().deleteLater()
            left_vboxx.itemAt(i).layout().deleteLater()

        for i in range(len(self.a)):
            left_hbox = QHBoxLayout()
            self.a[i].clicked.connect(self.image_state)
            self.b[i].stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(self.b[i])
            left_vboxx.addLayout(left_hbox)
        scene.clear()
        if len(objects) >= 1:

            img_obj_id = self.obj_name2id(current_object)

            imgd = self.DB.get_table(self.DB.get_table(str(img_obj_id), "Object")[0], "Image")[2]
            self.img_data = np.array(Image.open(BytesIO(imgd)).convert("RGB"))

            qim = QImage(self.img_data, self.img_data.shape[1], self.img_data.shape[0], self.img_data.strides[0],
                         QImage.Format_RGB888)
            w = qim.width()
            h = qim.height()
            im = QPixmap.fromImage(qim)

            qp = QPainter()
            im.setDevicePixelRatio(scale_factor_w)
            qp.begin(im)


            if len(sum(self.DB.bbox_info(img_obj_id), ())) != 0:
                coordinates = self.bbox2coordinate(self.DB.get_table(str(self.DB.get_bbox_id_from_args(img_obj_id)), "Bbox"))
                qp.setPen(line_pen)
                qp.setBrush(QBrush(Qt.transparent))
                qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
            qp.end()
            scene.clear()
            scene.addPixmap(im)
            view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
            scene.update()
        self.update()

    def obj_list2name(self, obj_list):
        btn_name_list = []
        for i in range(len(obj_list)):
            img_id = obj_list[i][0]
            loc_id = obj_list[i][1]
            cate_id = obj_list[i][2]
            # IP 구분이 필요한 경우 사용
            # img = self.DB.get_table(str(img_id), "Image")
            # ip_id = img[0]
            # env = self.DB.get_table(str(ip_id), "Environment")
            # ipv4 = env[1]

            loc = self.DB.get_table(str(loc_id), "Location")
            location_str = str(loc[2]) + "x" + str(loc[3])
            grid = self.DB.get_table(str(loc[0]), "Grid")
            grid_str = str(grid[1]) + "x" + str(grid[2])

            cate = self.DB.get_table(str(cate_id), "Category")
            cate_str = cate[2]
            super_cate = self.DB.get_table(str(cate[0]), "SuperCategory")
            super_cate_str = super_cate[1]

            btn_name = cate_str + "/" + super_cate_str + "_" + location_str + "/" + grid_str + "_" + str(obj_list[i][4]+1)
            btn_name_list.append(btn_name)
        return btn_name_list

    def obj_name2id(self, i):
        #i = "콜라/음료_1x2/3x3_1"

        i = i.split("_")#  "콜라/음료", "1x2/3x3", "1"
        i[0] = i[0].split("/")#  "콜라" "음료" "1x2" "3x3", "1"
        i[1] = i[1].split("/")

        super_id = self.DB.get_supercategory_id_from_args(i[0][1])
        cate_id = self.DB.get_category_id_from_args(str(super_id), i[0][0])
        grid_id = self.DB.get_grid_id_from_args(i[1][1])
        loc_id = self.DB.get_location_id_from_args(str(grid_id), i[1][0])
        obj_id = self.DB.get_obj_id_from_args(str(loc_id), str(cate_id), (int(i[2])-1))
        return str(obj_id)

    def coordinate2bbox(self, coordinate):
        bbox = []
        bbox.append(coordinate[0][0])
        bbox.append(coordinate[0][1])
        bbox.append(abs(coordinate[0][0] - coordinate[1][0]))
        bbox.append(abs(coordinate[0][1] - coordinate[2][1]))
        return bbox

    def bbox2coordinate(self, bbox):
        obj = self.get_table(bbox[0], "Object")
        coor = [[bbox[2], bbox[3]], [bbox[2] + bbox[4], bbox[3]], [bbox[2], bbox[3] + bbox[5]], [bbox[2] + bbox[4], bbox[3] + bbox[5]], obj[2]]
        return coor

    def category_list2name(self, category_list):
        cate_name = []
        for i in category_list:
            a = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if a == "mix":
                continue
            else:
                cate_name.append(i[2] + "/" + self.DB.get_table(str(i[0]), "SuperCategory")[1])
        return cate_name

    def addlabel(self):
        global color_value
        global label_list
        global category_id_list
        category_id_list = []
        label_list = []
        k = 0

        for i in self.label_name_list:
            if i.isChecked():
                color_value.append(random.sample(range(0, 255), 3))
                back_label_color = "background-color: " + QColor(color_value[k][0], color_value[k][1],
                                                                 color_value[k][2]).name()
                label_list.append(QRadioButton(i.text()))
                label_list[k].clicked.connect(self.color_select)
                label_list[k].setStyleSheet(back_label_color)
                k = k + 1
            else:
                continue
        label_list[0].toggle()
        for i in label_list:
            cate_name = i.text()
            cate_name = cate_name.split("/")
            super_id = str(self.DB.get_supercategory_id_from_args(cate_name[1]))
            category_id_list.append(self.DB.get_category_id_from_args(super_id, cate_name[0]))
        self.color_select()
        print(self.label_vbox.count())
        for i in reversed(range(self.label_vbox.count())):
           self.label_vbox.itemAt(i).widget().deleteLater()

        for i in range(len(label_list)):
            self.label_vbox.addWidget(label_list[i])
        self.label_box.setLayout(self.label_vbox)
        self.update()


class tracking_screen(QGraphicsView):
    # 그래픽스(이미지를 보여주는 공간)의 마우스 함수를 커스터마이징 하기위해 만든 새로운 클래스

    def mouseMoveEvent(self, e):
        # 마우스가 움직일 때, 일어나는 이벤트
        global scale_factor_w
        global view
        global draggin_idx
        global minimum_mask
        global edit_btn
        global qp
        global im
        global label_color
        global fill_color
        global qim
        global label_line_color
        global pen
        global line_pen

        # 마우스 위치를 확대, 축소된 이미지에 맞도록 변환
        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        if qim != []:
            w = qim.width()
            h = qim.height()
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods) and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x()/scale_factor_w, e.y()/scale_factor_w, w, h), Qt.KeepAspectRatio)
        # 수정 작업 중 드래그 했을 때, 점과 선이 실시간으로 갱신되도록 설정
        else:
            if mask_btn.isChecked():
                if draggin_idx == 10:

                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(self.start_point.x(), self.start_point.y(), x - self.start_point.x(), y - self.start_point.y()))
                    qp.end()
                    scene.addPixmap(im)

            if edit_btn.isChecked():
                if draggin_idx != -1:
                    a = coordinates[minimum_mask]
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)

                    iter_num = 0
                    for i in coordinates:
                        if iter_num != minimum_mask:
                            qp.setPen(pen)
                            # qp.drawPoints(QPolygon(i))
                            qp.setPen(label_line_color[iter_num])
                            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0]-i[0][0], i[3][1]-i[0][1]))
                        iter_num = iter_num + 1


                    qp.setPen(label_line_color[minimum_mask])
                    if draggin_idx == 0:
                        qp.drawRect(QRect(x, y, a[3][0] - x, a[3][1] - y))
                        coordinates[minimum_mask][0] = [x, y]
                        coordinates[minimum_mask][1] = [a[1][0], y]
                        coordinates[minimum_mask][2] = [x, a[2][1]]
                    elif draggin_idx == 1:
                        qp.drawRect(QRect(a[0][0], y, x - a[0][0], a[2][1] - y))
                        coordinates[minimum_mask][0] = [a[0][0], y]
                        coordinates[minimum_mask][1] = [x, y]
                        coordinates[minimum_mask][3] = [x, a[2][1]]
                    elif draggin_idx == 2:
                        qp.drawRect(QRect(x, a[0][1], a[1][0] - x, y - a[0][1]))
                        coordinates[minimum_mask][0] = [x, a[0][1]]
                        coordinates[minimum_mask][2] = [x, y]
                        coordinates[minimum_mask][3] = [a[1][0], y]
                    elif draggin_idx == 3:
                        qp.drawRect(QRect(a[0][0], a[0][1], x - a[0][0], y - a[0][1]))
                        coordinates[minimum_mask][1] = [x, a[0][1]]
                        coordinates[minimum_mask][2] = [a[0][0], y]
                        coordinates[minimum_mask][3] = [x, y]

                    qp.end()
                    scene.addPixmap(im)



    def mouseReleaseEvent(self, e):
        # 마우스가 클릭됬다가 떨어질 때 발생하는 이벤트
        global view
        global scale_factor_w
        global draggin_idx
        global minimum_mask
        global edit_btn
        global qp
        global im
        global mask_num
        global label_color
        global fill_color
        global qim
        global label_line_color
        global mask_btn
        global coordinates


        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods):
            print("nothing")
        else:
            if mask_btn.isChecked():

                label_color.append(pen)
                label_line_color.append(line_pen)
                fill_color.append(brush)
                for i in range(len(color_value)):
                    if QColor(color_value[i][0], color_value[i][1], color_value[i][2]) == line_pen.color():
                        cate_id = self.name2cate_id(label_list[i].text())
                        print("cate_id = " + str(cate_id))
                coordinates.append([[self.start_point.x(), self.start_point.y()], [x, self.start_point.y()], [self.start_point.x(), y], [x, y], cate_id])


                qp = QPainter()
                im.setDevicePixelRatio(scale_factor_w)
                qp.begin(im)
                iter_num = 0
                for i in coordinates:
                    qp.setPen(label_line_color[iter_num])
                    if mask_num == iter_num:
                        qp.setBrush(fill_color[iter_num])
                    else:
                        qp.setBrush(QBrush(Qt.transparent))
                    qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                    iter_num = iter_num + 1

                qp.end()
                scene.clear()
                scene.addPixmap(im)
                self.repaint()


                if draggin_idx == 10:

                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(self.start_point.x(), self.start_point.y(), x - self.start_point.x(), y - self.start_point.y()))
                    qp.end()
                    scene.addPixmap(im)
                draggin_idx = -1

            # 수정 작업중일 때, 마우스가 때지면 최종 수정된 마스크 값으로 마스크 값을 갱신
            if edit_btn.isChecked():
                if e.button() == Qt.LeftButton and draggin_idx == 0:
                    a = coordinates[minimum_mask]
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    iter_num = 0
                    for i in coordinates:
                        if iter_num != minimum_mask:
                            if mask_num == iter_num:
                                qp.setBrush(fill_color[iter_num])
                            else:
                                qp.setBrush(QBrush(Qt.transparent))
                            qp.setPen(label_line_color[iter_num])
                            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                        iter_num = iter_num + 1

                    if mask_num == minimum_mask:
                        qp.setBrush(fill_color[minimum_mask])
                    qp.setPen(label_line_color[minimum_mask])

                    if draggin_idx == 0:
                        qp.drawRect(QRect(x, y, a[3][0] - x, a[3][1] - y))
                        coordinates[minimum_mask][0] = [x, y]
                        coordinates[minimum_mask][1] = [a[1][0], y]
                        coordinates[minimum_mask][2] = [x, a[2][1]]
                    elif draggin_idx == 1:
                        qp.drawRect(QRect(a[0][0], y, x - a[0][0], a[2][1] - y))
                        coordinates[minimum_mask][0] = [a[0][0], y]
                        coordinates[minimum_mask][1] = [x, y]
                        coordinates[minimum_mask][3] = [x, a[2][1]]
                    elif draggin_idx == 2:
                        qp.drawRect(QRect(x, a[0][1], a[1][0] - x, y - a[0][1]))
                        coordinates[minimum_mask][0] = [x, a[0][1]]
                        coordinates[minimum_mask][2] = [x, y]
                        coordinates[minimum_mask][3] = [a[1][0], y]
                    elif draggin_idx == 3:
                        qp.drawRect(QRect(a[0][0], a[0][1], x - a[0][0], y - a[0][1]))
                        coordinates[minimum_mask][1] = [x, a[0][1]]
                        coordinates[minimum_mask][2] = [a[0][0], y]
                        coordinates[minimum_mask][3] = [x, y]

                    #qp.setPen(label_color[minimum_mask])
                    #qp.drawPoints(QRect(a))
                    qp.end()
                    scene.addPixmap(im)
                draggin_idx = -1
                print("minimum_mask : " + str(minimum_mask))

    def wheelEvent(self, ev):

        # 휠이 움직일때 발생하는 이벤트
        mods = ev.modifiers()
        delta = ev.angleDelta()

        global scale_factor_w
        global qp
        global scene
        global im
        global view

        # ctrl+휠을 하면 이미지의 사이즈가 확대, 축소 되도록 수정
        w = im.width()
        h = im.height()
        if Qt.ControlModifier == int(mods):
            qp = QPainter()
            qp.begin(im)
            # 확대, 축소비율 설정 휠이 한번 움직일때마다 10%씩 작아지거나 커짐, 최소, 최대 크기는 0.5배에서 4배로 설정
            if delta.y() > 0 and scale_factor_w > 0.25:
                scale_factor_w = scale_factor_w * 0.9
            elif scale_factor_w < 2 and delta.y() < 0:
                scale_factor_w = scale_factor_w * 1.1

            im.setDevicePixelRatio(scale_factor_w)
            qp.end()
            scene.clear()
            scene.addPixmap(im)
            w = qim.width()
            h = qim.height()
            view.fitInView(QRectF(ev.x() / scale_factor_w, ev.y() / scale_factor_w, w, h), Qt.KeepAspectRatio)


    def mousePressEvent(self, e):
        # 마우스를 클릭했을 때, 발생하는 이벤트트
        global view
        global scale_factor_w

        global draggin_idx
        global minimum_mask
        global edit_btn
        global qp
        global pen
        global scene
        global brush
        global mask_num
        global mask_btn
        global fill_color
        global label_color
        global line_pen
        global label_line_color
        global im
        global current_label
        global color_value

        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        w = qim.width()
        h = qim.height()
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods) and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x() / scale_factor_w, e.y() / scale_factor_w, w, h), Qt.KeepAspectRatio)
        else:
            # 마스킹 작업 중 이벤트
            if mask_btn.isChecked():
                # 좌클릭시 포인트 생성 및 선 생성
                if e.buttons() == Qt.LeftButton:
                    self.start_point = QPoint(x, y)
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(pen)
                    qp.drawPoint(x, y)
                    qp.end()
                    scene.addPixmap(im)
                    draggin_idx = 10

            # 수정 작업중 발생하는 이벤트
            # 클릭위치와 가장 가까운 점을 계산하여 해당 포인트를 마우스 위치로 수정
            if edit_btn.isChecked():
                min_group = []

                if len(coordinates) != 0:
                    if e.buttons() == Qt.LeftButton and draggin_idx == -1:
                        point = [x, y]

                        for i in coordinates:
                            dist = np.array(i[:4]) - np.array(point)
                            dist = dist[:, 0] ** 2 + dist[:, 1] ** 2
                            min_group.append(min(dist))
                            dist = []

                        min_group = np.array(min_group)
                        minimum_mask = min_group.argmin()
                        min_dist = np.array(coordinates[minimum_mask][:4]) - np.array(point)
                        min_dist = np.array(min_dist[:, 0] ** 2 + min_dist[:, 1] ** 2)
                        minimum_value = min_dist.argmin()

                        # 마우스 위치와 포인트의 위치 사이의 거리가 1000이상일 경우 작업x
                        # print(min_group.min())
                        if min_group.min() < 1000:
                            draggin_idx = minimum_value
                            # print(draggin_idx)

                iter_num = 0
                # 마스크내부에 클릭이 됬을 경우 해당 마스크를 색칠
                for i in coordinates:
                    if QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]).contains(QPoint(x, y)) and e.buttons() == Qt.LeftButton and iter_num == 0:
                        mask_num = iter_num

                        qp = QPainter()
                        im = QPixmap.fromImage(qim)
                        im.setDevicePixelRatio(scale_factor_w)
                        qp.begin(im)
                        qp.setPen(label_line_color[mask_num])
                        qp.setBrush(fill_color[mask_num])
                        qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                        qp.end()
                        scene.addPixmap(im)

                        # 현재 마스크가 어떤 마스크인지 좌측에 표시해주는 코드
                        for i in range(len(color_value)):
                            if QColor(color_value[i][0], color_value[i][1], color_value[i][2]) == label_color[mask_num].color():
                                current_label.setText(label_list[i].text())

                    elif QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]).contains(QPoint(x, y)) and e.buttons() == Qt.LeftButton:
                        if mask_num != 1000000:
                            qp = QPainter()
                            qp.begin(im)
                            qp.setPen(label_line_color[mask_num])
                            qp.setBrush(QBrush(Qt.transparent))
                            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                            qp.end()
                            scene.addPixmap(im)

                            mask_num = iter_num
                            qp = QPainter()
                            qp.begin(im)
                            qp.setPen(label_line_color[mask_num])
                            qp.setBrush(fill_color[mask_num])
                            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                            qp.end()
                            scene.addPixmap(im)
                            for i in range(len(color_value)):
                                if QColor(color_value[i][0], color_value[i][1], color_value[i][2]) == label_color[mask_num].color():
                                    current_label.setText(label_list[i].text())

                        else:
                            mask_num = iter_num

                            qp = QPainter()
                            qp.begin(im)
                            qp.setPen(label_line_color[mask_num])
                            qp.setBrush(fill_color[mask_num])
                            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                            qp.end()
                            scene.addPixmap(im)

                    elif iter_num == 0:
                        qp = QPainter()
                        im = QPixmap.fromImage(qim)
                        im.setDevicePixelRatio(scale_factor_w)
                        qp.begin(im)
                        qp.setPen(label_line_color[iter_num])
                        qp.setBrush(QBrush(Qt.transparent))
                        qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                        qp.end()
                        scene.addPixmap(im)

                    else:
                        qp = QPainter()
                        qp.begin(im)
                        qp.setPen(label_line_color[iter_num])
                        qp.setBrush(QBrush(Qt.transparent))
                        qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                        qp.end()
                        scene.addPixmap(im)

                    iter_num = iter_num + 1
                print(mask_num)

    def name2cate_id(self, name):
        mydb = DB.DB('192.168.10.69', 3306, 'root', 'return123', 'test')
        name = name.split("/")
        sup_id = mydb.get_supercategory_id_from_args(name[1])
        cate_id = mydb.get_category_id_from_args(str(sup_id), name[0])
        return cate_id