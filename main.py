#-*- coding:utf-8 -*-
# firefly : 192.168.1.186
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import *
import resist_DB, picture_DB_sample, labelling
import check_DB as check
import augment_DB as project
from DCD_DB_API_master.db_api import DB
from MQTT_client import mqtt_connector
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

class MyApp(QWidget):
    """
    update_object에 category_id -> cat_id
    check_nomix_OBM -> mask값만 있어도 되도록 수정


    Annotation tool의 가장 상위 코드, 해당 코드를 실행 시키면 툴 실행

    실행 시킨 후 수행 할 작업의 버튼을 클릭 시, 해당 작업을 수행할 수 있는 새로운 창이 열림
    DB와의 연동은 특정 버튼(추후 DB연동 버튼과 일반 버튼의 색을 구분 예정)을 누를 때만 되므로 작업 중 구현 기능으로 해결할 수 없는
    문제가 생겼을 경우 창을 닫고 새로 열면 됨

    버튼별 상세 설명은 해당 기능이 구현된 파일의 주석에 있음

    모든 작업은 DB에 저장되기 때문에 따로 특정한 컨펌을 할 필요 없이 각 작업이 끝나면 창을 닫으면 됨
    """
    def __init__(self, db):
        super().__init__()
        self.initUI()
        self.DB = db
        # for i in range(8841,9441):
        #     tem_img = self.DB.get_table(str(i), "Image")
        #     im_data = np.array(Image.open(BytesIO(tem_img[2])).convert("RGB"))
        #     im_data[:, :, [0, 2]] = im_data[:, :, [2, 0]]
        #     cv2.imwrite(str(i) + ".jpg", im_data)
        #     with open(str(i) + ".jpg", 'rb') as file:
        #         img = file.read()
        #     self.DB.update_image(str(i), img=img)


        # a = []
        # for i in self.DB.list_table("Object"):
        #     if i[1] == 32 and i[4] == 10:
        #         a.append(i[0])
        # print(a)
        # print(len(a))

        # a=[]
        # for i in self.DB.list_table("Object"):
        #     if i[3] == 8837:
        #         a.append(i[0])
        # for i in self.DB.list_table("Bbox"):
        #     for j in a:
        #         if i[1] == j:
        #             print(i)

        # for i in self.DB.list_table("Image"):
        #     if i[0] < 8441 and i[3] == 3:
        #         self.DB.delete_table(str(i[0]), "Image")
        # for i in self.DB.list_table("Object"):
        #     print(i[3])
        #
        # for i in range(9451, 9461):
        #     self.DB.delete_table(str(i), "Image")
        # for i in range(1, 31):
        #     self.DB.delete_mix_obj(str(i))

        # for i in range(20, 26):
        #     tem_img = self.DB.get_table(str(i), "Image")
        #     im_data = np.array(Image.open(BytesIO(tem_img[2])).convert("RGB"))
        #     im_data[:, :, [0, 2]] = im_data[:, :, [2, 0]]
        #     cv2.imwrite(str(i) + ".png", im_data)
# #
#         for i in range(48, 58):
#             image_id = self.DB.get_table(str(i), "Object")[0]
#             tem_img = self.DB.get_table(str(image_id), "Image")
#             im_data = np.array(Image.open(BytesIO(tem_img[2])).convert("RGB"))
#             im_data[:, :, [0, 2]] = im_data[:, :, [2, 0]]
#             cv2.imwrite(str(i) + ".png", im_data)



    def initUI(self):
        #기능별 버튼 생성
        resist_btn = QPushButton("등록", self)
        picture_btn = QPushButton("촬영", self)
        check_btn = QPushButton('검수', self)
        labeling_btn = QPushButton("라벨링", self)
        project_btn = QPushButton("합성", self)
        zig_btn = QPushButton("지그오픈")

        #버튼과 해당 기능을 하는 함수를 연결
        resist_btn.clicked.connect(self.regist_part)
        picture_btn.clicked.connect(self.picture_window)
        check_btn.clicked.connect(self.check_window)
        labeling_btn.clicked.connect(self.labeling_window)
        project_btn.clicked.connect(self.project_window)
        zig_btn.clicked.connect(self.open)

        #버튼 나열
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(resist_btn, 1, 0)
        grid.addWidget(picture_btn, 1, 1)
        grid.addWidget(check_btn, 1, 2)
        grid.addWidget(labeling_btn, 2, 0)
        grid.addWidget(project_btn, 2, 1)
        grid.addWidget(zig_btn, 2, 2)
        self.setLayout(grid)

        #윈도우 사이즈, 타이틀 설정
        self.resize(500, 500)
        self.setWindowTitle("베이리스")
        #프로그램 아이콘 설정
        self.setWindowIcon(QIcon("beyless.png"))
        self.show()

    #등록 기능 창을 띄워주는 함수
    def regist_part(self):
        self.res_window = resist_DB.resist_app(self.DB)
        self.res_window.regist_window()

    # 촬영 기능을 하는 창을 띄워주는 함수
    def picture_window(self):
        self.selection_window = picture_DB_sample.picture_app(self.DB)
        self.selection_window.selection_window()

    # 검수 기능 창을 띄워주는 함수
    def check_window(self):
        self.check_window = check.check_app(self.DB)
        self.check_window.check_window()

    # 라벨링 기능 창을 띄워주는 함수
    def labeling_window(self):
        self.label_window = labelling.label_app(self.DB)
        self.label_window.label_window()

    # 합성 기능 창을 띄워주는 함수
    def project_window(self):
        self.augmentation_window = project.project_app(self.DB)
        self.augmentation_window.augmentation()

    #지그 테스트를 위한 지그 오픈 및, 찍힌 사진을 띄워주는 함수
    def open(self):
        self.open_window = QWidget()
        img_label = QLabel()
        conn = mqtt_connector('192.168.10.69', 1883, "20001")
        conn.collect_dataset("20001", 1)  # ip, port  collect: env_id , image_type
        image_id = conn.get_result()
        print(image_id)
        # 저장된 이미지를 읽어보여주는 함수
        tem_img = self.DB.get_table(str(image_id), "Image")
        print(tem_img[0])
        im_data = np.array(Image.open(BytesIO(tem_img[2])).convert("RGB"))
        cv2.imwrite("dd.png", im_data)
        qim = QImage(im_data, im_data.shape[1], im_data.shape[0], im_data.strides[0], QImage.Format_RGB888)
        self.image_data = QPixmap.fromImage(qim)
        img_label.clear()

        qp = QPainter()
        qp.begin(self.image_data)
        # 오브젝트에 관련된 비박스가 존재할 경우 비박스 출력

        qp.setPen(QPen(QColor(255, 0, 0), 4))
        qp.drawLine(0, qim.height()/2, qim.width(), qim.height()/2)
        qp.drawLine(qim.width()/2, 0, qim.width()/2, qim.height())
        qp.end()

        img_label.setPixmap(self.image_data.scaledToWidth(1000))
        vbox = QVBoxLayout()
        vbox.addWidget(img_label)
        self.open_window.setLayout(vbox)
        self.open_window.show()

    def keyPressEvent(self, QKeyEvent):
        print(QKeyEvent.key())


#실제 코드를 실행
if __name__ == '__main__':
    mydb = DB.DB('192.168.10.69', 3306, 'root', 'return123', 'test')
    mydb.init_table()
    app = QApplication(sys.argv)
    ex = MyApp(mydb)
    sys.exit(app.exec_())
