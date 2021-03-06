from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2

class resist_app(QWidget):
    """
    최상위 창에서 등록 버튼을 누르면 활성화 되는 클래스

    디바이스(환경), 그리드, 분류, 물품을 등록하는 창
    예시)
    디바이스
    ID : xxx.xxx.xxx.xxx  (x는 0~9 정수)
    층수 : 1~x (정수)
    가로 : 1~x (정수)
    깊이 : 1~x (정수)
    높이 : 1~x (정수)

    그리드
    x : 1~x(정수)
    y : 1~x(정수)
    예외 : mix전용 그리드는 x = 0, y = 0 으로 입력

    분류
    분류 : (str)

    물품등록
    분류 : 이름 위의 박스에서 물품의 분류를 선택
    이름 : (str)
    가로 : 1~x (정수)
    깊이 : 1~x (정수)
    높이 : 1~x (정수)
    촬영 횟수 : 1~x (정수)
    이미지 : 찾기 버튼 클릭 후 파일 선택

    위의 예시 형식대로 입력 후, 등록 버튼을 선택하면 해당 정보가 등록 되면서 확인 창이 뜸
    """
    def __init__(self, db):
        super().__init__()
        self.DB = db

    def regist_window(self):
        #각 정보별 등록버튼 생성 및 기능 함수 연동
        device_btn = QPushButton("등록")
        device_btn.setStyleSheet("background-color: blue")
        grid_btn = QPushButton("등록")
        grid_btn.setStyleSheet("background-color: blue")
        super_category_btn = QPushButton("등록")
        super_category_btn.setStyleSheet("background-color: blue")
        category_btn = QPushButton("등록")
        category_btn.setStyleSheet("background-color: blue")
        device_btn.clicked.connect(self.send_device_text)
        grid_btn.clicked.connect(self.send_grid_text)
        super_category_btn.clicked.connect(self.send_super_category_text)
        category_btn.clicked.connect(self.send_category_text)

        # 타이핑할 수 있는 위젯, 선택할 수 있는 위젯 생성
        self.broker_IP = QLineEdit()
        self.device_ID = QLineEdit()
        self.floor = QLineEdit()
        self.device_w = QLineEdit()
        self.device_d = QLineEdit()
        self.device_h = QLineEdit()
        self.grid_x = QLineEdit()
        self.grid_y = QLineEdit()
        self.super_category_name = QLineEdit()
        self.super_category_list = QComboBox()
        self.category_name = QLineEdit()
        self.category_w = QLineEdit()
        self.category_d = QLineEdit()
        self.category_h = QLineEdit()
        self.iterate_num = QLineEdit()
        self.thumbnail = QLineEdit()
        self.typing16 = QPushButton("찾기")
        self.typing16.clicked.connect(self.search_image)

        #이미 존재하는 분류를 박스에 추가
        self.super_category_cash = self.DB.list_table("SuperCategory")
        if self.super_category_cash != None:
            for i in self.super_category_cash:
                self.super_category_list.addItem(i[1])

        #그리드의 특정 위치에 특정 요소 배치
        grid = QGridLayout()

        grid.addWidget(device_btn, 7, 2)#(요소, 행, 열)
        grid.addWidget(grid_btn, 10, 2)
        grid.addWidget(super_category_btn, 12, 2)
        grid.addWidget(category_btn, 21, 2)

        grid.addWidget(self.broker_IP, 1, 2)
        grid.addWidget(self.device_ID, 2, 2)
        grid.addWidget(self.floor, 3, 2)
        grid.addWidget(self.device_w, 4, 2)
        grid.addWidget(self.device_d, 5, 2)
        grid.addWidget(self.device_h, 6, 2)
        grid.addWidget(self.grid_x, 8, 2)
        grid.addWidget(self.grid_y, 9, 2)
        grid.addWidget(self.super_category_name, 11, 2)
        grid.addWidget(self.super_category_list, 13, 2)
        grid.addWidget(self.category_name, 14, 2)
        grid.addWidget(self.category_w, 15, 2)
        grid.addWidget(self.category_d, 16, 2)
        grid.addWidget(self.category_h, 17, 2)
        grid.addWidget(self.iterate_num, 18, 2)
        grid.addWidget(self.thumbnail, 19, 2)
        grid.addWidget(self.typing16, 20, 2)

        label1 = QLabel("디바이스")
        label2 = QLabel("Broker_ip")
        label3= QLabel("Device_id")
        label4 = QLabel("층수")
        label5 = QLabel("가로")
        label6 = QLabel("깊이")
        label7 = QLabel("높이")
        label8 = QLabel("그리드")
        label9 = QLabel("x")
        label10 = QLabel("y")
        label11 = QLabel("분류정보")
        label12 = QLabel("분류")
        label13 = QLabel("물품정보")
        label14 = QLabel("분류")
        label15 = QLabel("이름")
        label16 = QLabel("가로")
        label17 = QLabel("세로")
        label18 = QLabel("높이")
        label19 = QLabel("촬영 횟수")
        label20 = QLabel("이미지")

        grid.addWidget(label1, 1, 0)
        grid.addWidget(label2, 1, 1)
        grid.addWidget(label3, 2, 1)
        grid.addWidget(label4, 3, 1)
        grid.addWidget(label5, 4, 1)
        grid.addWidget(label6, 5, 1)
        grid.addWidget(label7, 6, 1)
        grid.addWidget(label8, 8, 0)
        grid.addWidget(label9, 8, 1)
        grid.addWidget(label10, 9, 1)
        grid.addWidget(label11, 11, 0)
        grid.addWidget(label12, 11, 1)
        grid.addWidget(label13, 13, 0)
        grid.addWidget(label14, 13, 1)
        grid.addWidget(label15, 14, 1)
        grid.addWidget(label16, 15, 1)
        grid.addWidget(label17, 16, 1)
        grid.addWidget(label18, 17, 1)
        grid.addWidget(label19, 18, 1)
        grid.addWidget(label20, 19, 1)

        #요소들이 배치된 그리드를 실제 창에 배치

        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.Box)
        self.right_layout = QVBoxLayout()


        self.device_frame = QFrame()
        self.device_frame.setFrameShape(QFrame.Box)
        self.device_list = QScrollArea()
        self.device_list.setWidgetResizable(True)

        self.grid_frame = QFrame()
        self.grid_frame.setFrameShape(QFrame.Box)
        self.grid_list = QScrollArea()
        self.grid_list.setWidgetResizable(True)

        self.category_frame = QFrame()
        self.category_frame.setFrameShape(QFrame.Box)
        self.category_list = QScrollArea()
        self.category_list.setWidgetResizable(True)

        #label1,7
        self.category_label = QLabel("물품")
        self.grid_label = QLabel("그리드")
        self.device_label = QLabel("디바이스")

        self.device_cash = self.DB.list_table("Environment")
        self.device_a = []
        self.device_b = []
        self.device_vbox = QVBoxLayout()
        if self.device_cash != None:
            for i in self.device_cash:
                self.device_hbox = QHBoxLayout()
                self.name = QLabel(i[1] + "/" + str(i[0]) + "/" + str(i[2]))
                self.del_button = QPushButton("삭제")
                self.del_button.clicked.connect(self.device_delete)
                self.del_button.setCheckable(True)
                self.device_a.append(self.name)
                self.device_b.append(self.del_button)
                self.device_hbox.addWidget(self.name)
                self.device_hbox.addWidget(self.del_button)
                self.device_vbox.addLayout(self.device_hbox)
        self.device_frame.setLayout(self.device_vbox)
        self.device_list.setWidget(self.device_frame)

        self.grid_cash = self.DB.list_table("Grid")
        self.grid_a = []
        self.grid_b = []
        self.grid_vbox = QVBoxLayout()
        if self.grid_cash != None:
            for i in self.grid_cash:
                grid_hbox = QHBoxLayout()
                name = QLabel(str(i[1]) + "x" + str(i[2]))
                del_button = QPushButton("삭제")
                del_button.clicked.connect(self.grid_delete)
                del_button.setCheckable(True)
                self.grid_a.append(name)
                self.grid_b.append(del_button)
                grid_hbox.addWidget(name)
                grid_hbox.addWidget(del_button)
                self.grid_vbox.addLayout(grid_hbox)
        self.grid_frame.setLayout(self.grid_vbox)
        self.grid_list.setWidget(self.grid_frame)

        self.category_cash = self.DB.list_table("Category")
        self.category_a = []
        self.category_b = []
        self.category_vbox = QVBoxLayout()
        if self.category_cash != None:
            for i in self.category_cash:
                category_hbox = QHBoxLayout()
                name = QLabel(i[2] + "/" + self.DB.get_table(str(i[1]), "SuperCategory")[1])
                del_button = QPushButton("삭제")
                del_button.clicked.connect(self.category_delete)
                del_button.setCheckable(True)
                self.category_a.append(name)
                self.category_b.append(del_button)
                category_hbox.addWidget(name)
                category_hbox.addWidget(del_button)
                self.category_vbox.addLayout(category_hbox)
        self.category_frame.setLayout(self.category_vbox)
        self.category_list.setWidget(self.category_frame)

        self.right_layout.addWidget(self.device_label)
        self.right_layout.addWidget(self.device_list)
        self.right_layout.addWidget(self.grid_label)
        self.right_layout.addWidget(self.grid_list)
        self.right_layout.addWidget(self.category_label)
        self.right_layout.addWidget(self.category_list)

        self.right_frame.setLayout(self.right_layout)

        self.hbox = QHBoxLayout()

        self.hbox.addLayout(grid)
        self.hbox.addWidget(self.right_frame)

        self.setLayout(self.hbox)

        #윈도우 이름 설정 및 위도우 띄우기
        self.resize(1000, 700)
        self.setWindowTitle("등록")
        self.show()

    def device_delete(self):
        for i, info in enumerate(self.device_a):
            if self.sender() == self.device_b[i]:
                delete_name = info.text()
                del self.device_a[i]
                del self.device_b[i]
                break

        for j in reversed(range(self.device_vbox.count())):
            k = self.device_vbox.itemAt(j).layout()
            if j == i:
                for l in reversed(range(k.count())):
                    k.itemAt(l).widget().deleteLater()
                k.deleteLater()
        delete_name = delete_name.split("/")
        env_id = self.DB.get_env_id(delete_name[1], delete_name[0], delete_name[2])
        self.DB.delete_table(str(env_id), "Environment")

    def grid_delete(self):
        for i, info in enumerate(self.grid_b):
            if self.sender() == info:
                delete_name = self.grid_a[i].text()
                del info
                del self.grid_a[i]
                break

        for j in reversed(range(self.grid_vbox.count())):
            k = self.grid_vbox.itemAt(j).layout()
            if j == i:
                for l in reversed(range(k.count())):
                    k.itemAt(l).widget().deleteLater()
                k.deleteLater()

        grid_id = self.DB.get_grid_id(delete_name)
        self.DB.delete_table(str(grid_id), "Grid")

    def category_delete(self):
        for i, info in enumerate(self.category_b):
            if self.sender() == info:
                delete_name = self.category_a[i].text()
                del info
                del self.category_a[i]
                break

        for j in reversed(range(self.category_vbox.count())):
            k = self.category_vbox.itemAt(j).layout()
            if j == i:
                for l in reversed(range(k.count())):
                    k.itemAt(l).widget().deleteLater()
                k.deleteLater()
        cate_name = delete_name.split("/")
        super_id = self.DB.get_super_id_SN(cate_name[1])
        category_id = self.DB.get_cat_id_SI(str(super_id), cate_name[0])
        self.DB.delete_table(str(category_id), "Category")

    def send_device_text(self):
        #입력받은 디바이스 정보를 DB에 보내주는 함수
        return_value = self.DB.set_environment(self.device_ID.text(), self.broker_IP.text(), self.floor.text(), self.device_w.text(), self.device_d.text(), self.device_h.text())
        #중복된 데이터는 아래의 함수를 실행시키지 않음
        if return_value == True:
            bix = QHBoxLayout()
            new_env = QLabel(self.broker_IP.text() + "/" + self.device_ID.text() + "/" + self.floor.text())
            self.del_button2 = QPushButton("삭제")
            bix.addWidget(new_env)
            bix.addWidget(self.del_button2)
            self.del_button2.clicked.connect(self.device_delete)
            self.device_vbox.addLayout(bix)
            self.device_a.append(new_env)
            self.device_b.append(self.del_button2)
            self.update()
            #DB에 보낸 데이터를 확인시켜주는 창
            self.env_check_window = QWidget()

            ID_label = QLabel("deice_ID : " + self.device_ID.text())
            IP_label = QLabel("broker_IP : " + self.broker_IP.text())
            floor_label = QLabel("층수 : " + self.floor.text())
            w_label = QLabel("가로 : " + self.device_w.text())
            d_label = QLabel("깊이 : " + self.device_d.text())
            h_label = QLabel("높이 : " + self.device_h.text())
            check_label = QLabel("위의 정보를 가진 환경이 등록되었습니다.")
            check_btn = QPushButton("환경 확인")
            check_btn.clicked.connect(self.check)

            vbox = QVBoxLayout()
            vbox.addWidget(ID_label)
            vbox.addWidget(IP_label)
            vbox.addWidget(floor_label)
            vbox.addWidget(w_label)
            vbox.addWidget(d_label)
            vbox.addWidget(h_label)
            vbox.addWidget(check_label)
            vbox.addWidget(check_btn)

            self.env_check_window.setLayout(vbox)
            self.env_check_window.setWindowTitle("환경 등록 확인")
            self.env_check_window.show()

            # DB로 보내진 정보들을 Tool에서 지움
            self.device_ID.setText("")
            self.broker_IP.setText("")
            self.floor.setText("")
            self.device_w.setText("")
            self.device_d.setText("")
            self.device_h.setText("")

    def send_grid_text(self):
        #그리드 정보를 DB에 보내주는 함수
        grid_x_name = self.grid_x.text()
        grid_y_name = self.grid_y.text()
        x_len = int(grid_x_name)
        y_len = int(grid_y_name)
        return_value = self.DB.set_grid(x_len, y_len)
        # 중복된 데이터는 아래의 함수를 실행시키지 않음
        if return_value == True:
            bix = QHBoxLayout()
            new_grid = QLabel(grid_x_name + "x" + grid_y_name)
            self.del_button3 = QPushButton("삭제")
            bix.addWidget(new_grid)
            bix.addWidget(self.del_button3)
            self.del_button3.clicked.connect(self.grid_delete)
            self.grid_vbox.addLayout(bix)
            self.grid_a.append(new_grid)
            self.grid_b.append(self.del_button3)
            self.update()

            grid_cash = self.DB.list_table("Grid")
            for i, info in enumerate(grid_cash):
                if info[1] == x_len and info[2] == y_len:
                    grid_id = info[0]

            #그리드에 존재할 수 있는 모든 로케이션 생성
            location_check = ""
            #0x0이 들어올 경우 예외적으로 생성
            if grid_x_name == "0" and grid_y_name == "0":
                self.DB.set_location(str(grid_id), "0", "0")
                location_check = "0x0, "
            # 그리드에 존재할 수 있는 모든 로케이션 생성

            for i in range(x_len):
                for j in range(y_len):
                    self.DB.set_location(str(grid_id), str(i+1), str(j+1))
                    location_check = location_check + str(i+1) + "x" + str(j+1) + ", "

            # DB에 보낸 데이터를 확인시켜주는 창
            self.grid_resist = QWidget()
            grid_check_label  = QLabel(grid_x_name + "x" + grid_y_name + " 그리드가 생성되었습니다.")
            location_check_label = QLabel(location_check + str(x_len * y_len) + "개의 로케이션이 생성되었습니다.")
            check_btn = QPushButton("그리드 확인")
            check_btn.clicked.connect(self.check)
            vbox = QVBoxLayout()
            vbox.addWidget(grid_check_label)
            vbox.addWidget(location_check_label)
            vbox.addWidget(check_btn)

            self.grid_resist.setLayout(vbox)
            self.grid_resist.setWindowTitle("그리드, 로케이션 추가")
            self.grid_resist.show()

            # DB로 보내진 정보들을 Tool에서 지움
            self.grid_x.setText("")
            self.grid_y.setText("")



    def send_super_category_text(self):
        # 입력받은 디바이스 정보를 DB에 보내주는 함수
        super_name = self.super_category_name.text()
        return_value = self.DB.set_supercategory(super_name)

        # 중복된 데이터는 아래의 함수를 실행시키지 않음
        if return_value == True:
            #등록된 분류를 박스에 추가함
            self.super_category_list.addItem(super_name)
            self.super_category_list.setCurrentText(super_name)
            # DB로 보내진 정보들을 Tool에서 지움
            self.super_category_name.setText("")

    def send_category_text(self):
        #물품의 분류를 불러옴
        self.super_category_cash = self.DB.list_table("SuperCategory")
        for i in self.super_category_cash:
            if i[1] == self.super_category_list.currentText():
                super_category_id = str(i[0])
        # 썸네일 이미지를 읽어옴
        f = open(self.thumbnail.text(), "rb")
        # 물품 정보를 DB에 보내주는 함수
        return_value = self.DB.set_category(super_category_id, self.category_name.text(), self.category_w.text(), self.category_d.text(), self.category_h.text(), self.iterate_num.text(), f.read())
        f.close()
        if return_value == True:
            bix = QHBoxLayout()
            new_category = QLabel(self.category_name.text() + "/" + self.DB.get_table(super_category_id, "SuperCategory")[1])
            self.del_button4 = QPushButton("삭제")
            bix.addWidget(new_category)
            bix.addWidget(self.del_button4)
            self.del_button4.clicked.connect(self.category_delete)
            self.category_vbox.addLayout(bix)
            self.category_a.append(new_category)
            self.category_b.append(self.del_button4)
            self.update()

            # 중복된 데이터는 아래의 함수를 실행시키지 않음
            self.category_check_window = QWidget()

            super_category_label = QLabel("분류 : " + self.super_category_list.currentText())
            name_label = QLabel("이름 : " + self.category_name.text())
            w_label = QLabel("가로 : " + self.category_w.text())
            d_label = QLabel("깊이 : " + self.category_d.text())
            h_label = QLabel("높이 : " + self.category_h.text())
            iteration_label = QLabel("반복 횟수 : " + self.iterate_num.text())
            thumb_label = QLabel("썸네일 : ")
            check_btn = QPushButton("물품 확인")
            check_btn.clicked.connect(self.check)
            thumbnail_label = QLabel()
            img = cv2.imread(self.thumbnail.text())
            img[:, :, [0, 2]] = img[:, :, [2, 0]]
            qim = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)
            im = QPixmap.fromImage(qim)
            thumbnail_label.setPixmap(im.scaledToWidth(500))

            check_label = QLabel("위의 정보로 카테고리가 등록되었습니다.")

            vbox = QVBoxLayout()
            vbox.addWidget(super_category_label)
            vbox.addWidget(name_label)
            vbox.addWidget(w_label)
            vbox.addWidget(d_label)
            vbox.addWidget(h_label)
            vbox.addWidget(iteration_label)
            vbox.addWidget(thumb_label)
            vbox.addWidget(thumbnail_label)
            vbox.addWidget(check_label)
            vbox.addWidget(check_btn)

            # DB로 보내진 정보들을 Tool에서 지움
            self.category_name.setText("")
            self.category_w.setText("")
            self.category_d.setText("")
            self.category_h.setText("")
            self.iterate_num.setText("")
            self.thumbnail.setText("")

            self.category_check_window.setLayout(vbox)
            self.category_check_window.setWindowTitle("카테고리 체크")
            self.category_check_window.show()

    def search_image(self):
        #썸네일 파일을 찾을 수 있도록 창을 띄워주는 함수
        thumbnail = QFileDialog()
        thumb_name = thumbnail.getOpenFileName()
        self.thumbnail.setText(thumb_name[0])

    def check(self):
        #물품 등록 후 확인 창에서 버튼을 누르면 창이 닫는 함수
        if self.sender().text() == "환경 확인":
            self.env_check_window.close()
        elif self.sender().text() == "물품 확인":
            self.category_check_window.close()
        elif self.sender().text() == "그리드 확인":
            self.grid_resist.close()

# 썸네일 이미지 확인 코드
# a = self.DB.get_category(1)
# im = Image.open(BytesIO(a[0][6]))
# im.show()




