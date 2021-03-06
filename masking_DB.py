from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import random
from io import BytesIO
from PIL import Image
import viewer
#그래픽스 클래스에서도 참조해야할 변수들 글로벌로 선언

global check_state #마스킹 작업 상태 표시
global edit_btn # 수정 버튼
global draggin_idx # 드래그 작업 참조 변수
global mask_btn # 마스킹 버튼
global im # 마스크를 포함한 이미지
global qim # 마스크 없는 원 이미지
global label_name #라벨 이름
global color_value # 색의 실제 값
global category_box # 현재 선택할 수 있는 물품을 보여주는 박스
global left_vboxx
global current_object # 현재 선택된 오브젝트
global point_num

class mask(QWidget):
    def __init__(self, db):
        super().__init__()
        self.DB = db
        global draggin_idx
        global label_name
        global color_value
        global check_state
        global qim
        global point_num
        global current_object

        current_object = ""


        #변수들 초기화
        self.collect_color = [[255, 0, 0], [255, 255, 0], [0, 255, 255], [0, 255, 0], [255, 0, 255]]

        check_state = 100 # 작업중이 아님을 나타내는 값 선언
        draggin_idx = -1
        color_value = []
        self.label_list = []
        qim = []
        point_num = 0

    def masking(self):
        global edit_btn
        global im
        global mask_btn
        global qim
        global category_box
        global left_vboxx
        global current_object
        progress = 0
        #이미지를 보여줄 그래픽스 공간 생성
        self.view = viewer.QViewer()
        self.view.setMouseTracking(True)
        self.view.setInteractive(True)

        # 편의 기능들 생성
        self.btn_group = QButtonGroup()
        self.label_group = QButtonGroup()

        edit_btn = QPushButton("수정(E)")
        edit_btn.setCheckable(True)
        edit_btn.setShortcut("E")
        edit_btn.setToolTip("E")
        edit_btn.clicked.connect(self.edit_mode)
        mask_btn = QPushButton("마스킹(Q)")
        mask_btn.setCheckable(True)
        mask_btn.setShortcut("Q")
        mask_btn.setToolTip("Q")
        mask_btn.clicked.connect(self.mask_mode)
        mask_btn.click()
        move_btn = QPushButton("화면 이동(W)")
        move_btn.setCheckable(True)
        move_btn.setShortcut("W")
        move_btn.setToolTip("W")
        move_btn.clicked.connect(self.move_mode)
        original_size_btn = QPushButton("이미지 리셋(G)")
        original_size_btn.setToolTip("G")
        original_size_btn.setShortcut("G")
        original_size_btn.clicked.connect(self.set_original_size)
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
        category_box = QComboBox()

        #현재 작업할 수 있는 물품들 박스에 추가(mix 제외)
        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(str(i[1]), "SuperCategory")[1]
            if super_name != "mix" and super_name != "background":
                category_box.addItem(i[2] + "/" + super_name)

        #현재 물품과 연관된 모든 오브젝트들 호출(mix 제외)
        cate_info = category_box.currentText().split("/")
        self.current_category = str(self.DB.get_cat_id_SN(cate_info[1], cate_info[0]))

        objects = []
        for i in self.DB.list_table("Grid"):
            if i[1] != 0:
                obj = self.DB.list_obj_CN(str(i[0]), self.current_category, "0")
                if obj == None:
                    obj = []
                else:
                    obj = list(obj)
                if len(obj) != 0:
                    objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)

        self.a = []
        self.b = []
        count = 0

        # 현재 선택된 물품에 해당하는 라벨 생성
        category_name = category_box.currentText()

        RGB = random.choice(self.collect_color)
        self.view.scene.push_color(RGB)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_name)
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()

        #호출된 오브젝트들로 버튼 생성
        for i in btn_names:
            temp_btn = QPushButton(i)
            temp_btn.clicked.connect(self.image_state)
            temp_btn.setCheckable(True)
            if count == 0:
                #temp_btn.click()
                current_object = temp_btn.text()
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if self.DB.get_mask(self.obj_name2id(i)) !=None:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1

        #작업 진행도 표시
        len_a = len(self.a)
        self.progress_state = QLabel("진행도 : " + str(progress) + "/" + str(len_a))
        left_frame = QFrame()

        left_vboxx = QVBoxLayout()
        left_vboxp = QVBoxLayout()

        left_vboxp.addWidget(category_box)
        left_vboxp.addWidget(self.progress_state)
        left_vboxx.addLayout(left_vboxp)
        left_vboxp.addWidget(next_btn)
        left_vboxp.addWidget(before_btn)
        category_box.currentIndexChanged.connect(self.list_change)

        # 진행도 체크박스 기능 연동
        # 오브젝트 버튼은 클릭 시 해당이미지 출력, 체크박스는 현재 진행상태 표시
        for i in range(len_a):
            left_hbox = QHBoxLayout()
            self.b[i].stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(self.b[i])
            left_vboxx.addLayout(left_hbox)

        left_frame.setLayout(left_vboxx)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(left_frame)
        self.vertical_box = QVBoxLayout()
        self.current_object_label = QLabel(current_object)
        self.vertical_box.addWidget(self.current_object_label)
        self.vertical_box.addWidget(category_box)
        self.vertical_box.addWidget(self.progress_state)
        self.vertical_box.addWidget(self.scroll_area)
        self.vertical_box.addWidget(next_btn)
        self.vertical_box.addWidget(before_btn)

        self.btn_group.addButton(edit_btn)
        self.btn_group.addButton(mask_btn)
        self.btn_group.addButton(move_btn)

        self.label_vbox = QVBoxLayout()
        label_box = QGroupBox()
        self.label_vbox.addWidget(self.label_list)
        label_box.setLayout(self.label_vbox)

        vbox = QVBoxLayout()
        vbox.addWidget(edit_btn)
        vbox.addWidget(mask_btn)
        vbox.addWidget(move_btn)
        vbox.addWidget(original_size_btn)
        vbox.addWidget(save_btn)
        vbox.addWidget(label_box)
        right_frame = QFrame()
        right_frame.setLayout(vbox)

        hbox = QHBoxLayout()
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setLayout(self.vertical_box)
        left_splitter = QSplitter(Qt.Horizontal)
        left_splitter.addWidget(vertical_splitter)
        left_splitter.addWidget(self.view)
        left_splitter.addWidget(right_frame)
        left_splitter.setStretchFactor(1, 5)
        hbox.addWidget(left_splitter)

        self.resize(1500, 1000)
        self.setWindowTitle("마스킹")
        self.setLayout(hbox)
        self.show()
        if len(self.a) != 0:
            self.a[0].click()
    def mask_mode(self):
        self.view.scene.mode = 0
        self.view.scene.set_poly_mode(0)
        self.view.setDragMode(QGraphicsView.NoDrag)
    def edit_mode(self):
        self.view.scene.mode = 1
        self.view.scene.set_poly_mode(1)
        self.view.setDragMode(QGraphicsView.NoDrag)
    def move_mode(self):
        self.view.scene.mode = 2
        self.view.scene.set_poly_mode(2)
        if self.sender().isChecked():
            print("on")
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_original_size(self):
        for i in self.a:
            if i.text() == self.current_object_label.text():
                i.click()

    def save_state(self):
        #현재 진행도(체크박스의 체크 개수)를 보여주는 함수
        a = 0
        b = len(self.b)
        for i in range(b):
            if self.b[i].isChecked():
                a = a + 1
        self.progress_state.setText("진행도 : " + str(a) + "/" + str(b))

    def image_state(self):
        #이미지이름을 누르면 해당 이미지가 보이도록 해주는 함수
        global draggin_idx
        global im
        global qim
        global current_object
        global check_state

        #작업상태 및 변수들 초기화
        check_state = 100
        current_object = self.sender().text()
        self.current_object_label.setText(current_object)
        self.view.scene.reset_mask()

        #현재의 오브젝트의 이미지 출력
        img_obj_id = self.obj_name2id(current_object)
        imgd = self.DB.get_table(self.DB.get_table(str(img_obj_id), "Object")[3], "Image")[2]
        self.img_data = np.array(Image.open(BytesIO(imgd)).convert("RGB"))
        qim = QImage(self.img_data, self.img_data.shape[1], self.img_data.shape[0], self.img_data.strides[0],
                     QImage.Format_RGB888)
        im = QPixmap.fromImage(qim)
        self.view.setPhoto(im)
        # 오브젝트와 관련된 비박스가 존재할 경우 마스크 출력
        masks = self.DB.get_mask(img_obj_id)
        if masks != None:
            maskpoint_value = self.XYvalue2maskvalue(masks)
            maskpoint = self.value2qpoints(maskpoint_value)
            self.view.scene.setPoint(maskpoint)
            self.view.scene.mask_show()
        self.update()


    def save_info(self):
        #저장버튼과 연결된 함수, 마스크값을 저장하고, 해당 이미지 비박스 체크
        global current_object
        obj_id = self.obj_name2id(current_object)
        self.DB.delete_mask(obj_id)
        if len(self.view.scene.poly.points) != 0:
            value = self.qpoint2value(self.view.scene.poly.points)
            x, y = self.maskvalue2XYvalue(value)
            for j in range(len(x)):
                self.DB.set_mask(obj_id, x[j], y[j])

            for i in range(len(self.a)):
                if self.a[i].isChecked():
                    self.b[i].setCheckState(Qt.Checked)

    def move_image(self):
        # 다음, 이전이미지로 이동하는 함수
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
        # 변경된 물품의 모든 오브젝트들을 호출하는 함수
        global category_box
        global left_vboxx
        global im
        global qim
        global check_state
        global current_object

        # 변수들 초기화
        progress = 0
        check_state = 100
        self.a = []
        self.b = []
        count = 0
        self.view.scene.reset_mask()

        # 변경된 물품의 라벨 생성
        cate_info = category_box.currentText().split("/")
        RGB = random.choice(self.collect_color)
        self.view.scene.push_color(RGB)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_box.currentText())
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()
        for i in reversed(range(self.label_vbox.count())):
            self.label_vbox.itemAt(i).widget().deleteLater()
        self.label_vbox.addWidget(self.label_list)

        # 변경된 물품과 관련된 모든 오브젝트 호출(mix 제외)
        self.current_category = str(self.DB.get_cat_id_SN(cate_info[1], cate_info[0]))

        objects = []
        for i in self.DB.list_table("Grid"):
            if i[1] != 0:
                obj = self.DB.list_obj_CN(str(i[0]), self.current_category, "0")
                if obj == None:
                    obj = []
                else:
                    obj = list(obj)
                if len(obj) != 0:
                    objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)

        # 호출된 오브젝트들의 버튼 생성
        for i in btn_names:
            temp_btn = QPushButton(i)
            temp_btn.setCheckable(True)
            if count == 0:
                temp_btn.click()
                current_object = temp_btn.text()
                self.current_object_label.setText(current_object)
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if self.DB.get_mask(self.obj_name2id(i)) != None:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1
        len_a = len(self.a)
        self.progress_state.setText("진행도 : " + str(progress) + "/" + str(len_a))

        # 기존의 오브젝트들 제거
        for i in reversed(range(1, left_vboxx.count())):
            left_vboxx.itemAt(i).layout().itemAt(1).widget().deleteLater()
            left_vboxx.itemAt(i).layout().itemAt(0).widget().deleteLater()
            left_vboxx.itemAt(i).layout().deleteLater()

        # 새로 생성된 버튼들 기능 연동
        for i in range(len(self.a)):
            left_hbox = QHBoxLayout()
            self.a[i].clicked.connect(self.image_state)
            self.b[i].stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(self.b[i])
            left_vboxx.addLayout(left_hbox)

        # 변경된 물품의 오브젝트가 1개이상일 경우 첫번째 오브젝트의 이미지 출력
        if len(objects) >= 1:
            first_image_name = self.a[0].text()
            img_obj_id = self.obj_name2id(first_image_name)
            obj_info1 = self.DB.get_table(img_obj_id, "Object")
            img_info1 = self.DB.get_table(str(obj_info1[3]), "Image")
            img = np.array(Image.open(BytesIO(img_info1[2])).convert("RGB"))
            qim = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
            im = QPixmap.fromImage(qim)
            self.view.setPhoto(im)
            #해당 오브젝트의 마스크가 존재할 경우 출력
            if self.DB.get_mask(img_obj_id) != None:
                maskpoint_value = self.XYvalue2maskvalue(self.DB.get_mask(img_obj_id))
                maskpoint = self.value2qpoints(maskpoint_value)
                self.view.scene.setPoint(maskpoint)
                self.view.scene.mask_show()
        self.update()

    def obj_list2name(self, obj_list):
        # 오브젝트 테이블을 받아 버튼 이름 반환
        btn_name_list = []
        for i in range(len(obj_list)):
            # img_id = obj_list[i][0]
            loc_id = obj_list[i][1]
            cate_id = obj_list[i][2]
            # IP 구분이 필요한 경우 사용
            # img = self.DB.get_table(str(img_id), "Image")
            # ip_id = img[0]
            # env = self.DB.get_table(str(ip_id), "Environment")
            # ipv4 = env[1]

            loc = self.DB.get_table(str(loc_id), "Location")
            location_str = str(loc[2]) + "x" + str(loc[3])
            grid = self.DB.get_table(str(loc[1]), "Grid")
            grid_str = str(grid[1]) + "x" + str(grid[2])

            cate = self.DB.get_table(str(cate_id), "Category")
            cate_str = cate[2]
            super_cate = self.DB.get_table(str(cate[1]), "SuperCategory")
            super_cate_str = super_cate[1]

            btn_name = cate_str + "/" + super_cate_str + "_" + location_str + "/" + grid_str + "_" + str(obj_list[i][4])
            btn_name_list.append(btn_name)
        return btn_name_list

    def obj_name2id(self, i):
        # 버튼이름을 참조하여 오브젝트 아이디를 반환해주는 함수
        # 아래 주석이 함수의 예시
        # i = "콜라/음료_1x2/3x3_1"
        i = i.split("_")  # "콜라/음료", "1x2/3x3", "1"
        i[0] = i[0].split("/")  # "콜라" "음료" "1x2" "3x3", "1"
        i[1] = i[1].split("/")

        cate_id = self.DB.get_cat_id_SN(i[0][1], i[0][0])
        loc_id = str(self.DB.get_loc_id_GL(i[1][1], i[1][0]))
        obj_id = self.DB.get_obj_id_from_args(loc_id, str(cate_id), i[2], "-1", "-1")

        return str(obj_id)

    def maskvalue2XYvalue(self, maskvalue):
        #마스크의 포인트 들을 x, y좌표로 분리하는 함수
        x = []
        y = []
        for i in maskvalue:#[[12,15],[124,235],[123,22], [124,1235]]
            x.append(i[0])
            y.append(i[1])
        return x, y

    def XYvalue2maskvalue(self, mask_table):
        #x, y로 분리된 좌표들을 점들로 만드는 함수
        maskvalue = []

        mask_table = sorted(mask_table)

        for i in mask_table:
            maskvalue.append([i[1], i[2]])
        return maskvalue

    def value2qpoints(self, maskpoint_value):
        #int값을 Qpoint 값으로 변환하는 함수
        maskpoint = []

        for i in maskpoint_value:
            maskpoint.append(QPointF(i[0], i[1]))
        return maskpoint

    def qpoint2value(self, points):
        value = []
        for i in points:
             value.append([i.x(), i.y()])
        return value

