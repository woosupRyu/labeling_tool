from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import random
from io import BytesIO
from PIL import Image
from DCD_DB_API_master.db_api import DB
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
global coordinates # 비박스 정보 (좌상좌표, 우상좌표, 좌하좌표, 우하좌표, 카테고리)
global category_box # 물품 선택 박스
global left_vboxx
global current_object # 현재 작업중인 원본 오브젝트
global label_list # 라벨링할 수 있는 라벨 리스트
global category_id_list
global mix_label_color # 물품의 아이디를 key로 받아 해당 물품의 색을 반환해주는 딕셔너리

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
        global mix_label_color

        #초기값 설정
        self.collect_color = [[255, 0, 0], [255, 0, 80], [255, 0, 160], [255, 0, 240], [190, 0, 255], [110, 0, 255], [30, 0, 255], [0, 130, 255], [0, 210, 255], [0, 255, 220], [0, 255, 140], [0, 255, 60], [100, 255, 0], [180, 255, 0], [240, 255, 0], [255, 160, 0], [255, 80, 0], [128, 64, 64], [112, 64, 128], [64, 96, 128], [64, 128, 80], [128, 128, 64], [190, 94, 94], [190, 94, 174], [126, 94, 190], [94, 142, 190], [94, 190, 158]]
        mix_label_color = {}
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
        global mix_label_color
        global label_color
        global label_line_color
        global fill_color

        progress = 0
        # 이미지를 보여줄 그래픽스 공간 생성
        scene = QGraphicsScene()
        view = tracking_screen(scene)
        view.setMouseTracking(True)

        # 편의 기능들 생성
        self.btn_group = QButtonGroup()
        self.label_group = QButtonGroup()

        edit_btn = QPushButton("수정(E)")
        edit_btn.setCheckable(True)
        edit_btn.setShortcut("E")
        edit_btn.setToolTip("E")
        mask_btn = QPushButton("비박싱(Q)")
        mask_btn.setCheckable(True)
        mask_btn.setShortcut("Q")
        mask_btn.setToolTip("Q")
        mask_btn.toggle()
        label_change_btn = QPushButton("라벨수정(F)")
        label_change_btn.setShortcut("F")
        label_change_btn.clicked.connect(self.change_label)
        original_size_btn = QPushButton("기본크기(G)")
        original_size_btn.setShortcut("G")
        original_size_btn.setToolTip("G")
        original_size_btn.clicked.connect(self.set_original_size)
        mask_delete_btn = QPushButton("마스크 삭제(Delete)")
        mask_delete_btn.setShortcut("Delete")
        mask_delete_btn.clicked.connect(self.delete_mask)
        save_btn = QPushButton("저장(S)")
        save_btn.setStyleSheet("background-color: blue")
        save_btn.setShortcut("S")
        save_btn.setToolTip("S")
        save_btn.clicked.connect(self.save_info)
        next_btn = QPushButton("->(D)")
        next_btn.clicked.connect(self.move_image)
        next_btn.setShortcut("D")
        next_btn.setToolTip("D")
        before_btn = QPushButton("<-(A)")
        before_btn.clicked.connect(self.move_image)
        before_btn.setShortcut("A")
        before_btn.setToolTip("A")
        #label_label = QLabel("선택 마스크의 라벨")
        current_label = QLineEdit()
        category_box = QComboBox()

        label_frame = QFrame()
        label_frame.setFrameShape(QFrame.Box)
        ver_box = QVBoxLayout()

        #라벨링 해야할 물품들을 선택할 수 있는 박스 생성
        self.label_name_list = []
        category_name_list = self.category_list2name(self.DB.list_table("Category"))
        num = 0
        for i in category_name_list:
            label_box = QCheckBox(i)
            label_box.clicked.connect(self.addlabel)
            self.label_name_list.append(label_box)
            ver_box.addWidget(label_box)
            num = num + 1
        label_frame.setLayout(ver_box)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(label_frame)

        #분류가 mix인 물품중 작업할 물품을 선택할 수 있는 박스 생생
        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if super_name == "mix":
                category_box.addItem(i[2] + "/" + super_name)

        self.a = []
        self.b = []
        count = 0

        #현재 물품의 모든 오브젝트와 연동되는 버튼 생성
        cate_info = category_box.currentText().split("/")
        super_id = self.DB.get_supercategory_id_from_args(cate_info[1])
        self.current_category = str(self.DB.get_category_id_from_args(str(super_id), cate_info[0]))
        objects = []
        for i in self.DB.list_table("Grid"):
            if i[1] == 0:
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
            if len(DB.get_bbox_from_img_id(self.DB, str(self.obj_name2img_id(i)))) != 0:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1
        obj_id = self.obj_name2id(current_object)

        exist_bbox = DB.get_bbox_from_img_id(self.DB, str(self.DB.get_table(obj_id, "Object")[0]))

        self.label_vbox = QVBoxLayout()
        self.label_box = QGroupBox()

        # 생성된 오브젝트에 비박스가 존재할 경우 필요 라벨 호출
        category_name = category_box.currentText()
        if len(exist_bbox) == 0:
            RGB = random.choice(self.collect_color)
            back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
            label_list = QRadioButton(category_name)
            label_list.clicked.connect(self.color_select)
            label_list.setStyleSheet(back_label_color)
            label_list.toggle()
            self.addlabel()
        else:
            cate_list = []
            for j in exist_bbox:
                bbox_cate = self.bbox2cate_id(j)

                cate_list.append(bbox_cate)
                coor = self.bbox2coordinate(j)
                coor.append(bbox_cate)
                coordinates.append(coor)

            bbox_label_list = self.category_id2name(cate_list)

            for i in range(len(category_name_list)):
                if category_name_list[i] in bbox_label_list:
                    self.label_name_list[i].setChecked(True)
                    self.addlabel()
            label_line_color = []
            label_color = []
            fill_color = []
            for i in coordinates:
                label_line_color.append(QPen(mix_label_color[i[4]], 6))
                label_color.append(QPen(mix_label_color[i[4]], 2))
                fill_color.append(QBrush(mix_label_color[i[4]], Qt.Dense2Pattern))

        # 버튼 좌측의 체크박스 기준으로 현재 작업진행도 표시
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

        #버튼, 체크박스에 기능 연동
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

        if type(label_list) == list:
            for i in label_list:
                self.label_vbox.addWidget(i)
        else:
            self.label_vbox.addWidget(label_list)
        self.label_box.setLayout(self.label_vbox)

        # 이미지에 비박스가 존재하는 경우 이미지에 표시
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

            if len(exist_bbox) != 0:
                for i in range(len(coordinates)):
                    pen = label_color[i]
                    line_pen = label_line_color[i]
                    brush = fill_color[i]
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(coordinates[i][0][0], coordinates[i][0][1], coordinates[i][3][0] - coordinates[i][0][0], coordinates[i][3][1] - coordinates[i][0][1]))
            self.color_select()
            qp.end()
            scene.clear()
            scene.addPixmap(im)
            view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
            scene.update()

        vbox = QVBoxLayout()
        vbox.addWidget(edit_btn)
        vbox.addWidget(mask_btn)
        vbox.addWidget(label_change_btn)
        vbox.addWidget(original_size_btn)
        vbox.addWidget(mask_delete_btn)
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

        self.resize(1500, 1000)
        self.setWindowTitle("비박싱")
        self.setLayout(hbox)
        self.show()

    def color_select(self):
        #현재의 컬러에 해당하는 팬(비박스 그리는 객체), 브러시(비박스 색칠하는 객체) 설정
        k = 0
        global pen
        global brush
        global line_pen
        global color_value
        global label_list
        if type(label_list) == list:
            for i in label_list:
                if i.isChecked():
                    pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 6)
                    line_pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 2)
                    brush = QBrush(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), Qt.Dense2Pattern)
                k = k + 1
        else:
            pen = QPen(QColor(color_value[0][0], color_value[0][1], color_value[0][2]), 6)
            line_pen = QPen(QColor(color_value[0][0], color_value[0][1], color_value[0][2]), 2)
            brush = QBrush(QColor(color_value[0][0], color_value[0][1], color_value[0][2]), Qt.Dense2Pattern)

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
        global line_pen
        global pen
        global brush

        #변수 초기화 및 이미지 표시
        scale_factor_w = 1
        mask_num = 1000000
        draggin_idx = -1
        self.collect_color = [[255, 0, 0], [255, 0, 80], [255, 0, 160], [255, 0, 240], [190, 0, 255], [110, 0, 255], [30, 0, 255], [0, 130, 255], [0, 210, 255], [0, 255, 220], [0, 255, 140], [0, 255, 60], [100, 255, 0], [180, 255, 0], [240, 255, 0], [255, 160, 0], [255, 80, 0], [128, 64, 64], [112, 64, 128], [64, 96, 128], [64, 128, 80], [128, 128, 64], [190, 94, 94], [190, 94, 174], [126, 94, 190], [94, 142, 190], [94, 190, 158]]

        label_color = []
        label_line_color = []
        fill_color = []
        coordinates = []
        current_object = self.sender().text()
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

        # 이미지에 비박스가 존재할 경우 필요라벨 호출 및 표시
        category_name_list = self.category_list2name(self.DB.list_table("Category"))
        exist_bbox = DB.get_bbox_from_img_id(self.DB, str(self.DB.get_table(img_obj_id, "Object")[0]))
        if len(exist_bbox) != 0:
            cate_list = []
            for j in exist_bbox:
                bbox_cate = self.bbox2cate_id(j)
                cate_list.append(bbox_cate)
                coor = self.bbox2coordinate(j)
                coor.append(bbox_cate)
                coordinates.append(coor)

            bbox_label_list = self.category_id2name(cate_list)

            for i in range(len(category_name_list)):
                if category_name_list[i] in bbox_label_list:
                    self.label_name_list[i].setChecked(True)
                    self.addlabel()
            label_line_color = []
            label_color = []
            fill_color = []

            for i in coordinates:
                label_line_color.append(QPen(mix_label_color[i[4]], 6))
                label_color.append(QPen(mix_label_color[i[4]], 2))
                fill_color.append(QBrush(mix_label_color[i[4]], Qt.Dense2Pattern))
            for i in label_list:
                self.label_vbox.addWidget(i)
            self.label_box.setLayout(self.label_vbox)

            for i in range(len(coordinates)):
                pen = label_color[i]
                line_pen = label_line_color[i]
                brush = fill_color[i]
                qp.setPen(line_pen)
                qp.drawRect(QRect(coordinates[i][0][0], coordinates[i][0][1],
                                  coordinates[i][3][0] - coordinates[i][0][0],
                                  coordinates[i][3][1] - coordinates[i][0][1]))
            self.color_select()

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

        # 이미지와 관련된 모든 비박스 삭제
        img_obj_id = self.obj_name2id(current_object)
        img_id = str(self.DB.get_table(img_obj_id, "Object")[0])
        loc_id = str(self.DB.get_location_id_from_args(str(self.DB.get_grid_id_from_args("0x0")), '0x0'))
        category_id_list = sorted(category_id_list)
        iteration = current_object.split("_")[2]

        DB.delete_nomix_object_from_img_id(self.DB, str(img_id))

        #현재의 비박스 정보들을 저장
        if len(coordinates) != 0:
            for i in range(len(category_id_list)):
                for j in coordinates:
                    if j[4] == category_id_list[i]:
                        num = DB.get_max_mix_num(self.DB, loc_id, str(j[4]), iteration)
                        self.DB.set_object(img_id, loc_id, str(j[4]), iteration, str(int(num+1)))
                        box_info = self.coordinate2bbox(j)
                        self.DB.set_bbox(str(self.DB.get_last_id("Object"))[2:-3], str(box_info[0]), str(box_info[1]), str(box_info[2]), str(box_info[3]))
            for i in range(len(self.a)):
                if self.a[i].isChecked():
                    self.b[i].setCheckState(Qt.Checked)

    def move_image(self):
        # 보여지는 이미지를 이동하는 함수
        len_a = len(self.a)
        sender = self.sender().text()
        if sender == "<-(A)":
            for i in range(len_a):
                if self.a[i].isChecked():
                    if i > 0:
                        self.a[i - 1].click()
                        break
        elif sender == "->(D)":
            for i in range(len_a):
                if self.a[i].isChecked():
                    if i < (len_a - 1):
                        self.a[i + 1].click()
                        break

    def list_change(self):
        # 보고싶은 물품을 갱신했을 경우 실행되는 함수
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
        global pen
        global brush
        global label_color
        global label_line_color
        global fill_color
        global scale_factor_w
        global mask_num
        global draggin_idx
        global category_id_list
        global color_value

        #변수들 초기화
        category_id_list = []

        progress = 0
        self.a = []
        self.b = []
        count = 0
        coordinates = []
        color_value = []

        scale_factor_w = 1
        mask_num = 1000000
        draggin_idx = -1

        label_color = []
        label_line_color = []
        fill_color = []
        coordinates = []
        self.collect_color = [[255, 0, 0], [255, 0, 80], [255, 0, 160], [255, 0, 240], [190, 0, 255], [110, 0, 255], [30, 0, 255], [0, 130, 255], [0, 210, 255], [0, 255, 220], [0, 255, 140], [0, 255, 60], [100, 255, 0], [180, 255, 0], [240, 255, 0], [255, 160, 0], [255, 80, 0], [128, 64, 64], [112, 64, 128], [64, 96, 128], [64, 128, 80], [128, 128, 64], [190, 94, 94], [190, 94, 174], [126, 94, 190], [94, 142, 190], [94, 190, 158]]

        cate_info = category_box.currentText().split("/")

        #선택된 라벨 초기화
        for i in self.label_name_list:
            i.setCheckState(Qt.Unchecked)

        RGB = random.choice(self.collect_color)
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
            if len(DB.get_bbox_from_img_id(self.DB, str(self.obj_name2img_id(i)))) != 0:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1

        obj_id = self.obj_name2id(current_object)
        exist_bbox = DB.get_bbox_from_img_id(self.DB, str(self.DB.get_table(obj_id, "Object")[0]))
        category_name = category_box.currentText()
        if len(exist_bbox) == 0:
            RGB = random.choice(self.collect_color)
            back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
            label_list = QRadioButton(category_name)
            label_list.clicked.connect(self.color_select)
            label_list.setStyleSheet(back_label_color)
            label_list.toggle()
            pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 6)
            line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 2)
            brush = QBrush(QColor(RGB[0], RGB[1], RGB[2]), Qt.Dense2Pattern)
        else:
            category_name_list = self.category_list2name(self.DB.list_table("Category"))
            cate_list = []
            for j in exist_bbox:
                bbox_cate = self.bbox2cate_id(j)
                cate_list.append(bbox_cate)
                coor = self.bbox2coordinate(j)
                coor.append(bbox_cate)
                coordinates.append(coor)

            bbox_label_list = self.category_id2name(cate_list)

            for i in range(len(category_name_list)):
                if category_name_list[i] in bbox_label_list:
                    self.label_name_list[i].setChecked(True)
                    self.addlabel()
            label_line_color = []
            label_color = []
            fill_color = []
            for i in coordinates:
                label_line_color.append(QPen(mix_label_color[i[4]], 6))
                label_color.append(QPen(mix_label_color[i[4]], 2))
                fill_color.append(QBrush(mix_label_color[i[4]], Qt.Dense2Pattern))
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

            if len(exist_bbox) != 0:
                for i in range(len(coordinates)):
                    pen = label_color[i]
                    line_pen = label_line_color[i]
                    brush = fill_color[i]
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(coordinates[i][0][0], coordinates[i][0][1], coordinates[i][3][0] - coordinates[i][0][0], coordinates[i][3][1] - coordinates[i][0][1]))
                self.color_select()
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

            btn_name = cate_str + "/" + super_cate_str + "_" + location_str + "/" + grid_str + "_" + str(obj_list[i][4])
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
        obj_id = self.DB.get_obj_id_from_args(str(loc_id), str(cate_id), i[2], "-1")
        return str(obj_id)

    def coordinate2bbox(self, coordinate):
        bbox = []
        bbox.append(coordinate[0][0])
        bbox.append(coordinate[0][1])
        bbox.append(abs(coordinate[0][0] - coordinate[1][0]))
        bbox.append(abs(coordinate[0][1] - coordinate[2][1]))
        return bbox

    def bbox2coordinate(self, bbox):
        obj = self.DB.get_table(bbox[0], "Object")
        coor = [[bbox[2], bbox[3]], [bbox[2] + bbox[4], bbox[3]], [bbox[2], bbox[3] + bbox[5]], [bbox[2] + bbox[4], bbox[3] + bbox[5]], obj[2]]
        return coor

    def category_list2name(self, category_list):
        cate_name = []
        for i in category_list:
            a = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if a == "mix" or a == "background":
                continue
            else:
                cate_name.append(i[2] + "/" + self.DB.get_table(str(i[0]), "SuperCategory")[1])
        return cate_name

    def category_id2name(self, category_id):
        cate_name = []
        for i in category_id:
            a = self.DB.get_table(str(i), "Category")
            b = self.DB.get_table(str(a[0]), "SuperCategory")[1]
            if a == "mix" or a == "background":
                continue
            else:
                cate_name.append(a[2] + "/" + b)
        return cate_name

    def addlabel(self):
        global color_value
        global label_list
        global category_id_list
        global mix_label_color
        category_id_list = []
        label_list = []
        color_value = []
        k = 0
        mix_label_color = {}
        for i in self.label_name_list:
            if i.isChecked():
                selected_color = random.choice(self.collect_color)
                self.collect_color.remove(selected_color)

                color_value.append(selected_color)
                label_col = QColor(color_value[k][0], color_value[k][1], color_value[k][2])
                back_label_color = "background-color: " + label_col.name()
                label_str = i.text()
                label_list.append(QRadioButton(label_str))
                label_id = self.DB.get_category_id_from_args(str(self.DB.get_supercategory_id_from_args(label_str.split("/")[1])), label_str.split("/")[0])
                mix_label_color[label_id] = label_col


                label_list[k].clicked.connect(self.color_select)
                label_list[k].setStyleSheet(back_label_color)
                k = k + 1
            else:
                continue
        self.collect_color = [[255, 0, 0], [255, 0, 80], [255, 0, 160], [255, 0, 240], [190, 0, 255], [110, 0, 255], [30, 0, 255], [0, 130, 255], [0, 210, 255], [0, 255, 220], [0, 255, 140], [0, 255, 60], [100, 255, 0], [180, 255, 0], [240, 255, 0], [255, 160, 0], [255, 80, 0], [128, 64, 64], [112, 64, 128], [64, 96, 128], [64, 128, 80], [128, 128, 64], [190, 94, 94], [190, 94, 174], [126, 94, 190], [94, 142, 190], [94, 190, 158]]


        if k == 0:
            RGB = random.choice(self.collect_color)
            color_value.append(RGB)
            back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
            category_name = category_box.currentText()
            label_list = QRadioButton(category_name)
            label_list.clicked.connect(self.color_select)
            label_list.setStyleSheet(back_label_color)
            label_list.toggle()
        if type(label_list) == list:
            label_list[0].toggle()
            for i in label_list:
                cate_name = i.text()
                cate_name = cate_name.split("/")
                super_id = str(self.DB.get_supercategory_id_from_args(cate_name[1]))
                category_id_list.append(self.DB.get_category_id_from_args(super_id, cate_name[0]))
        else:
            cate_name = label_list.text()
            cate_name = cate_name.split("/")
            super_id = str(self.DB.get_supercategory_id_from_args(cate_name[1]))
            category_id_list.append(self.DB.get_category_id_from_args(super_id, cate_name[0]))
        self.color_select()
        for i in reversed(range(self.label_vbox.count())):
           self.label_vbox.itemAt(i).widget().deleteLater()

        if type(label_list) == list:
            for i in range(len(label_list)):
                self.label_vbox.addWidget(label_list[i])
        else:
            self.label_vbox.addWidget(label_list)
        self.label_box.setLayout(self.label_vbox)
        self.update()

    def delete_mask(self):
        # 선택 마스크를 삭제하는 버튼과 연결된 함수
        global mask_num
        global qp
        global im
        global scene
        global fill_color
        global label_color
        global qim
        global label_line_color
        global coordinates

        # 선택된 마스크가 없으면 실행되는 함수
        if mask_num == 1000000:
            print("no mask")
        else:

            del coordinates[mask_num]

            del label_color[mask_num]
            del fill_color[mask_num]
            del label_line_color[mask_num]

            qp = QPainter()
            im = QPixmap.fromImage(qim)
            im.setDevicePixelRatio(scale_factor_w)
            qp.begin(im)
            iter_num = 0
            for i in coordinates:
                qp.setPen(label_line_color[iter_num])
                qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
                iter_num = iter_num + 1
            qp.end()
            scene.clear()
            scene.addPixmap(im)
            mask_num = 1000000

    def change_label(self):
        # 마스크의 라벨을 수정하는 버튼과 연결된 함수
        global scale_factor_w
        global qp
        global mask_num
        global scene
        global im
        global fill_color
        global label_color
        global pen
        global brush
        global coordinates
        global pen
        global brush
        global line_pen
        global color_value
        global label_list

        k = 0
        for i in label_list:
            if i.isChecked():
                lc = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 6)
                line_lc = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 2)
                bc = QBrush(QColor(color_value[k][0], color_value[k][1], color_value[k][2]),
                            Qt.Dense3Pattern)
            k = k + 1
        qp = QPainter()
        im = QPixmap.fromImage(qim)
        im.setDevicePixelRatio(scale_factor_w)
        qp.begin(im)
        iter_num = 0
        for i in coordinates:
            if mask_num == iter_num:
                label_line_color[iter_num] = line_lc
                qp.setPen(label_line_color[iter_num])
                label_color[iter_num] = lc
                for j in range(len(label_list)):
                    if label_list[j].isChecked():
                        coordinates[iter_num][4] = self.category_name2id(label_list[j].text())

            else:
                qp.setPen(label_line_color[iter_num])
            if mask_num == iter_num:
                fill_color[iter_num] = bc
                qp.setBrush(fill_color[iter_num])
            else:
                qp.setBrush(QBrush(Qt.transparent))
            qp.drawRect(QRect(i[0][0], i[0][1], i[3][0] - i[0][0], i[3][1] - i[0][1]))
            iter_num = iter_num + 1
        qp.end()
        scene.clear()
        scene.addPixmap(im)
        self.repaint()

    def bbox2cate_id(self, bbox):
        cate_table = self.DB.get_table(str(self.DB.get_table(str(bbox[0]), "Object")[2]), "Category")[1]
        return cate_table

    def obj_name2img_id(self, obj_name):
        obj_id = self.obj_name2id(obj_name)
        return self.DB.get_table(obj_id, "Object")[0]

    def category_name2id(self, name):
        name = name.split("/")
        return self.DB.get_category_id_from_args(str(self.DB.get_supercategory_id_from_args(name[1])), name[0])



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

                    for i in range(len(coordinates)):
                        qp.setPen(pen)
                        qp.setPen(label_line_color[i])
                        qp.drawRect(QRect(coordinates[i][0][0], coordinates[i][0][1], coordinates[i][3][0] - coordinates[i][0][0], coordinates[i][3][1] - coordinates[i][0][1]))
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
        global label_list


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
                        tem_coor = self.bbox2coordinate([x, y, a[3][0] - x, a[3][1] - y])
                        coordinates[minimum_mask] = self.point_sort(tem_coor)

                    elif draggin_idx == 1:
                        qp.drawRect(QRect(a[0][0], y, x - a[0][0], a[2][1] - y))
                        tem_coor = self.bbox2coordinate([a[0][0], y, x - a[0][0], a[2][1] - y])
                        coordinates[minimum_mask] = self.point_sort(tem_coor)
                    elif draggin_idx == 2:
                        qp.drawRect(QRect(x, a[0][1], a[1][0] - x, y - a[0][1]))
                        tem_coor = self.bbox2coordinate([x, a[0][1], a[1][0] - x, y - a[0][1]])
                        coordinates[minimum_mask] = self.point_sort(tem_coor)
                    elif draggin_idx == 3:
                        qp.drawRect(QRect(a[0][0], a[0][1], x - a[0][0], y - a[0][1]))
                        tem_coor = self.bbox2coordinate([a[0][0], a[0][1], x - a[0][0], y - a[0][1]])
                        coordinates[minimum_mask] = self.point_sort(tem_coor)

                    #qp.setPen(label_color[minimum_mask])
                    #qp.drawPoints(QRect(a))
                    qp.end()
                    scene.addPixmap(im)
                draggin_idx = -1


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
                        if min_group.min() < 1000:
                            draggin_idx = minimum_value


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

    def name2cate_id(self, name):
        mydb = DB.DB('192.168.10.69', 3306, 'root', 'return123', 'test')
        name = name.split("/")
        sup_id = mydb.get_supercategory_id_from_args(name[1])
        cate_id = mydb.get_category_id_from_args(str(sup_id), name[0])
        return cate_id

    def point_sort(self, coordinate):
        # 점들의 로케이션이 달라질 경우를 대비한 로케이션 재설정 함수
        sorted_coord = sorted(coordinate)
        new_coord = [[], [], [], []]
        new_coord[0] = sorted_coord[0]
        new_coord[1] = sorted_coord[2]
        new_coord[2] = sorted_coord[1]
        new_coord[3] = sorted_coord[3]
        return new_coord

    def bbox2coordinate(self, bbox):
        # 비박스의 x, y, w, h를 받아 네 점의 좌표를 반환
        coor = [[bbox[0], bbox[1]], [bbox[0] + bbox[2], bbox[1]], [bbox[0], bbox[1] + bbox[3]],
                [bbox[0] + bbox[2], bbox[1] + bbox[3]]]
        return coor
