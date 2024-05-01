 
from PyQt5.QtWidgets import QWidget, QPushButton, QGraphicsScene, QGraphicsView
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QBrush, QColor

from PyQt5.QtCore import QVariantAnimation, QPointF
from PyQt5.QtCore import pyqtSignal


class EEGModelGame(QWidget):
    #SAG ve SOLA ulaştığında sinyal gönder
    hedefeUlasti = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.initUI()
        #self.initThreads()
    def initUI(self):
        #self.setGeometry(100, 100, 800, 600)
        #self.setWindowTitle('PyQt5 Modern Arayüz')
        self.setStyleSheet("background-color: #333; color: white;")


        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setStyleSheet("background-color: transparent;")

        self.circle = QGraphicsEllipseItem(0, 0, 50, 50)
        self.circle.setBrush(QBrush(QColor(255, 0, 0)))
        self.scene.addItem(self.circle)

        self.leftSquare = QGraphicsRectItem(0, 150, 50, 350)
        self.rightSquare = QGraphicsRectItem(750, 150, 50, 350)
        #karenin rengini #45C63A yap
        self.leftSquare.setBrush(QBrush(QColor(69, 198, 58)))
        self.rightSquare.setBrush(QBrush(QColor(69, 198, 58)))
        # self.leftSquare.setBrush(QBrush(QColor(0, 255, 0)))
        # self.rightSquare.setBrush(QBrush(QColor(0, 255, 0)))
        self.scene.addItem(self.leftSquare)
        self.scene.addItem(self.rightSquare)

        self.circle.setPos(375, 275)
        # self.btnLeft = QPushButton('<-- Sol')

        # self.btnLeft.clicked.connect(self.moveLeft)
        # self.btnRight = QPushButton('Sağ -->')
        # self.btnRight.clicked.connect(self.moveRight)
        #self.btnStart = QPushButton('Başlat')
        #self.btnStart.clicked.connect(self.baslat)
        #self.coreButton = QPushButton('Core Başlat')
        #self.coreButton.clicked.connect(self.start_core)

        # hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        # hbox.addWidget(self.btnLeft)
        # #hbox.addWidget(self.view)
        # hbox.addWidget(self.btnRight)
        #hbox.addWidget(self.btnStart)
        #hbox.addWidget(self.coreButton)
        # vbox.addLayout(hbox)
        vbox.addWidget(self.view)
        self.setLayout(vbox)
        self.stepSize = 20



    def setGameSettings(self, adimSayisi):
        self.stepSize = 325/adimSayisi

        
    def checkCollisionAndReset(self):
        # Dairenin sol veya sağ dikdörtgenle çarpışıp çarpışmadığını kontrol et
        if self.circle.collidesWithItem(self.leftSquare):
            self.circle.setPos(375, 275)
            self.hedefeUlasti.emit(0)

        elif self.circle.collidesWithItem(self.rightSquare):
            
            # Daireyi başlangıç konumuna geri getir
            self.circle.setPos(375, 275)
            self.hedefeUlasti.emit(1)

    def konumSifirla(self):
        self.circle.setPos(375, 275)

    def moveLeft(self):
        # Animasyonu başlatmadan önce mevcut konumu al
        currentPos = self.circle.pos()
        # Animasyon için bitiş konumunu belirle
        endPos = QPointF(currentPos.x() - self.stepSize, currentPos.y())
        # Animasyonu oluştur ve ayarla
        self.animation = QVariantAnimation()
        self.animation.setStartValue(currentPos)
        self.animation.setEndValue(endPos)
        self.animation.setDuration(250)  # 0.25 saniye süre
        self.animation.valueChanged.connect(self.circle.setPos)
        self.animation.finished.connect(self.checkCollisionAndReset)  # Animasyon bittiğinde çarpışmayı kontrol et
        self.animation.start()

    def moveRight(self):
        # Animasyonu başlatmadan önce mevcut konumu al
        currentPos = self.circle.pos()
        # Animasyon için bitiş konumunu belirle
        endPos = QPointF(currentPos.x() + self.stepSize, currentPos.y())
        # Animasyonu oluştur ve ayarla
        self.animation = QVariantAnimation()
        self.animation.setStartValue(currentPos)
        self.animation.setEndValue(endPos)
        self.animation.setDuration(250)  # 0.25 saniye süre
        self.animation.valueChanged.connect(self.circle.setPos)
        self.animation.finished.connect(self.checkCollisionAndReset)  # Animasyon bittiğinde çarpışmayı kontrol et
        self.animation.start()