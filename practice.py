#-*- coding:utf-8 -*-
# firefly : 192.168.1.186
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import *
import resist, picture_modify, labelling
import check_DB as check
import project_DB as project
import DB
from mqtt import mqtt_connector
from io import BytesIO
from PIL import Image
import numpy as np

class MyApp(QWidget):
    """
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
        #im_data = np.array(cv2.imread("example.jpg")).tobytes()
        #self.DB.set_image(200000, im_data, 0, 0)
        #self.DB.update_object("1", img_id="1", loc_id="1", category_id="1", iteration="1", mix_num="0")

    def initUI(self):
        #기능별 버튼 생성
        resist_btn = QPushButton("등록", self)
        picture_btn = QPushButton("촬영", self)
        check_btn = QPushButton('검수', self)
        labeling_btn = QPushButton("라벨링", self)
        project_btn = QPushButton("합성", self)
        zig_btn = QPushButton("지그오픈")

        #버튼과 해당 기능을 하는 함수를 연결
        resist_btn.resize(resist_btn.sizeHint())
        resist_btn.clicked.connect(self.regist_part)
        picture_btn.resize(picture_btn.sizeHint())
        picture_btn.clicked.connect(self.picture_window)
        check_btn.resize(check_btn.sizeHint())
        check_btn.clicked.connect(self.check_window)
        labeling_btn.resize(labeling_btn.sizeHint())
        labeling_btn.clicked.connect(self.labeling_window)
        project_btn.resize(project_btn.sizeHint())
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

    # 창을 닫을 경우 진짜 닫을지 메세지 표시
    # def closeEvent(self, QCloseEvent):
    #     ans = QMessageBox.question(self, "종료확인", "종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #     if ans == QMessageBox.Yes:
    #         QCloseEvent.accept()
    #     else:
    #         QCloseEvent.ignore()

    #등록 기능 창을 띄워주는 함수
    def regist_part(self):
        self.res_window = resist.resist_app(self.DB)
        self.res_window.regist_window()

    # 촬영 기능을 하는 창을 띄워주는 함수
    def picture_window(self):
        self.selection_window = picture_modify.picture_app(self.DB)
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
        #지그오픈 및 사진촬영 함수
        mqtt_connector('192.168.10.19', 1883).collect_dataset("20001", 1)# ip, port  collect: env_id , image_type
        #지그에서 찍힌 사진을 띄움
        self.open_window = QWidget()
        img_label = QLabel()
        mage = str(self.DB.get_last_id("Image"))[2:-3]
        image = self.DB.get_table(mage, "Image")
        im_data = np.array(Image.open(BytesIO(image[2])).convert("RGB"))
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


#실제 코드를 실행
if __name__ == '__main__':
    mydb = DB.DB('192.168.10.69', 3306, 'root', 'return123', 'test')
    app = QApplication(sys.argv)
    ex = MyApp(mydb)
    sys.exit(app.exec_())