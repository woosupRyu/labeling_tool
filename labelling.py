from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import sys
from PyQt5.QtGui import *
from PyQt5 import QtCore
import bboxing
import masking_DB as masking
import bboxing_DB as bboxing
import mix_bboxing_DB as mix

class label_app(QWidget):
    def __init__(self, db):
        super().__init__()
        self.DB = db

    def label_window(self):
        mask_btn = QPushButton("Mask")
        bbox_btn = QPushButton("Bbox")
        mix_btn = QPushButton("Mix")
        bbox_btn.clicked.connect(self.bbox)
        mask_btn.clicked.connect(self.mask)
        mix_btn.clicked.connect(self.mix)

        vbox = QVBoxLayout()
        vbox.addWidget(bbox_btn)
        vbox.addWidget(mask_btn)
        vbox.addWidget(mix_btn)

        self.resize(400, 400)
        self.setLayout(vbox)
        self.setWindowTitle("작업 선택 창")
        self.show()
    def bbox(self):
        self.bbox_window = bboxing.bbox(self.DB)
        self.bbox_window.bboxing()

    def mask(self):
        self.mask_window = masking.mask(self.DB)
        self.mask_window.masking()

    def mix(self):
        self.mask_window = mix.mix(self.DB)
        self.mask_window.mix_bboxing()



