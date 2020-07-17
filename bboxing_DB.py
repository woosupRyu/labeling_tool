from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import random
from io import BytesIO
from PIL import Image

# 그래픽스 클래스에서도 참조해야할 변수들 글로벌로 선언
global sig
global view  # 이미지 보여주는 공간
global scale_factor_w  # 이미지 확대, 축소 배율
global edit_btn  # 수정 버튼
global draggin_idx  # 드래그 작업 참조 변수

global minimum_mask  #
global mask_btn  # 마스킹 버튼
global qp  # QPainter
global scene  # 이미지 보여주는 공간
global im  # 마스크를 포함한 이미지
global mask_num  # 선택된 마스크의 순서
global qim  # 마스크 없는 원 이미지
global line_pen  # 마스크 선 그리는 펜
global label_name  # 라벨 이름
global color_value  # 색의 실제 값
global coordinates # 비박스 정보
global category_box # 물품선택 박스
global left_vboxx #
global current_object # 현재 선택된 오브젝트

class bbox(QWidget):
    def __init__(self,  db):
        super().__init__()

        self.DB = db
        global scale_factor_w
        global draggin_idx
        global mask_num
        global label_name
        global color_value
        global coordinates
        global qim
        global sig
        global current_object

        current_object = ""

        #변수들 초기화
        self.collect_color = [[255, 0, 0], [255, 255, 0], [0, 255, 255], [0, 255, 0], [255, 0, 255]]
        scale_factor_w = 1
        mask_num = 1000000
        draggin_idx = -1
        coordinates = []

        color_value = []
        self.label_list = []
        qim = []
        sig = 0

    def bboxing(self):

        global view
        global edit_btn
        global scene
        global im
        global mask_btn
        global qim
        global category_box
        global left_vboxx
        global line_pen
        global current_object
        global coordinates
        progress = 0
        # 이미지를 보여줄 그래픽스 공간 생성
        scene = QGraphicsScene()
        view = tracking_screen(scene)
        view.setMouseTracking(True)

        # 기본 기능 버튼 생성
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
        original_size_btn = QPushButton("기본크기(G)")
        original_size_btn.setShortcut("G")
        original_size_btn.setToolTip("G")
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

        #물품선택 박스에 선택 가능한 물품 추가(mix 제외)
        category_box = QComboBox()
        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(str(i[0]), "SuperCategory")[1]
            if super_name != "mix" and super_name != "background":
                category_box.addItem(i[2] + "/" + super_name)

        #현재 선택된 물품의 모든 오브젝트 호출(mix 제외)
        cate_info = category_box.currentText().split("/")
        self.current_category = str(self.DB.get_cat_id(cate_info[0], cate_info[1]))
        objects = []
        for i in self.DB.list_table("Grid"):
            if i[1] != 0:
                obj = self.DB.list_obj_check_num(str(i[0]), self.current_category, "0")
                if obj != None:
                    obj = list(obj)
                    objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)


        #현재 오브젝트의 라벨 표시
        category_name = category_box.currentText()

        RGB = random.choice(self.collect_color)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_name)
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()
        line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 4)
        #호출한 오브젝트들을 호출할 수 있는 버튼 및 작업상태박스 생성
        self.a = []
        self.b = []
        count = 0

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
            if self.DB.get_bbox_info(self.obj_name2id(i)) != None:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)
            count = count + 1

        #작업 진행도 표시
        len_a = len(self.a)
        self.progress_state = QLabel("진행도 : " + str(progress) + "/" + str(len_a))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        #윈도우에 기능 배치
        self.left_frame = QFrame()

        left_vboxx = QVBoxLayout()
        category_box.currentIndexChanged.connect(self.list_change)

        #생성한 버튼들과 기능들 연동
        for i, info in enumerate(self.b):
            left_hbox = QHBoxLayout()
            #self.a[i].clicked.connect(self.image_state)
            info.stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(info)
            left_vboxx.addLayout(left_hbox)

        self.left_frame.setLayout(left_vboxx)

        scroll_area.setWidget(self.left_frame)
        self.vertical_box = QVBoxLayout()
        self.current_object_label = QLabel(current_object)
        self.vertical_box.addWidget(self.current_object_label)
        self.vertical_box.addWidget(category_box)
        self.vertical_box.addWidget(self.progress_state)
        self.vertical_box.addWidget(scroll_area)
        self.vertical_box.addWidget(next_btn)
        self.vertical_box.addWidget(before_btn)

        #상호베타적 버튼 설정
        self.btn_group.addButton(edit_btn)
        self.btn_group.addButton(mask_btn)

        self.label_vbox = QVBoxLayout()
        label_box = QGroupBox()
        self.label_vbox.addWidget(self.label_list)
        label_box.setLayout(self.label_vbox)

        #기능들 윈도우에 세팅
        vbox = QVBoxLayout()
        vbox.addWidget(edit_btn)
        vbox.addWidget(mask_btn)
        vbox.addWidget(original_size_btn)
        vbox.addWidget(save_btn)
        vbox.addWidget(label_box)
        right_frame = QFrame()
        right_frame.setLayout(vbox)

        # view_vbox = QVBoxLayout()
        # view_vbox.addWidget(self.current_object_label)

        hbox = QHBoxLayout()
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setLayout(self.vertical_box)
        left_splitter = QSplitter(Qt.Horizontal)
        left_splitter.addWidget(vertical_splitter)
        left_splitter.addWidget(view)
        left_splitter.addWidget(right_frame)
        left_splitter.setStretchFactor(1, 5)
        hbox.addWidget(left_splitter)

        self.resize(1500, 1000)
        self.setWindowTitle("비박싱")
        self.setLayout(hbox)
        self.show()
        if len(self.a) != 0:
            self.a[0].click()

    def set_original_size(self):
        # 이미지를 원래 크기로 되돌리는 버튼과 연결된 함수
        global scale_factor_w
        global qp
        global mask_num
        global scene
        global im
        global coordinates

        #이미지 배율을 1로 설정 후 다시 이미지 생성
        scale_factor_w = 1
        qp = QPainter()
        im.setDevicePixelRatio(scale_factor_w)
        qp.begin(im)
        if len(coordinates) != 0:
            qp.setPen(line_pen)
            qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))

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
        # 오브젝트 버튼을 누르면 해당 이미지가 보이도록 해주는 함수
        global scale_factor_w
        global draggin_idx
        global mask_num
        global im
        global qim
        global coordinates
        global current_object

        scale_factor_w = 1
        mask_num = 1000000
        draggin_idx = -1

        coordinates = []

        #현재 오브젝트와 연관된 이미지 표시
        current_object = self.sender().text()
        self.current_object_label.setText(current_object)

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

        #해당 오브젝트에 연관된 비박스가 있는 경우 비박스 표시
        po = self.DB.get_bbox_info(img_obj_id)
        if po != None:
            if len(sum(po, ())) != 0:
                coordinates = self.bbox2coordinate(self.DB.get_table(str(self.DB.get_bbox_id(img_obj_id))[1:-2], "Bbox"))
                qp.setPen(line_pen)
                qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
        qp.end()
        scene.clear()
        scene.addPixmap(im)
        view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        scene.update()
        self.update()

    def save_info(self):
        # 저장버튼과 연결된 함수, 마스크값을 저장하고, 해당 이미지에 작업이 완료됬다는 체크표시를 해줌
        global current_object
        global coordinates
        global scale_factor_w
        obj_id = self.obj_name2id(current_object)
        #해당된 오브젝트에 존재하는 비박스를 지운 후 현재 비박스 추가
        if scale_factor_w > 1:
            self.DB.delete_bbox(obj_id)
            if len(coordinates) != 0:
                box_info = self.coordinate2bbox(coordinates)
                self.DB.set_bbox(obj_id, box_info[0] * scale_factor_w, box_info[1] * scale_factor_w, box_info[2] * scale_factor_w, box_info[3] * scale_factor_w)

                for i, info in enumerate(self.a):
                    if info.isChecked():
                        self.b[i].setCheckState(Qt.Checked)
        else:
            self.DB.delete_bbox(obj_id)
            if len(coordinates) != 0:
                box_info = self.coordinate2bbox(coordinates)
                self.DB.set_bbox(obj_id, box_info[0], box_info[1], box_info[2], box_info[3])

                for i, info in enumerate(self.a):
                    if info.isChecked():
                        self.b[i].setCheckState(Qt.Checked)

    def move_image(self):
        #다음, 이전 이미지로 이동하는 버튼과 연동된 함수
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
        # 선택된 물품이 바뀔 경우 바뀐 물품의 오브젝트 리스트를 호출하는 함수
        global category_box
        global left_vboxx
        global line_pen
        global im
        global qim
        global current_object
        global coordinates

        coordinates = []
        progress = 0 #불러온 오브젝트들 중 bbox작업이 완료된 오브젝트들의 개수를 저장하는 변수
        self.a = []
        self.b = []

        cate_info = category_box.currentText().split("/")

        # 바뀐 물품의 라벨 추가 및 색 설정
        RGB = random.choice(self.collect_color)
        back_label_color = "background-color: " + QColor(RGB[0], RGB[1], RGB[2]).name()
        self.label_list = QRadioButton(category_box.currentText())
        self.label_list.setStyleSheet(back_label_color)
        self.label_list.toggle()
        line_pen = QPen(QColor(RGB[0], RGB[1], RGB[2]), 4)
        for i in reversed(range(self.label_vbox.count())):
            self.label_vbox.itemAt(i).widget().deleteLater()
        self.label_vbox.addWidget(self.label_list)
        self.current_category = str(self.DB.get_cat_id(cate_info[0], cate_info[1]))

        #바뀐 물품과 관련된 오브젝트들 호출 및 버튼생성(mix제외)
        objects = []
        for i in self.DB.list_table("Grid"):
            if i[1] != 0:
                obj = self.DB.list_obj_check_num(str(i[0]), self.current_category, "0")
                if obj != None:
                    obj = list(obj)
                    objects.append(obj)
        objects = sum(objects, [])
        btn_names = self.obj_list2name(objects)

        for i, info in enumerate(btn_names):
            temp_btn = QPushButton(info)
            temp_btn.clicked.connect(self.image_state)
            temp_btn.setCheckable(True)
            self.label_group.addButton(temp_btn)
            if i == 0:
                temp_btn.click()
                current_object = btn_names[0]
                current_object = temp_btn.text()
                self.current_object_label.setText(current_object)
            self.a.append(temp_btn)
            tem_box = QCheckBox()
            if self.DB.get_bbox_info(self.obj_name2id(info)) != None:
                tem_box.toggle()
                progress = progress + 1
            self.b.append(tem_box)

        # 진행도 갱신
        len_a = len(self.a)
        self.progress_state.setText("진행도 : " + str(progress) + "/" + str(len_a))

        #바뀌기 전의 오브젝트들을 삭제
        for i in reversed(range(0, left_vboxx.count())):
            left_vboxx.itemAt(i).layout().itemAt(0).widget().deleteLater()
            left_vboxx.itemAt(i).layout().itemAt(1).widget().deleteLater()
            left_vboxx.itemAt(i).layout().deleteLater()

        #바뀐 후의 오브젝트들(버튼 및 박스) 추가
        for i, info in enumerate(self.b):
            left_hbox = QHBoxLayout()
            info.stateChanged.connect(self.save_state)
            left_hbox.addWidget(self.a[i])
            left_hbox.addWidget(info)
            left_vboxx.addLayout(left_hbox)
        self.update()
        #오브젝트가 존재할 경우 이미지 표시
        # if len(objects) >= 1:
        #     img_obj_id = self.obj_name2id(current_object)
        #
        #     imgd = self.DB.get_table(self.DB.get_table(str(img_obj_id), "Object")[0], "Image")[2]
        #     self.img_data = np.array(Image.open(BytesIO(imgd)).convert("RGB"))
        #
        #     qim = QImage(self.img_data, self.img_data.shape[1], self.img_data.shape[0], self.img_data.strides[0],
        #                  QImage.Format_RGB888)
        #     w = qim.width()
        #     h = qim.height()
        #     im = QPixmap.fromImage(qim)
        #
        #     qp = QPainter()
        #     im.setDevicePixelRatio(scale_factor_w)
        #     qp.begin(im)
        #
        #     # 현재 오브젝트와 연관된 bbox가 존재할 경우 표시
        #     po = self.DB.get_bbox_info(img_obj_id)
        #     if po != None:
        #         if len(sum(po, ())) != 0:
        #             coordinates = self.bbox2coordinate(self.DB.get_table(str(self.DB.get_bbox_id(img_obj_id))[1:-2], "Bbox"))
        #             qp.setPen(line_pen)
        #             qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
        #     qp.end()
        #     scene.clear()
        #     scene.addPixmap(im)
        #     view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        #     scene.update()


    def obj_list2name(self, obj_list):
        #오브젝트 테이블을 받아 버튼 이름 반환
        btn_name_list = []
        for i in obj_list:
            #img_id = obj_list[i][0]
            loc_id = i[1]
            cate_id = i[2]
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

            btn_name = cate_str + "/" + super_cate_str + "_" + location_str + "/" + grid_str + "_" + str(i[4])
            btn_name_list.append(btn_name)
        return btn_name_list

    def obj_name2id(self, i):
        # 버튼이름을 참조하여 오브젝트 아이디를 반환해주는 함수
        # 아래 주석이 함수의 예시
        # i = "콜라/음료_1x2/3x3_1"
        i = i.split("_")  # "콜라/음료", "1x2/3x3", "1"
        i[0] = i[0].split("/")  # "콜라" "음료" "1x2" "3x3", "1"
        i[1] = i[1].split("/")

        cate_id = self.DB.get_cat_id(i[0][0], i[0][1])
        loc_id = str(self.DB.get_loc_id_GL(i[1][1], i[1][0]))[1:-2]
        obj_id = self.DB.get_obj_id_from_args(loc_id, str(cate_id), i[2], "-1")

        return str(obj_id)

    def coordinate2bbox(self, coordinate):
        # 비박스의 네 점의 좌표를 받아 x, y, w, h형식으로 변환
        bbox = []
        bbox.append(coordinate[0][0])
        bbox.append(coordinate[0][1])
        bbox.append(abs(coordinate[0][0] - coordinate[1][0]))
        bbox.append(abs(coordinate[0][1] - coordinate[2][1]))
        return bbox

    def bbox2coordinate(self, bbox):
        # 비박스의 x, y, w, h를 받아 네 점의 좌표를 반환
        coor = [[bbox[2], bbox[3]], [bbox[2] + bbox[4], bbox[3]], [bbox[2], bbox[3] + bbox[5]], [bbox[2] + bbox[4], bbox[3] + bbox[5]]]
        return coor



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
        global qim
        global pen
        global line_pen

        # 마우스 위치를 확대, 축소된 이미지에 맞도록 변환
        if scale_factor_w <= 1:
            x = view.mapToScene(e.pos()).x() * scale_factor_w
            y = view.mapToScene(e.pos()).y() * scale_factor_w
        else:
            x = view.mapToScene(e.pos()).x()
            y = view.mapToScene(e.pos()).y()
        if qim != []:
            w = im.width()
            h = im.height()

        # Ctrl + 마우스드래그를 할 경우, 화면이 이동
        if sig == 1 and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x()/scale_factor_w, e.y()/scale_factor_w, w, h), Qt.KeepAspectRatio)
        else:
            # 비박싱 작업 중 드래그 했을 때, 점과 선이 실시간으로 갱신되도록 설정
            if mask_btn.isChecked():
                if draggin_idx == 10:# 비박싱 작업중인 경우 draggin_inx = 10 아닐경우 -1
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(self.start_point.x(), self.start_point.y(), x - self.start_point.x(), y - self.start_point.y()))
                    qp.end()
                    scene.addPixmap(im)
            # 수정 작업 중 드래그 했을 때, 점과 선이 실시간으로 갱신되도록 설정
            if edit_btn.isChecked():
                # 특정 포인트가 선택된 경우에만 수정되도록 설정
                if draggin_idx != -1:
                    qp = QPainter()
                    im = QPixmap.fromImage(qim)
                    im.setDevicePixelRatio(scale_factor_w)
                    qp.begin(im)
                    qp.setPen(line_pen)

                    # 선택된 포인트가 1번째 꼭지점인 경우
                    if draggin_idx == 0:
                        qp.drawRect(QRect(x, y, coordinates[3][0] - x, coordinates[3][1] - y))
                        coordinates[0] = [x, y]
                        coordinates[1] = [coordinates[1][0], y]
                        coordinates[2] = [x, coordinates[2][1]]

                    # 선택된 포인트가 2번째 꼭지점인 경우
                    elif draggin_idx == 1:
                        qp.drawRect(QRect(coordinates[0][0], y, x - coordinates[0][0], coordinates[2][1] - y))
                        coordinates[0] = [coordinates[0][0], y]
                        coordinates[1] = [x, y]
                        coordinates[3] = [x, coordinates[2][1]]

                    # 선택된 포인트가 3번째 꼭지점인 경우
                    elif draggin_idx == 2:
                        qp.drawRect(QRect(x, coordinates[0][1], coordinates[1][0] - x, y - coordinates[0][1]))
                        coordinates[0] = [x, coordinates[0][1]]
                        coordinates[2] = [x, y]
                        coordinates[3] = [coordinates[1][0], y]

                    # 선택된 포인트가 4번째 꼭지점인 경우
                    elif draggin_idx == 3:
                        qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], x - coordinates[0][0], y - coordinates[0][1]))
                        coordinates[1] = [x, coordinates[0][1]]
                        coordinates[2] = [coordinates[0][0], y]
                        coordinates[3] = [x, y]

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
        global qim
        global mask_btn
        global coordinates
        global sig

        # 마우스 위치를 확대, 축소된 이미지에 맞도록 변환
        if scale_factor_w <= 1:
            x = view.mapToScene(e.pos()).x() * scale_factor_w
            y = view.mapToScene(e.pos()).y() * scale_factor_w
        else:
            x = view.mapToScene(e.pos()).x()
            y = view.mapToScene(e.pos()).y()

        if sig != 1:
            # Ctrl이 눌려 있을 경우 아무 작업도 실행되지 않음
            if mask_btn.isChecked() and e.button() == Qt.LeftButton:
                # 현재 비박스 정보를 갱신
                coordinates = [[self.start_point.x(), self.start_point.y()], [x, self.start_point.y()], [self.start_point.x(), y], [x, y]]

                # 갱신된 비박스 정보를 표시
                qp = QPainter()
                im.setDevicePixelRatio(scale_factor_w)
                qp.begin(im)
                qp.setPen(line_pen)
                qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
                qp.end()
                scene.clear()
                scene.addPixmap(im)
                self.repaint()
                """
                if draggin_idx == 10:
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.drawRect(QRect(self.start_point.x(), self.start_point.y(), x - self.start_point.x(), y - self.start_point.y()))
                    qp.end()
                    scene.addPixmap(im)
                """
                draggin_idx = -1

            # 수정 작업중일 때, 마우스가 때지면 최종 수정된 마스크 값으로 마스크 값을 갱신
            if edit_btn.isChecked() and e.button() == Qt.LeftButton:
                qp = QPainter()
                im = QPixmap.fromImage(qim)
                im.setDevicePixelRatio(scale_factor_w)
                qp.begin(im)
                qp.setPen(line_pen)
                """
                qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], coordinates[3][0] - coordinates[0][0], coordinates[3][1] - coordinates[0][1]))
                """
                if draggin_idx == 0:
                    qp.drawRect(QRect(x, y, coordinates[3][0] - x, coordinates[3][1] - y))
                    tem_coor = self.bbox2coordinate([x, y, coordinates[3][0] - x, coordinates[3][1] - y])
                    coordinates = self.point_sort(tem_coor)
                elif draggin_idx == 1:
                    qp.drawRect(QRect(coordinates[0][0], y, x - coordinates[0][0], coordinates[2][1] - y))
                    tem_coor = self.bbox2coordinate([coordinates[0][0], y, x - coordinates[0][0], coordinates[2][1] - y])
                    coordinates = self.point_sort(tem_coor)
                elif draggin_idx == 2:
                    qp.drawRect(QRect(x, coordinates[0][1], coordinates[1][0] - x, y - coordinates[0][1]))
                    tem_coor = self.bbox2coordinate([x, coordinates[0][1], coordinates[1][0] - x, y - coordinates[0][1]])
                    coordinates = self.point_sort(tem_coor)
                elif draggin_idx == 3:
                    qp.drawRect(QRect(coordinates[0][0], coordinates[0][1], x - coordinates[0][0], y - coordinates[0][1]))
                    tem_coor = self.bbox2coordinate([coordinates[0][0], coordinates[0][1], x - coordinates[0][0], y - coordinates[0][1]])
                    coordinates = self.point_sort(tem_coor)
                qp.end()
                scene.addPixmap(im)
                draggin_idx = -1

        else:
            sig = 0

    def wheelEvent(self, ev):
        # 휠이 움직일때 발생하는 이벤트
        mods = ev.modifiers()
        delta = ev.angleDelta()

        global scale_factor_w
        global qp
        global scene
        global im
        global view
        global line_pen

        # ctrl+휠을 하면 이미지의 사이즈가 확대, 축소 되도록 수정

        qp = QPainter()
        qp.begin(im)
        # 확대, 축소비율 설정 휠이 한번 움직일때마다 10%씩 작아지거나 커짐, 최소, 최대 크기는 0.5배에서 4배로 설정
        if delta.y() > 0 and scale_factor_w > 0.25:
            scale_factor_w = scale_factor_w * 0.9
        elif scale_factor_w < 2 and delta.y() < 0:
            scale_factor_w = scale_factor_w * 1.1
        if scale_factor_w < 0.5:
            line_pen.setWidth(2)
        else:
            line_pen.setWidth(4)
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
        global scene
        global mask_num
        global mask_btn
        global line_pen
        global im
        global color_value

        if scale_factor_w <= 1:
            x = view.mapToScene(e.pos()).x() * scale_factor_w
            y = view.mapToScene(e.pos()).y() * scale_factor_w
        else:
            x = view.mapToScene(e.pos()).x()
            y = view.mapToScene(e.pos()).y()
        w = im.width()
        h = im.height()

        #Ctrl + 좌클릭을 할 경우 화면이동
        if sig == 1 and e.buttons() == Qt.LeftButton:
            view.fitInView(QRectF(e.x()/scale_factor_w, e.y()/scale_factor_w, w, h), Qt.KeepAspectRatio)
        else:
            # 마스킹 작업 중 이벤트
            if mask_btn.isChecked():
                # 좌클릭시 포인트 생성 및 draggin_idx = 10(작업중)으로 변환
                if e.buttons() == Qt.LeftButton:
                    self.start_point = QPoint(x, y)
                    qp = QPainter()
                    qp.begin(im)
                    qp.setPen(line_pen)
                    qp.drawPoint(x, y)
                    qp.end()
                    scene.addPixmap(im)
                    draggin_idx = 10

            # 수정 작업중 발생하는 이벤트
            # 클릭위치와 가장 가까운 점을 계산하여 해당 포인트를 마우스 위치로 수정
            if edit_btn.isChecked():
                if len(coordinates) != 0:
                    if e.buttons() == Qt.LeftButton and draggin_idx == -1:
                        point = [x, y]
                        min_dist = np.array(coordinates) - np.array(point)
                        min_dist = np.array(min_dist[:, 0] ** 2 + min_dist[:, 1] ** 2)
                        minimum_value = min_dist.argmin()

                        # 마우스 위치와 포인트의 위치 사이의 거리가 1000이상일 경우 포인트 반환x

                        if min(min_dist) < 1000:
                            draggin_idx = minimum_value

    def point_sort(self, coordinate):
        #점들의 로케이션이 달라질 경우를 대비한 로케이션 재설정 함수
        sorted_coord = sorted(coordinate)
        new_coord = [[],[],[],[]]
        new_coord[0] = sorted_coord[0]
        new_coord[1] = sorted_coord[2]
        new_coord[2] = sorted_coord[1]
        new_coord[3] = sorted_coord[3]
        return new_coord

    def bbox2coordinate(self, bbox):
        # 비박스의 x, y, w, h를 받아 네 점의 좌표를 반환
        coor = [[bbox[0], bbox[1]], [bbox[0] + bbox[2], bbox[1]], [bbox[0], bbox[1] + bbox[3]], [bbox[0] + bbox[2], bbox[1] + bbox[3]]]
        return coor

    def keyPressEvent(self, QKeyEvent):
        global sig
        if QKeyEvent.key() == Qt.Key_Space:
            sig = 1




