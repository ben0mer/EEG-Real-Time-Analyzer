import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from modelapi import ModelAPI
from pylsl import StreamInlet, resolve_stream
from PyQt5.QtCore import QThread, pyqtSignal, QProcess
import pandas as pd
# import joblib
import trainfunctions as tf


class EEGAnalyzeThread(QThread):
    moveLeft = pyqtSignal()
    moveRight = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.model_path = "exported_models//RandomForestClassifier()-7-O2.pkl"
        self.model_api = ModelAPI(self.model_path)
    def run(self):
        streams = resolve_stream('type', 'EEG')
        inlet = StreamInlet(streams[0])
        sample, timestamp = inlet.pull_sample()
        eeg_data = []
        while True:
            sample, timestamp = inlet.pull_sample()
            sample = [el / 1000000 for el in sample]
            eeg_data.append(sample)
            # EEG verisi 160 satır olup olmadığını kontrol et
            if len(eeg_data) == 160:
                # eeg_data verisinin 7. sütununu al
                yeni_veri = pd.DataFrame(eeg_data)
                yeni_veri = yeni_veri.iloc[:,7]
                yeni_veri = pd.DataFrame(yeni_veri)
                yeni_veri = tf.ornekle(yeni_veri, 160)
                #print(yeni_veri)
                self.make_prediction(yeni_veri)
                eeg_data = []
    def make_prediction(self, yeni_veri):
        predictions = self.model_api.tahmin(yeni_veri,_probability=True)
        #prediction'ın 0. sütunundaki değer 1 ise kareyi sağa kaydır, 0 ise sola kaydır
        predictions = self.model_api.tahmin(yeni_veri,_probability=True)
        print(predictions)
        if any(predictions[:, 0] == 1):
            self.moveRight.emit()
        else:
            self.moveLeft.emit()
            
        

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
        self.btnStart = QPushButton('Başlat')
        self.btnStart.clicked.connect(self.baslat)
        self.coreButton = QPushButton('Core Başlat')
        self.coreButton.clicked.connect(self.start_core)
        
        # Butonları ve görünümü düzene ekle
        hbox.addWidget(self.btnLeft)
        hbox.addWidget(self.view)
        hbox.addWidget(self.btnRight)
        hbox.addWidget(self.btnStart)
        hbox.addWidget(self.coreButton)
        self.process = QProcess(self)  # QProcess nesnesi oluştur
        # Ana düzeni ayarla
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.eeg_analyze_thread = EEGAnalyzeThread()
        self.eeg_analyze_thread.moveLeft.connect(self.moveLeft)
        self.eeg_analyze_thread.moveRight.connect(self.moveRight)

        
        self.show()

    def baslat(self):
        #QQhread başlat

        if not self.eeg_analyze_thread.isRunning():
            self.eeg_analyze_thread.start()
    def start_core(self):
        self.process.start('powershell.exe', ['-NoExit', '-Command', 'cd C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\emotiv-lsl; python -m pipenv run python main.py'])
        print("Core Başlatıldı")

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
