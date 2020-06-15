from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import random
import DB
from io import BytesIO
from PIL import Image
import copy
#그래픽스 클래스에서도 참조해야할 변수들 글로벌로 선언

global check_state
global view # 이미지 보여주는 공간
global scale_factor_w #이미지 확대, 축소 배율
global edit_btn # 수정 버튼
global draggin_idx # 드래그 작업 참조 변수
global maskpoint_group # 마스크 값들
global minimum_mask #
global mask_btn # 마스킹 버튼
global maskpoint # 마스크 값(QPoint)
global maskpoint_value # 마스크 값 (lsit)
global qp # QPainter
global scene # 이미지 보여주는 공간
global im # 마스크를 포함한 이미지
global pen # 마스크 포인트 그리는 펜
global brush # 마스크 채우는 붓
global mask_num # 선택된 마스크의 순서
global maskpoint_value_group # 마스크 값들(list)
global label_color # pen 색
global fill_color # brush 색
global qim # 마스크 없는 원 이미지
global line_pen # 마스크 선 그리는 펜
global label_line_color # line_pen 색
global label_name #라벨 이름
#global current_label # 선택된 마스크의 라벨
global color_value # 색의 실제 값
global category_box
global left_vboxx
global current_object

class mask(QWidget):
    #라벨들을 입력으로 받아서 라벨의 고유 색을 설정
    def __init__(self, db):
        super().__init__()
        self.DB = db
        global scale_factor_w
        global draggin_idx
        global maskpoint_group
        global mask_num
        global maskpoint
        global maskpoint_value
        global maskpoint_value_group
        global fill_color
        global label_color
        global label_line_color
        global label_name
        global color_value
        global check_state
        global qim

        check_state = 100


        scale_factor_w = 1 # 이미지 사이즈의 배율이므로 1로 초기화
        mask_num = 1000000 # 마스크 개수의 초기값
        maskpoint = []
        maskpoint_value = []
        draggin_idx = -1
        maskpoint_group = []
        maskpoint_value_group = []
        color_value = []
        self.label_list = []
        label_color = []
        label_line_color = []
        fill_color = []
        qim = []

        #라벨 개수에 맞도록 랜덤으로 색을 생성해서 라벨별로 색 부여
        # for i in label:
        #     color_value.append(random.sample(range(0, 255), 3))
        #     back_label_color = "background-color: " + QColor(color_value[k][0], color_value[k][1], color_value[k][2]).name()
        #     self.label_list.append(QRadioButton(i))
        #     self.label_list[k].clicked.connect(self.color_select)
        #     self.label_list[k].setStyleSheet(back_label_color)
        #     k = k + 1
        # self.label_list[0].toggle()
        # self.color_select()

    def masking(self):

        global view
        global edit_btn
        global scene
        global im
        global mask_btn
        global qim
        #global current_label
        global category_box
        global left_vboxx
        global pen
        global brush
        global line_pen
        global current_object
        progress = 0
        #이미지를 보여줄 그래픽스 공간 생성
        scene = QGraphicsScene()
        view = tracking_screen(scene)
        view.setMouseTracking(True)
        view.setInteractive(True)

        # 편의 기능들 생성
        self.btn_group = QButtonGroup()
        self.label_group = QButtonGroup()

        edit_btn = QPushButton("수정")
        edit_btn.setCheckable(True)
        edit_btn.setShortcut("E")
        edit_btn.setToolTip("E")
        mask_btn = QPushButton("마스킹")
        mask_btn.setCheckable(True)
        mask_btn.setShortcut("M")
        mask_btn.setToolTip("M")
        mask_btn.toggle()
        original_size_btn = QPushButton("기본크기")
        original_size_btn.setToolTip("G")
        original_size_btn.setShortcut("G")
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
        #current_label = QLineEdit()
        category_box = QComboBox()

        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if super_name != "mix":
                category_box.addItem(i[2] + "/" + super_name)

        self.a = []
        self.b = []
        count = 0

        cate_info = category_box.currentText().split("/")
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

        for i in btn_names:

            temp_btn = QPushButton(i)
            temp_btn.setCheckable(True)
            if count == 0:
                temp_btn.toggle()
                current_object = temp_btn.text()
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if len(self.DB.mask_info(self.obj_name2id(i))) != 0:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1


        category_name = category_box.currentText()

        RGB = random.sample(range(0, 255), 3)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_name)
        self.label_list.clicked.connect(self.color_select)
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()
        pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 6)
        line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 2)
        brush = QBrush(QColor(RGB[0], RGB[1], RGB[2]), Qt.Dense3Pattern)

        len_a = len(self.a)
        self.progress_state = QLabel("진행도 : " + str(progress) + "/" + str(len_a))
        left_frame = QFrame()

        left_vboxx = QVBoxLayout()
        left_vboxp = QVBoxLayout()
        #left_vboxp.addWidget(label_label)
        left_vboxp.addWidget(next_btn)
        left_vboxp.addWidget(before_btn)
        #left_vboxp.addWidget(current_label)
        left_vboxp.addWidget(category_box)
        left_vboxp.addWidget(self.progress_state)
        left_vboxx.addLayout(left_vboxp)
        category_box.currentIndexChanged.connect(self.list_change)



        for i in range(len_a):
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
        label_box = QGroupBox()
        self.label_vbox.addWidget(self.label_list)
        label_box.setLayout(self.label_vbox)

        if len(objects) >= 1:
            first_image_name = self.a[0].text()
            first_obj_id = self.obj_name2id(first_image_name)
            obj_info = self.DB.get_table(first_obj_id, "Object")
            img_info = self.DB.get_table(str(obj_info[0]), "Image")
            img = np.array(Image.open(BytesIO(img_info[2])).convert("RGB"))
            qp = QPainter()
            qim = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
            w = qim.width()
            h = qim.height()
            im = QPixmap.fromImage(qim)
            qp.begin(im)
            if self.DB.mask_info(first_obj_id) != None:
                maskpoint_value = self.XYvalue2maskvalue(self.DB.mask_info(first_obj_id))
                maskpoint = self.value2qpoints(maskpoint_value)
                qp.setPen(line_pen)
                qp.setBrush(QBrush(Qt.transparent))
                qp.drawPolygon(QPolygon(maskpoint))
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
        vbox.addWidget(label_box)
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
        self.setWindowTitle("마스킹")
        self.setLayout(hbox)
        self.show()


    def color_select(self):
        k = 0
        global pen
        global brush
        global line_pen
        global color_value

        for i in self.label_list:
            if i.isChecked():
                pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 6)
                line_pen = QPen(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), 2)
                brush = QBrush(QColor(color_value[k][0], color_value[k][1], color_value[k][2]), Qt.Dense3Pattern)
            k = k + 1


    def set_original_size(self):
        # 이미지를 원래 크기로 되돌리는 버튼과 연결된 함수
        global scale_factor_w
        global maskpoint_group
        global qp
        global mask_num
        global scene
        global im
        global fill_color
        global label_color
        global maskpoint

        scale_factor_w = 1
        qp = QPainter()
        im.setDevicePixelRatio(scale_factor_w)
        qp.begin(im)
        qp.setPen(line_pen)
        qp.setBrush(QBrush(Qt.transparent))
        qp.drawPolygon(QPolygon(maskpoint))
        qp.end()
        w = im.width()
        h = im.height()
        scene.clear()
        scene.addPixmap(im)
        view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        scene.update()

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
        global scale_factor_w
        global draggin_idx
        global maskpoint_group
        global mask_num
        global maskpoint
        global maskpoint_value
        global maskpoint_value_group
        global fill_color
        global label_color
        global label_line_color
        global im
        global qim
        global current_object
        global check_state
        check_state = 100

        current_object = self.sender().text()
        print("현재 오브젝트 이미지 이름 : " + current_object)
        scale_factor_w = 1
        mask_num = 1000000
        maskpoint = []
        maskpoint_value = []
        draggin_idx = -1
        maskpoint_group = []
        maskpoint_value_group = []
        label_color = []
        label_line_color = []
        fill_color = []

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

        if self.DB.mask_info(img_obj_id) != None:
            maskpoint_value = self.XYvalue2maskvalue(self.DB.mask_info(img_obj_id))
            maskpoint = self.value2qpoints(maskpoint_value)
            qp.setPen(line_pen)
            qp.setBrush(QBrush(Qt.transparent))
            qp.drawPolygon(QPolygon(maskpoint))
        qp.end()
        scene.clear()
        scene.addPixmap(im)
        view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        scene.update()

    def save_info(self):
        #저장버튼과 연결된 함수, 마스크값을 저장하고, 해당 이미지에 작업이 완료됬다는 체크표시를 해줌
        global current_object
        global maskpoint_value

        obj_id = self.obj_name2id(current_object)
        print(obj_id)

        self.DB.delete_mask_from_obj_id(obj_id)
        if len(maskpoint_value) != 0:
            x, y = self.maskvalue2XYvalue(maskpoint_value)
            for j in range(len(x)):
                self.DB.set_mask(obj_id, x[j], y[j])

            for i in range(len(self.a)):
                if self.a[i].isChecked():
                    self.b[i].setCheckState(Qt.Checked)

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
        global line_pen
        global brush
        global im
        global qim
        global maskpoint
        global maskpoint_value
        global check_state
        global current_object
        progress = 0
        check_state = 100
        self.a = []
        self.b = []
        count = 0

        cate_info = category_box.currentText().split("/")

        RGB = random.sample(range(0, 255), 3)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_box.currentText())
        self.label_list.clicked.connect(self.color_select)
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()
        pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 6)
        line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 2)
        brush = QBrush(QColor(RGB[0], RGB[1], RGB[2]), Qt.Dense3Pattern)
        for i in reversed(range(self.label_vbox.count())):
            self.label_vbox.itemAt(i).widget().deleteLater()
        self.label_vbox.addWidget(self.label_list)


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

        for i in btn_names:
            temp_btn = QPushButton(i)
            temp_btn.setCheckable(True)
            if count == 0:
                temp_btn.toggle()
                current_object = temp_btn.text()
            self.label_group.addButton(temp_btn)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if len(self.DB.mask_info(self.obj_name2id(i))) != 0:
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
            first_image_name = self.a[0].text()
            img_obj_id = self.obj_name2id(first_image_name)
            obj_info1 = self.DB.get_table(img_obj_id, "Object")
            img_info1 = self.DB.get_table(str(obj_info1[0]), "Image")
            img = np.array(Image.open(BytesIO(img_info1[2])).convert("RGB"))
            qp = QPainter()
            qim = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
            w = qim.width()
            h = qim.height()
            im = QPixmap.fromImage(qim)
            qp.begin(im)
            if self.DB.mask_info(img_obj_id) != None:
                maskpoint_value = self.XYvalue2maskvalue(self.DB.mask_info(img_obj_id))
                maskpoint = self.value2qpoints(maskpoint_value)
                qp.setPen(line_pen)
                qp.setBrush(QBrush(Qt.transparent))
                qp.drawPolygon(QPolygon(maskpoint))
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

    def maskvalue2XYvalue(self, maskvalue):
        x = []
        y = []
        for i in maskvalue:#[[12,15],[124,235],[123,22], [124,1235]]
            x.append(i[0])
            y.append(i[1])
        return x, y
    def XYvalue2maskvalue(self, mask_table):
        maskvalue = []

        mask_table = sorted(mask_table)

        for i in mask_table:
            maskvalue.append([i[1], i[2]])
        return maskvalue
    def value2qpoints(self, maskpoint_value):
        maskpoint = []

        for i in maskpoint_value:
            maskpoint.append(QPoint(i[0], i[1]))
        return maskpoint



