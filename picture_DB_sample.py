from PyQt5.QtCore import *
from io import BytesIO
from PIL import Image
import numpy as np
from MQTT_client import mqtt_connector
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import copy

class picture_app(QWidget):
    """
    최상위 화면에서 촬영 버튼을 누르면 생성되는 클래스
    1. 촬영할 환경, 그리드를 박스에서 선택한 후, 원하는 물품을 클릭하고 -> 버튼을 누르면 해당 물품이 좌측 공간에서 가운데 공간으로 이동한다.
    2. 만약 원하지 않는 물품을 실수로 가운데로 옮겼을 경우 가운데 공간에서 해당 물품을 선택 후 <- 버튼을 클릭하면 다시 좌측 공간으로 이동한다.
    3. 원하는 물품들을 모두 가운데 공간에 둔 후, 물품추가 버튼을 누르면 물품들에 그리드 정보가 합쳐져 우측 공간으로 이동한다.
    4. 원하는 모든 물품을 우측 공간에 넘겨줄 때 까지 1., 2. 과정을 반복 후, 원하는 물품이 모두 오른쪽 공간에 이동되면 확인 버튼을 누른다.(이순간 Object table이 생성됨)
    5. 좌측에 촬영해야할 물품 리스트가 뜨고 가운데 해당 물품의 로케이션이 뜬다.(미구현) 우측화면엔 기본적으로 썸네일 이미지가 보이며,
    이미 촬영된 이미지가 있을 경우, 촬영된 이미지를 보여준다.
    6. 촬영 버튼을 누르면 우측의 이미지가 촬영된 이미지로 바뀐다.(촬영 버튼을 누르는 순간 해당 물품의 이미지는 촬영된 이미지로 업데이트 됨)
    !!!등록에서 잘못 등록한 물품들은 여기서 삭제해야함. 물품리스트에서 삭제하고 싶은 물품을 선택 후, 삭제 버튼 클릭!!!
    """
    def __init__(self, db):
        super().__init__()
        self.DB = db


    # 현재는 물품추가는 없음
    def selection_window(self):

        # 디바이스와 물품을 선택하는 윈도우 생성
        self.device_combo = QComboBox()
        self.environment_cash = self.DB.list_table("Environment")
        self.grid_cash = self.DB.list_table("Grid")
        self.category_cash = self.DB.list_table("Category")

        device_label = QLabel("디바이스")
        grid_label = QLabel("그리드")

        #환경, 그리드를 선택할 수 있는 박스 생성
        self.grid_box = QComboBox()
        self.device_box = QComboBox()

        #박스에 현재 존재하는 환경을 추가
        for i in self.environment_cash:
            self.device_box.addItem(str(i[1]) + "/" + str(i[2]))

        #박스에 현재 존재하는 그리드를 추가
        for i in self.grid_cash:
            self.grid_box.addItem(str(i[1]) + "x" + str(i[2]))

        #선택할 수 있는 카테고리(물품)를 보여주는 트리 생성
        self.object_list = QTreeWidget(self)
        self.object_list.setColumnCount(1)
        self.object_list.setHeaderLabels(["물품 리스트", ])

        #촬영하고 싶은 물품 리스트를 보여주는 트리 생성
        self.add_list = QTreeWidget(self)
        self.add_list.setColumnCount(1)
        self.add_list.setHeaderLabels(["추가할 물품 리스트", ])

        #실제 촬영단계로 넘어가는 정보를 보여주는 트리 생성
        self.added_list = QTreeWidget(self)
        self.added_list.setColumnCount(3)
        self.added_list.setHeaderLabels(["추가된 물품 리스트", "그리드", "횟수"])

        #촬영 정보를 선택하는 버튼들 생성
        self.move_left = QPushButton("<-(A)")
        self.move_left.setStyleSheet("background-color : yellow")
        self.move_left.setShortcut("A")
        self.move_left.setToolTip("A")
        self.move_right = QPushButton("->(D)")
        self.move_right.setStyleSheet("background-color : yellow")
        self.move_right.setShortcut("D")
        self.move_right.setToolTip("D")
        self.confirm_btn = QPushButton("확인")
        self.confirm_btn.setStyleSheet("background-color : blue")
        self.add_category_btn = QPushButton("물품 추가(F)")
        self.add_category_btn.setShortcut("F")
        self.add_category_btn.setToolTip("F")
        self.add_category_btn.setStyleSheet("background-color : green")
        self.obj_delete_btn = QPushButton("삭제(Delete)")
        self.obj_delete_btn.setStyleSheet("background-color : yellow")
        self.obj_delete_btn.setShortcut("Delete")
        self.obj_delete_btn.setToolTip("Delete")
        self.obj_delete_btn.clicked.connect(self.delete_object)
        self.delete_btn = QPushButton("삭제")
        self.delete_btn.setStyleSheet("background-color : blue")
        self.delete_btn.clicked.connect(self.delete_category)
        empty_layout = QHBoxLayout()
        empty_layout.addWidget(self.delete_btn)
        empty_layout.addStretch(1)
        empty_layout.addWidget(self.obj_delete_btn)

        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addWidget(self.object_list)
        layout.addWidget(self.add_list)
        layout.addWidget(self.added_list)

        h0layout = QBoxLayout(QBoxLayout.LeftToRight)
        h0layout.addWidget(device_label)
        h0layout.addWidget(self.device_box)

        hlayout = QBoxLayout(QBoxLayout.LeftToRight)
        hlayout.addWidget(grid_label)
        hlayout.addWidget(self.grid_box)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_layout.addLayout(h0layout)
        main_layout.addLayout(hlayout)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.move_right)
        main_layout.addWidget(self.move_left)
        main_layout.addLayout(empty_layout)
        main_layout.addWidget(self.add_category_btn)
        main_layout.addWidget(self.confirm_btn)

        #DB에서 카테고리(물품)를 불러와 물품트리에 보여주는 파트
        self.setLayout(main_layout)
        self.objects = QTreeWidget.invisibleRootItem(self.object_list)
        super_len = len(self.DB.list_table("SuperCategory"))
        for j in range(super_len):
            for i in self.category_cash:
                super_name = self.DB.get_table(i[0], "SuperCategory")[1]
                if i[0] == j + 1 and super_name != "mix" and super_name != "background":
                    item = self.make_tree_item(i[2] + "/" + super_name, 0)
                    self.objects.addChild(item)

        for j in range(super_len):
            for i in self.category_cash:
                super_name = self.DB.get_table(i[0], "SuperCategory")[1]
                if i[0] == j + 1 and (super_name == "mix" or super_name == "background"):
                    item = self.make_tree_item(i[2] + "/" + super_name, 0)
                    self.objects.addChild(item)

        self.move_right.clicked.connect(self.move_object)
        self.move_left.clicked.connect(self.move_object)
        self.confirm_btn.clicked.connect(self.select_object)
        self.add_category_btn.clicked.connect(self.add_category)

        self.resize(1200, 800)
        self.setWindowTitle("물품추가")
        self.show()


    def add_category(self):
        # 물건추가 버튼을 눌렀을 경우 추가를원하는 물품을 보여주는 트리에 있는 물품들을 실제 촬영단계로 넘기는 트리로 넘기는 함수
        self.add_category = QTreeWidget.invisibleRootItem(self.added_list)
        for i in range(self.add_list.topLevelItemCount()):
            item = self.add_list.topLevelItem(i)
            for j in self.category_cash:
                if j[2] + "/" + self.DB.get_table(j[0], "SuperCategory")[1] == item.text(0):
                    if item.text(0).split("/")[1] == "mix":
                        add_item = self.make_multi_tree_item([item.text(0), "0x0", j[6]])
                    elif item.text(0).split("/")[1] == "background":
                        add_item = self.make_multi_tree_item([item.text(0), "1x1", j[6]])
                    else:
                        add_item = self.make_multi_tree_item([item.text(0), self.grid_box.currentText(), j[6]])
            self.add_category.addChild(add_item)

        # 추가 완료된 아이템을 리스트에서 방출
        source_tw = self.add_list
        target_tw = self.object_list
        source = QTreeWidget.invisibleRootItem(source_tw)
        root = QTreeWidget.invisibleRootItem(target_tw)
        for i in range(source_tw.topLevelItemCount()):
            item = source_tw.topLevelItem(0)
            source.removeChild(item)
            root.addChild(item)



    def select_object(self):

        # 물품선택 화면에서 확인버튼을 누르면 선택된 물품정보들을 다음 화면으로 넘기며 실제 촬영화면을 띄워주는 함수
        self.category_list = []
        self.grid_list = []
        self.iterate_list = []

        for i in range(self.added_list.topLevelItemCount()):
            item = self.added_list.topLevelItem(i)
            self.category_list.append(item.text(0))
            self.grid_list.append(item.text(1))
            self.iterate_list.append(item.text(2))
        self.picture_data = list(zip(self.category_list, self.grid_list, self.iterate_list))

        #촬영을 원하는 물품들의 정보들로 오브젝트를 생성하는 부분(이미지는 None)
        for i in self.picture_data:
            cate_super_cate = i[0].split("/")
            cate_id = str(self.DB.get_cat_id(cate_super_cate[0], cate_super_cate[1]))
            self.DB.set_obj_list(str(self.DB.get_grid_id(i[1]))[1:-2], cate_id, str(self.DB.get_table(cate_id, "Category")[6]), "-1")

        #모든 오브젝트를 생성한 후 오브젝트 정보들 캐싱
        self.object_cash = self.DB.list_table("Object")
        self.close()
        self.shoot_window()


    def make_tree_item(cls, name, i):
        # 물품 트리에 아이템을 추가하는 함수
        item = QTreeWidgetItem()
        item.setText(i, name)
        return item

    def make_multi_tree_item(cls, name):
        # 촬영 물품 트리에 아이템을 추가하는 함수
        item = QTreeWidgetItem()
        item.setText(0, name[0])
        item.setText(1, name[1])
        item.setText(2, str(name[2]))
        return item

    def move_object(self):
        # 물품 트리에서 추가 물품 트리로 아이템을 옮기는 함수
        sender = self.sender()
        if self.move_right == sender:
            source_tw = self.object_list
            target_tw = self.add_list
        else:
            source_tw = self.add_list
            target_tw = self.object_list

        # 현재 선택된 아이템을 꺼내어 반대편 쪽으로 전달(초기화)
        item = source_tw.currentItem()
        source = QTreeWidget.invisibleRootItem(source_tw)
        source.removeChild(item)

        root = QTreeWidget.invisibleRootItem(target_tw)
        root.addChild(item)

    def delete_category(self):
        #잘못 만들어진 물품을 삭제하는 함수
        ans = QMessageBox.question(self, "삭제확인", "삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans == QMessageBox.Yes:
            category = self.object_list.currentItem()
            cate_str = category.text(0)
            cate_str = cate_str.split("/")
            source = QTreeWidget.invisibleRootItem(self.object_list)
            source.removeChild(category)
            self.DB.delete_table(str(self.DB.get_cat_id(cate_str[0], cate_str[1])), "Category")

    def delete_object(self):
        item = self.added_list.currentItem()
        source = QTreeWidget.invisibleRootItem(self.added_list)
        source.removeChild(item)

    def shoot_window(self):
        # 실제 촬영할 윈도우 생성
        self.category_list = []
        self.grid_x_list = []
        self.grid_y_list = []
        self.iterate_list = []
        for i in range(self.added_list.topLevelItemCount()):
            item = self.added_list.topLevelItem(i)
            self.category_list.append(item.text(0))
            grid = item.text(1)
            grid = grid.replace("x", " ")
            grid = grid.split()
            self.grid_x_list.append(grid[0])
            self.grid_y_list.append(grid[1])
            self.iterate_list.append(item.text(2))
        self.picture_data = list(zip(self.category_list, self.grid_x_list, self.grid_y_list, self.iterate_list))

        device = self.device_box.currentText().split("/")
        self.device_id = str(self.DB.get_env_id(device[0], device[1]))
        #물품추가 윈도우를 닫음
        self.close()

        #촬영 윈도우를 생성
        self.shoot_windows = QWidget()

        #레이아웃 및 작업공간을 나눌 수 있는 프레임 생성
        hbox = QHBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        self.mid_frame = QFrame()
        self.mid_frame.setFrameShape(QFrame.Box)
        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.Box)
        self.image_label = QLabel()
        self.image_hbox = QHBoxLayout()
        self.image_hbox.addWidget(self.image_label)
        self.right_frame.setLayout(self.image_hbox)
        """
        왼쪽 프레임
        """
        #프레임에 넣을 레이아웃 생성
        title = QLabel("물품 리스트")
        btn_layout = QHBoxLayout()
        left_btn = QPushButton("<-(A)")
        left_btn.clicked.connect(self.move_image)
        left_btn.setShortcut("A")
        left_btn.setToolTip("A")
        right_btn = QPushButton("->(D)")
        right_btn.clicked.connect(self.move_image)
        right_btn.setShortcut("D")
        right_btn.setToolTip("D")
        btn_layout.addWidget(left_btn)
        btn_layout.addWidget(right_btn)
        btn_frame = QFrame()
        btn_frame.setLayout(btn_layout)
        device_label = QLabel(self.device_box.currentText())
        self.btn_group = QButtonGroup()
        self.scroll_vbox = QVBoxLayout()

        #클릭했을 때, 각 물품을 띄워줄 수 있도록 물품 별 버튼 생성
        self._scrollArea = QScrollArea()
        self._scrollArea.setWidgetResizable(True)
        self.a = []
        # 생성된 모든 오브젝트에 접근 가능한 버튼 생성
        # mix데이터가 들어올 경우 iteration 수만큼 오브젝트 생성
        for i in self.picture_data:
            if i[1] == "0" and i[2] == "0":
                for k in range(int(i[3])):
                    tt = QPushButton(str(i[0]) + "_0x0/0x0_" + str(k + 1))
                    tt.setCheckable(True)
                    self.btn_group.addButton(tt)
                    self.a.append(tt)
            else:
                for j in range(1, int(i[1]) * int(i[2]) + 1):
                    for k in range(int(i[3])):
                        tt = QPushButton(
                            str(i[0]) + "_" + str((j - 1) % int(i[1]) + 1) + "x" + str((j - 1) // int(i[1]) + 1) + "/" +
                            i[1] + "x" + i[2] + "_" + str(k + 1))
                        tt_name = tt.text().split("_")  # (테스트 1x2 5) - >(오브젝트이름, 1x2/3x3, 횟수)
                        category_id = str(self.DB.get_cat_id(tt_name[0].split("/")[0], tt_name[0].split("/")[1]))
                        location_id = str(self.DB.get_loc_id_GL(tt_name[1].split("/")[1], tt_name[1].split("/")[0]))[1:-2]
                        iteration = str(tt_name[2])
                        self.current_obj_id = self.DB.get_obj_id_from_args(location_id, category_id, iteration, "-1")
                        # 해당 오브젝트가 이미지를 가지고 있으면(이미 촬영이 된 경우) 해당 이미지를 보여줌

                        if self.DB.get_table(self.current_obj_id, "Object")[0] != None:
                            im = self.DB.get_table(str(self.DB.get_table(self.current_obj_id, "Object")[0]), "Image")
                            if im[4] == 2:
                                tt.setStyleSheet("background-color: red")
                        tt.setCheckable(True)
                        self.btn_group.addButton(tt)
                        self.a.append(tt)

        #생성된 버튼과 오브젝트 정보를 연동
        for i in range(len(self.a)):
            if i == 0:
                self.a[i].clicked.connect(self.load_image_grid)
                self.a[i].click()
            else:
                self.a[i].clicked.connect(self.load_image_grid)
            self.scroll_vbox.addWidget(self.a[i])
        left_frame.setLayout(self.scroll_vbox)
        self._scrollArea.setWidget(left_frame)

        """
        중앙 프레임
        """
        grid_label = QLabel("그리드")
        #미구현

        """
        오른쪽 프레임
        """

        #촬영버튼 생성
        shoot_btn = QPushButton("촬영(S)")
        shoot_btn.setShortcut("S")
        shoot_btn.clicked.connect(self.shoot)
        self.right_hbox = QHBoxLayout()

        #이미지 표시

        #윈도우를 나누어 만들어진 프레임들을 나눠진 공간에 배치
        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(grid_label)
        splitter2.addWidget(self.mid_frame)

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.addWidget(title)
        splitter3.addWidget(device_label)
        splitter3.addWidget(self._scrollArea)
        splitter3.addWidget(btn_frame)

        splitter4 = QSplitter(Qt.Vertical)
        splitter4.addWidget(shoot_btn)
        splitter4.addWidget(self.right_frame)
        splitter4.splitterMoved.connect(self.print_xy)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(splitter3)
        splitter1.addWidget(splitter2)
        splitter1.addWidget(splitter4)
        splitter1.splitterMoved.connect(self.print_xy)

        hbox.addWidget(splitter1)
        self.shoot_windows.setLayout(hbox)
        self.shoot_windows.setWindowTitle("촬영")
        self.shoot_windows.show()

    def print_xy(self):
        print(self.right_frame.width())
        print(self.right_frame.height())
        self.image_label.clear()
        width = copy.deepcopy(self.right_frame.width())
        height = copy.deepcopy(self.right_frame.height())
        if self.right_frame.width() > 1500:
            width = 1500
            print("width max")
        if self.right_frame.height() > 800:
            height = 800
            print("height max")
        self.image_label.setPixmap(self.image_data.scaled(width, height))


    def load_image_grid(self):
        #버튼이 클릭됬을 때, 해당 오브젝트의 이미지를 띄워주는 함수
        #버튼으로 부터 어떤 오브젝트를 접근해야 하는지 확인
        self.image_name = self.sender()
        self.image_name = self.image_name.text()
        self.image_name = self.image_name.split("_")

        category_id = str(self.DB.get_cat_id(self.image_name[0].split("/")[0], self.image_name[0].split("/")[1]))
        location_id = str(self.DB.get_loc_id_GL(self.image_name[1].split("/")[1], self.image_name[1].split("/")[0]))[1:-2]
        iteration = str(self.image_name[2])

        self.current_obj_id = self.DB.get_obj_id_from_args(location_id, category_id, iteration, "-1")
        #해당 오브젝트가 이미지를 가지고 있으면(이미 촬영이 된 경우) 해당 이미지를 보여줌
        if self.DB.get_table(self.current_obj_id, "Object")[0] != None:
            im = self.DB.get_table(str(self.DB.get_table(self.current_obj_id, "Object")[0]), "Image")
            im_data = np.array(Image.open(BytesIO(im[2])).convert("RGB"))
            qim = QImage(im_data, im_data.shape[1], im_data.shape[0], im_data.strides[0], QImage.Format_RGB888)
            self.image_data = QPixmap.fromImage(qim)
            self.image_label.clear()
            width = self.right_frame.width()
            height = self.right_frame.height()
            if self.right_frame.width() > 1500:
                width = 1500
            if self.right_frame.height() > 800:
                height = 800
            self.image_label.setPixmap(self.image_data.scaled(width, height))


        #해당 오브젝트가 이미지를 가지고 있지 않으면(첫 촬영인 경우) 썸네일을 보여줌
        else:
            for i in self.category_cash:
                if category_id == str(i[1]):
                    im_data = np.array(Image.open(BytesIO(i[7])).convert("RGB"))
                    qim = QImage(im_data, im_data.shape[1], im_data.shape[0], im_data.strides[0], QImage.Format_RGB888)
                    self.image_data = QPixmap.fromImage(qim)
                    self.image_label.clear()
                    width = self.right_frame.width()
                    height = self.right_frame.height()
                    if self.right_frame.width() > 1500:
                        width = 1500
                    if self.right_frame.height() > 800:
                        height = 800
                    self.image_label.setPixmap(self.image_data.scaled(width, height))

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

    def shoot(self):
        #촬영 버튼과 연동된 실제 촬영 및, 이미지 업데이트 함수
        #촬영하여 이미지를 DB에 저장하는 함수
        conn = mqtt_connector('192.168.10.71', 1883, self.device_id)
        conn.collect_dataset(self.device_id, 1)# ip, port  collect: env_id , image_type
        image_id = conn.get_result()
        #저장된 이미지를 읽어보여주는 함수
        tem_img = self.DB.get_table(str(image_id), "Image")
        self.image1 = np.array(Image.open(BytesIO(tem_img[2])).convert("RGB"))
        #self.image1[:, :, [0, 2]] = self.image1[:, :, [2, 0]]
        qim = QImage(self.image1, self.image1.shape[1], self.image1.shape[0], self.image1.strides[0],
                     QImage.Format_RGB888)
        im = QPixmap.fromImage(qim)

        #이미지 사이즈를 조정
        self.image_label.setPixmap(im.scaledToWidth(1500))

        #현재 오브젝트에 촬영된 이미지 업데이트
        self.DB.update_object(self.current_obj_id, img_id=tem_img[1])
        self.DB.update_img_img_obj_id(self.current_obj_id, tem_img[2])

        #믹스인 경우 데이터 타입을 2로 설정
        if self.image_name[0].split("/")[1] == "mix":
            self.DB.update_image(self.DB.get_table(self.current_obj_id, "Object")[0], type=2)
