from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from io import BytesIO
from PIL import Image
from PyQt5.QtGui import *
import numpy as np
from DCD_DB_API_master.db_api import DB

global lock
lock = True

class check_app(QWidget):
    """
    최상위 화면에서 검수 버튼을 클릭했을 때 생성되는 클래스

    물품과 그리드를 선택하면 해당하는 오브젝트들이 가진 이미지를 보여줌
    거절되었거나 검수되지 않은 이미지만 보여줌
    1. 원하는 물품과 그리드를 선택 후, 나타나는 해당 오브젝트들의 사진을 보고 체크박스에 거절할 이미지에 체크됨
    2. 작업 완료 후 거절 버튼을 누르면 체크된 버튼들은 붉은색이 되며 거절됨
    3. 나머지 버튼들의 체크박스를 클릭한 후, 허락버튼을 누르면 해당 이미지들은 초록색이 되며 허락됨

    !!! 검수 화면에서는 거절되었거나 검수되지 않은 이미지만 보여주므로
    한번 허락된 이미지는 검수화면을 닫았다 키거나 물품을 바꿧다 돌아오게 되면 사라지게 되니 거절은 쉽게하더라도
    허락은 신중하게 해야함!!!
    """
    def __init__(self, db):
        super().__init__()
        self.DB = db

    def check_window(self):
        #레이아웃 및 프레임 생성 및 편의 버튼 생성
        hbox = QHBoxLayout()
        self.left_frame = QFrame()
        self.left_frame.setFrameShape(QFrame.Box)
        mid_frame = QFrame()
        mid_frame.setFrameShape(QFrame.Box)
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Box)
        select_all_btn = QPushButton("전체선택(G)")
        select_all_btn.setShortcut("G")
        select_all_btn.setToolTip("G")
        select_all_btn.clicked.connect(self.select_all)
        move_right_btn = QPushButton("->(D)")
        move_right_btn.clicked.connect(self.move_image)
        move_right_btn.setShortcut("D")
        move_right_btn.setToolTip("D")
        move_left_btn = QPushButton("<-(A)")
        move_left_btn.clicked.connect(self.move_image)
        move_left_btn.setShortcut("A")
        move_left_btn.setToolTip("A")

        """
        중간 프레임
        """
        # 이미지 표시
        mid_hbox = QHBoxLayout()
        self.image_label = QLabel()
        mid_hbox.addWidget(self.image_label)
        mid_frame.setLayout(mid_hbox)

        """
        왼쪽 프레임
        """
        # 카테고리 및 그리드 선택 박스 생성
        self.category_box = QComboBox()
        for i in self.DB.list_table("Category"):
            super_name = self.DB.get_table(i[0], "SuperCategory")
            self.category_box.addItem(i[2] + "/" + super_name[1])
        self.category_box.currentIndexChanged.connect(self.change_category)
        self.category_box.resize(self.category_box.sizeHint())

        self.grid_box = QComboBox()
        for i in self.DB.list_table("Grid"):
            self.grid_box.addItem(str(i[1]) + "x" + str(i[2]))
        self.grid_box.currentIndexChanged.connect(self.change_grid)
        self.grid_box.resize(self.grid_box.sizeHint())

        #검수할 오브젝트 버튼 생성 준비
        self.left_vbox = QVBoxLayout()
        self.scroll_vbox = QVBoxLayout()
        self._scrollArea = QScrollArea()
        self._scrollArea.setWidgetResizable(True)
        self.a = []
        self.b = []
        self.btn_group = QButtonGroup()
        cate_info = self.category_box.currentText().split("/")
        super_id = self.DB.get_supercategory_id_from_args(cate_info[1])
        self.current_category = str(self.DB.get_category_id_from_args(str(super_id), cate_info[0]))
        self.current_grid = str(self.DB.get_grid_id_from_args(self.grid_box.currentText()))

        #현재 물품과 그리드를 참고하여 검수되지 않았거나 거절된 이미지를 가진 오브젝트만 호출
        objects = []
        ob = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "1"))
        if len(ob) != 0:
            objects.append(ob)
        rejected = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "2"))
        if len(rejected) != 0:
            objects.append(rejected)

        #호출된 오브젝트들로 버튼 생성 및 연동
        num = 0
        obj_btn_name_list = self.obj_list2name(sum(objects, []))
        for i in range(len(sum(objects, []))):
            check_box = QCheckBox()
            image_btn = QPushButton(obj_btn_name_list[i])
            image_btn.setCheckable(True)
            self.btn_group.addButton(image_btn)
            image_btn.clicked.connect(self.signal)
            tem_hbox = QHBoxLayout()
            tem_hbox.addWidget(check_box)
            tem_hbox.addWidget(image_btn)
            self.left_vbox.addLayout(tem_hbox)
            self.a.append(check_box)
            self.b.append(image_btn)
            if num == 0:
                self.b[num].click()
            num = num + 1
        self.scroll_vbox.addLayout(self.left_vbox)
        #self.left_frame.setLayout(self.scroll_vbox)
        self._scrollArea.setLayout(self.scroll_vbox)



        """
        오른쪽 프레임
        """
        #이미지 검수 버튼 설정
        pass_btn = QPushButton("허락")
        pass_btn.setStyleSheet("background-color: green")
        reject_btn = QPushButton("거절")
        reject_btn.setStyleSheet("background-color: red")

        pass_btn.clicked.connect(self.pass_image)
        reject_btn.clicked.connect(self.reject_image)

        grid = QGridLayout()
        grid.addWidget(pass_btn, 1, 0)
        grid.addWidget(reject_btn, 2, 0)

        right_frame.resize(100, 1000)
        right_frame.setLayout(grid)

        # 작업공간 배치
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.category_box)
        splitter.addWidget(self.grid_box)
        splitter.setStretchFactor(0, 1)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(splitter)
        splitter1.addWidget(self._scrollArea)
        splitter1.addWidget(move_left_btn)
        splitter1.addWidget(move_right_btn)
        splitter1.addWidget(select_all_btn)
        splitter1.setStretchFactor(1, 2)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(mid_frame)
        splitter2.addWidget(right_frame)
        splitter2.setStretchFactor(1, 4)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)

        self.resize(1300,1000)
        self.setWindowTitle("검수")
        self.show()

    def signal(self):
        global lock
        if lock:
            lock = False
            #이미지 클릭시 이미지를 띄워주는 함수
            btn_name = self.sender().text()
            obj_id = self.obj_name2id(btn_name)
            im = self.DB.get_table(str(self.DB.get_table(obj_id, "Object")[0]), "Image")

            im_data = np.array(Image.open(BytesIO(im[2])).convert("RGB"))
            qim = QImage(im_data, im_data.shape[1], im_data.shape[0], im_data.strides[0], QImage.Format_RGB888)
            self.image_data = QPixmap.fromImage(qim)
            self.image_label.clear()
            self.image_label.setPixmap(self.image_data.scaledToWidth(1000))
            lock = True

    def pass_image(self):
        #선택된 이미지들을 허락하는 함수
        for i in range(len(self.a)):
            if self.a[i].isChecked() == True:
                self.b[i].setStyleSheet("background-color : green")
                DB.update_image_check_num(self.DB, self.obj_name2id(self.b[i].text()), "0")
                self.a[i].toggle()

    def reject_image(self):
        global lock
        if lock:
            lock = False
            #선택된 이미지들을 거절하는 함수
            for i in range(len(self.a)):
                if self.a[i].isChecked() == True:
                    self.b[i].setStyleSheet("background-color : red")
                    DB.update_image_check_num(self.DB, self.obj_name2id(self.b[i].text()), "2")
                    self.a[i].toggle()
            lock = True

    def change_category(self):
        global lock
        if lock:
            lock = False
            #물품을 선택했을 때, 해당 물품의 오브젝트만 보여주는 함수
            #check_window함수와 유사함/ check_window함수 참조
            cate_info = self.category_box.currentText().split("/")
            super_id = self.DB.get_supercategory_id_from_args(cate_info[1])
            self.current_category = str(self.DB.get_category_id_from_args(str(super_id), cate_info[0]))
            objects = []
            self.a = []
            self.b = []
            for i in reversed(range(self.left_vbox.count())):
                k = self.left_vbox.itemAt(i).layout()
                for j in reversed(range(k.count())):
                    k.itemAt(j).widget().deleteLater()
                k.deleteLater()
            # for i in reversed(range(self.left_vbox.count())):
            #     self.left_vbox.itemAt(i).layout().deleteLater()
            ob = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "1"))
            if len(ob) != 0:
                objects.append(ob)
            rejected = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "2"))
            if len(rejected) != 0:
                objects.append(rejected)

            obj_btn_name_list = self.obj_list2name(sum(objects, []))
            num = 0
            for i in range(len(sum(objects, []))):
                check_box = QCheckBox()
                image_btn = QPushButton(obj_btn_name_list[i])
                image_btn.setCheckable(True)
                self.btn_group.addButton(image_btn)
                # check_box.clicked.connect(self.signal)
                image_btn.clicked.connect(self.signal)
                tem_hbox = QHBoxLayout()
                tem_hbox.addWidget(check_box)
                tem_hbox.addWidget(image_btn)

                self.left_vbox.addLayout(tem_hbox)
                self.a.append(check_box)
                self.b.append(image_btn)
                if num == 0:
                    lock = True
                    self.b[num].click()
                num = num + 1
            self.update()
            lock = True


    def change_grid(self):
        global lock
        if lock:
            lock = False
            #그리드가 바뀌었을 때, 해당 그리드와 관련된 오브젝트를 보여주는 함수
            #check_window, change_category함수와 유사함, check_window, change_category함수 참조
            self.current_grid = str(self.DB.get_grid_id_from_args(self.grid_box.currentText()))
            objects = []
            self.a = []
            self.b = []

            for i in reversed(range(self.left_vbox.count())):
                k = self.left_vbox.itemAt(i).layout()
                for j in reversed(range(k.count())):
                    k.itemAt(j).widget().deleteLater()
                k.deleteLater()

            ob = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "1"))
            if len(ob) != 0:
                objects.append(ob)
            rejected = list(DB.list_object_check_num(self.DB, self.current_category, self.current_grid, "2"))
            if len(rejected) != 0:
                objects.append(rejected)
            num = 0
            obj_btn_name_list = self.obj_list2name(sum(objects, []))
            for i in range(len(sum(objects, []))):
                check_box = QCheckBox()
                image_btn = QPushButton(obj_btn_name_list[i])
                image_btn.setCheckable(True)
                self.btn_group.addButton(image_btn)
                # check_box.clicked.connect(self.signal)
                image_btn.clicked.connect(self.signal)
                tem_hbox = QHBoxLayout()
                tem_hbox.addWidget(check_box)
                tem_hbox.addWidget(image_btn)
                self.left_vbox.addLayout(tem_hbox)
                self.a.append(check_box)
                self.b.append(image_btn)
                if num == 0:
                    lock = True
                    self.b[num].click()
                num = num + 1
            self.update()
            lock = True


    def obj_list2name(self, obj_list):
        #오브젝트들의 아이디를 참조하여 해당하는 버튼의 이름을 만들어주는 함수
        btn_name_list = []
        for i in range(len(obj_list)):
            #img_id = obj_list[i][0]
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
        #버튼이름을 참조하여 오브젝트 아이디를 반환해주는 함수
        #아래 주석이 함수의 예시
        #i = "콜라/음료_1x2/3x3_1"
        i = i.split("_")#  "콜라/음료", "1x2/3x3", "1"
        i[0] = i[0].split("/")#  "콜라" "음료" "1x2" "3x3", "1"
        i[1] = i[1].split("/")

        super_id = self.DB.get_supercategory_id_from_args(i[0][1])
        cate_id = self.DB.get_category_id_from_args(str(super_id), i[0][0])
        grid_id = self.DB.get_grid_id_from_args(i[1][1])
        loc_id = self.DB.get_location_id_from_args(str(grid_id), i[1][0])
        obj_id = self.DB.get_obj_id_from_args(str(loc_id), str(cate_id), (int(i[2])-1), "-1")
        return str(obj_id)

    def select_all(self):
        for i in self.a:
            i.setChecked(True)

    def move_image(self):
        #다음, 이전 이미지로 이동하는 버튼과 연동된 함수
        len_a = len(self.a)
        sender = self.sender().text()
        if sender == "<-(A)":
            for i in range(len_a):
                if self.b[i].isChecked():
                    if i > 0:
                        self.b[i - 1].click()
                        break
        elif sender == "->(D)":
            for i in range(len_a):
                if self.b[i].isChecked():
                    if i < (len_a - 1):
                        self.b[i + 1].click()
                        break