class tracking_screen(QGraphicsView):
    #그래픽스(이미지를 보여주는 공간)의 마우스 함수를 커스터마이징 하기위해 만든 새로운 클래스

    def mouseMoveEvent(self, e):
        #마우스가 움직일 때, 일어나는 이벤트
        global scale_factor_w
        global view
        global draggin_idx
        global maskpoint_group
        global minimum_mask
        global edit_btn
        global qp
        global im
        global label_color
        global fill_color
        global qim
        global label_line_color
        global maskpoint
        global scene
        global check_state

        #마우스 위치를 확대, 축소된 이미지에 맞도록 변환
        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        if qim != []:
            w = qim.width()
            h = qim.height()
        #수정 작업 중 드래그 했을 때, 점과 선이 실시간으로 갱신되도록 설정
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods) and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x()/scale_factor_w, e.y()/scale_factor_w, w, h), Qt.KeepAspectRatio)
        else:
            if mask_btn.isChecked():
                if check_state == 30:
                    temp_maskpoint = copy.deepcopy(maskpoint)
                    temp_maskpoint.append(QPoint(x, y))
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)

                    qp.setPen(pen)
                    qp.drawPoints(QPolygon(temp_maskpoint))
                    qp.setPen(line_pen)
                    qp.drawPolyline(QPolygon(temp_maskpoint))
                    qp.end()
                    scene.addPixmap(im)

            if edit_btn.isChecked():
                if draggin_idx != -1:

                    maskpoint[draggin_idx] = QPoint(x, y)
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)

                    qp.setPen(pen)
                    qp.drawPoints(QPolygon(maskpoint))
                    qp.setPen(line_pen)
                    qp.drawPolygon(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)

    def mouseReleaseEvent(self, e):
        #마우스가 클릭됬다가 떨어질 때 발생하는 이벤트
        global view
        global scale_factor_w
        global draggin_idx
        global maskpoint_group
        global minimum_mask
        global edit_btn
        global qp
        global im
        global mask_num
        global label_color
        global fill_color
        global qim
        global label_line_color
        global maskpoint_value_group
        global maskpoint
        global maskpoint_value
        global scene
        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods) and e.buttons() == Qt.LeftButton:
            print("nothing")
        else:
            #수정 작업중일 때, 마우스가 때지면 최종 수정된 마스크 값으로 마스크 값을 갱신
            if edit_btn.isChecked():
                if e.button() == Qt.LeftButton and draggin_idx != -1:
                    maskpoint_value[draggin_idx] = [x, y]
                    maskpoint[draggin_idx] = QPoint(x, y)

                    draggin_idx = -1
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)

                    qp.setBrush(QBrush(Qt.transparent))
                    qp.setPen(line_pen)
                    qp.drawPolygon(QPolygon(maskpoint))
                    qp.setPen(pen)
                    qp.drawPoints(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)


    def wheelEvent(self, ev):
        global scene

        #휠이 움직일때 발생하는 이벤트
        mods = ev.modifiers()
        delta = ev.angleDelta()

        global scale_factor_w
        global qp
        global im
        global qim
        global view

        #ctrl+휠을 하면 이미지의 사이즈가 확대, 축소 되도록 수정

        if Qt.ControlModifier == int(mods):
            qp = QPainter()
            qp.begin(im)
            #확대, 축소비율 설정 휠이 한번 움직일때마다 10%씩 작아지거나 커짐, 최소, 최대 크기는 0.5배에서 4배로 설정
            if delta.y() > 0 and scale_factor_w > 0.25:
                scale_factor_w = scale_factor_w * 0.9
            elif scale_factor_w < 2 and delta.y() < 0:
                scale_factor_w = scale_factor_w * 1.1

            im.setDevicePixelRatio(scale_factor_w)
            qp.end()
            scene.clear()
            scene.addPixmap(im)
            #scene.setTransform(QTransform.translate(ev.x(), ev.y()))
            w = qim.width()
            h = qim.height()
            view.fitInView(QRectF(ev.x() / scale_factor_w, ev.y() / scale_factor_w, w, h), Qt.KeepAspectRatio)


    def mousePressEvent(self, e):
        #마우스를 클릭했을 때, 발생하는 이벤트트
        global view
        global scale_factor_w
        global maskpoint_group
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
        #global current_label
        global color_value
        global maskpoint_value
        global maskpoint
        global check_state
        global qim
        x = (view.mapToScene(e.pos()).x()) * scale_factor_w
        y = (view.mapToScene(e.pos()).y()) * scale_factor_w
        w = qim.width()
        h = qim.height()
        mods = e.modifiers()
        if Qt.ControlModifier == int(mods) and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x()/scale_factor_w, e.y()/scale_factor_w, w, h), Qt.KeepAspectRatio)
        else:
            #마스킹 작업 중 이벤트
            if mask_btn.isChecked():
                #좌클릭시 포인트 생성 및 선 생성

                if e.buttons() == Qt.LeftButton and check_state == 100:
                    maskpoint.append(QPoint(x, y))
                    maskpoint_value.append([x, y])
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(pen)
                    qp.drawPoint(x, y)
                    qp.setPen(line_pen)
                    qp.drawPolyline(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)
                    check_state = 30

                elif e.buttons() == Qt.LeftButton and check_state == 30:
                    maskpoint.append(QPoint(x, y))
                    maskpoint_value.append([x, y])
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(pen)
                    qp.drawPoint(x, y)
                    qp.setPen(line_pen)
                    qp.drawPolyline(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)

                elif e.buttons() == Qt.LeftButton and check_state == 10:
                    print("here")
                    maskpoint = []
                    maskpoint_value = []
                    maskpoint.append(QPoint(x, y))
                    maskpoint_value.append([x, y])
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    qp.setPen(pen)
                    qp.drawPoint(x, y)
                    qp.setPen(line_pen)
                    qp.drawPolyline(QPolygon(maskpoint))
                    qp.end()
                    scene.clear()
                    scene.addPixmap(im)
                    check_state = 30

                #우클릭시 최종 마스크 생성
                elif e.buttons() == Qt.RightButton:
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(line_pen)

                    qp.drawPolygon(QPolygon(maskpoint))
                    qp.end()

                    scene.addPixmap(im)

                    maskpoint_group.append(maskpoint)
                    label_color.append(pen)
                    label_line_color.append(line_pen)
                    fill_color.append(brush)
                    maskpoint_value_group.append(maskpoint_value)
                    check_state = 10



            #수정 작업중 발생하는 이벤트
            #클릭위치와 가장 가까운 점을 계산하여 해당 포인트를 마우스 위치로 수정
            if edit_btn.isChecked():
                if len(maskpoint_value) != 0:
                    if e.buttons() == Qt.LeftButton and draggin_idx == -1:
                        point = [x, y]
                        dist = np.array(maskpoint_value) - np.array(point)
                        dist = np.array(dist[:, 0] ** 2 + dist[:, 1] ** 2)
                        minimum_mask = dist.argmin()
                        min_dist = np.array(maskpoint_value) - np.array(point)
                        min_dist = np.array(min_dist[:, 0] ** 2 + min_dist[:, 1] ** 2)
                        minimum_value = min_dist.argmin()

                        #마우스 위치와 포인트의 위치 사이의 거리가 1000이상일 경우 작업x
                        if min(min_dist) < 1000:
                            draggin_idx = minimum_value


                #마스크내부에 클릭이 됬을 경우 해당 마스크를 색칠

                if QPolygon(maskpoint).containsPoint(QPoint(x, y), Qt.OddEvenFill) and e.buttons() == Qt.LeftButton:

                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.setBrush(brush)
                    qp.drawPolygon(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)
                    #아래 for문 때문에 첫번째 마스크 클릭시 첫번째 마스크가 투명해지는 현상 발생
                    #현재 마스크가 어떤 마스크인지 좌측에 표시해주는 코드

                else:
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.setBrush(QBrush(Qt.transparent))
                    qp.drawPolygon(QPolygon(maskpoint))
                    qp.end()
                    scene.addPixmap(im)
