import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt

class CircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PyQt5 Modern Arayüz')
        
        # Arayüzün koyu temasını ayarla
        self.setStyleSheet("background-color: #333; color: white;")
        
        # Yatay düzeni oluştur
        hbox = QHBoxLayout()
        
        # Yuvarlağı ve kareleri içerecek sahneyi ve görünümü oluştur
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setStyleSheet("background-color: transparent;")
        
        # Yuvarlağı oluştur ve sahneye ekle
        self.circle = QGraphicsEllipseItem(0, 0, 50, 50)
        self.circle.setBrush(QBrush(QColor(255, 0, 0)))
        self.scene.addItem(self.circle)
        
        # Kareleri oluştur ve sahneye ekle
        self.leftSquare = QGraphicsRectItem(0, 250, 50, 50)
        self.rightSquare = QGraphicsRectItem(750, 250, 50, 50)
        self.leftSquare.setBrush(QBrush(QColor(0, 255, 0)))
        self.rightSquare.setBrush(QBrush(QColor(0, 255, 0)))
        self.scene.addItem(self.leftSquare)
        self.scene.addItem(self.rightSquare)
        
        # Yuvarlağın başlangıç konumunu ayarla
        self.circle.setPos(375, 275)
        
        # Butonları oluştur ve fonksiyonlarına bağla
        self.btnLeft = QPushButton('<-- Sol')
        self.btnLeft.clicked.connect(self.moveLeft)
        self.btnRight = QPushButton('Sağ -->')
        self.btnRight.clicked.connect(self.moveRight)
        
        # Butonları ve görünümü düzene ekle
        hbox.addWidget(self.btnLeft)
        hbox.addWidget(self.view)
        hbox.addWidget(self.btnRight)
        
        # Ana düzeni ayarla
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        self.show()

    def moveLeft(self):
        if self.circle.x() > 0:
            self.circle.moveBy(-10, 0)
            if self.circle.collidesWithItem(self.leftSquare):
                self.circle.setPos(375, 275)

    def moveRight(self):
        if self.circle.x() < 700:
            self.circle.moveBy(10, 0)
            if self.circle.collidesWithItem(self.rightSquare):
                self.circle.setPos(375, 275)

# Uygulamayı başlat
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CircleWidget()
    sys.exit(app.exec_())
