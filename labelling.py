from PyQt5.QtWidgets import *
import masking_DB as masking
import augment_check_DB as aug_bboxing
import mix_bboxing_DB as mix

class label_app(QWidget):
    def __init__(self, db):
        super().__init__()
        self.DB = db

    def label_window(self):
        mask_btn = QPushButton("Mask")
        bbox_btn = QPushButton("Aug Bbox")
        mix_btn = QPushButton("Mix Bbox")
        bbox_btn.clicked.connect(self.aug_bbox)
        mask_btn.clicked.connect(self.mask)
        mix_btn.clicked.connect(self.mix)

        vbox = QVBoxLayout()
        vbox.addWidget(mask_btn)
        vbox.addWidget(bbox_btn)
        vbox.addWidget(mix_btn)

        self.resize(400, 400)
        self.setLayout(vbox)
        self.setWindowTitle("작업 선택 창")
        self.show()

    def aug_bbox(self):
        self.aug_bbox_window = aug_bboxing.aug_check(self.DB)
        self.aug_bbox_window.aug_bbox()

    def mask(self):
        self.mask_window = masking.mask(self.DB)
        self.mask_window.masking()

    def mix(self):
        self.mask_window = mix.mix(self.DB)
        self.mask_window.mix_bboxing()



