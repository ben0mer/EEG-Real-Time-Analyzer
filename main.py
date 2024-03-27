

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout
import pyqtgraph as pg
from PyQt5 import QtCore

from EEGStreamThread import EEGStreamThread
from UpdatePlotThread import UpdatePlotThread

class eegGraphWidget(QtWidgets.QWidget):
    # EEG verilerini çizmek için kullanılacak widget
    # 14 adet EEG verisi çizilecek 14 adet grafik alt alta olacak

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Arayüzün özelliklerini ayarla
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('EEG Veri Grafiği')
        self.setStyleSheet("background-color: #333; color: white;")
        # EEG verilerini çizmek için 14 adet grafik oluştur
        self.eegGrafikler = []
        #Grafiklerin çizdirileceği renkleri tutan liste
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        for i in range(14):
            self.eegGrafikler.append(pg.PlotWidget())
            #arka planı transparant yap
            self.eegGrafikler[i].setBackground('transparent')
            self.eegGrafikler[i].setXRange(0, 800)
            #self.eegGrafikler[i].setYRange(-1, 1)
            self.eegGrafikler[i].showGrid(x=True, y=True)
            self.eegGrafikler[i].setStyleSheet("background-color: #333; color: white;")
            #Grafiklerin çizdirileceği renkleri ayarla
            self.eegGrafikler[i].plot(pen=self.colors[i % len(self.colors)])
            #grafiğin boyutunu ayarla
            self.eegGrafikler[i].setFixedHeight(200)
            #self.eegGrafikler[i].setFixedWidth(800)
        # Grafikleri düzenle
        self.grafikLayout = QVBoxLayout()
        for i in range(14):
            self.grafikLayout.addWidget(self.eegGrafikler[i])
        #Grafiğin sol tarafında 14 adet EEG veri için isimler
        self.labelLayout = QVBoxLayout()
        self.labelLayout.addWidget(QtWidgets.QLabel("AF3"))
        self.labelLayout.addWidget(QtWidgets.QLabel("F7"))
        self.labelLayout.addWidget(QtWidgets.QLabel("F3"))
        self.labelLayout.addWidget(QtWidgets.QLabel("FC5"))
        self.labelLayout.addWidget(QtWidgets.QLabel("T7"))
        self.labelLayout.addWidget(QtWidgets.QLabel("P7"))
        self.labelLayout.addWidget(QtWidgets.QLabel("O1"))
        self.labelLayout.addWidget(QtWidgets.QLabel("O2"))
        self.labelLayout.addWidget(QtWidgets.QLabel("P8"))
        self.labelLayout.addWidget(QtWidgets.QLabel("T8"))
        self.labelLayout.addWidget(QtWidgets.QLabel("FC6"))
        self.labelLayout.addWidget(QtWidgets.QLabel("F4"))
        self.labelLayout.addWidget(QtWidgets.QLabel("F8"))
        self.labelLayout.addWidget(QtWidgets.QLabel("AF4"))
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.labelLayout)
        self.layout.addLayout(self.grafikLayout)
        self.setLayout(self.layout)
        self.show()
    


class AnaPencere(QtWidgets.QMainWindow):
    def __init__(self):
        super(AnaPencere, self).__init__()
        uic.loadUi("C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\EEGAnalyzer\\EEG-Real-Time-Analyzer\\eeganalyzergui.ui", self)
        self.initUI()

        self.process = QtCore.QProcess(self) # Core'u başlatmak için QProcess kullan

        self.eegVeri_sideBarButton.clicked.connect(self.setPage0)
        self.eegKayit_sideBarButton.clicked.connect(self.setPage1)
        self.modelTest_sideBarButton.clicked.connect(self.setPage2)
        self.robotKol_sideBarButton.clicked.connect(self.setPage3)
        self.cihazaBaglanButton.clicked.connect(self.startCore)
        self.eegVeriAkisiButton.clicked.connect(self.startStream)


        self.grafikWidget = eegGraphWidget()
        # ScrollArea içine CustomWidget'ı ekle
        self.eegGrafik.setWidget(self.grafikWidget)
        self.num_graphs = 14
        self.data_lines = []
        self.max_points = 800
        self.data = [[0 for _ in range(self.max_points)] for _ in range(self.num_graphs)]
        for i in range(self.num_graphs):
            p = self.grafikWidget.eegGrafikler[i]
            pen = pg.mkPen(color=(255, 0, 0))
            data_line = p.plot(self.data[i], pen=pen)
            self.data_lines.append(data_line)

                # EEG veri akışı için thread
        self.eeg_stream_thread = EEGStreamThread()
        # Plot güncelleme için thread
        self.update_plot_thread = UpdatePlotThread(self.num_graphs, self.data_lines)
        # EEG veri akışı thread'inden gelen veriyi plot güncelleme thread'ine bağla
        self.eeg_stream_thread.new_eeg_data.connect(self.update_plot_thread.update_plot_data)


    
    def startStream(self):
        if not self.eeg_stream_thread.isRunning():
            self.eeg_stream_thread.start()
        if not self.update_plot_thread.isRunning():
            self.update_plot_thread.start()
    def startCore(self):
        self.process.start('powershell.exe', ['-NoExit', '-Command', 'cd C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\emotiv-lsl; python -m pipenv run python main.py'])
        print("Core Başlatıldı")
    def setPage0(self):
        self.contentBar.setCurrentIndex(0)
    def setPage1(self):
        self.contentBar.setCurrentIndex(1)  # Index numarası sayfanın 
    def setPage2(self):
        self.contentBar.setCurrentIndex(2)
    def setPage3(self):
        self.contentBar.setCurrentIndex(3)
    def initUI(self):
        # Arayüzünüzün özelleştirmelerini burada yapabilirsiniz.
        # Örneğin, arkaplan rengini ayarlamak için:
        self.setStyleSheet("background-color: #333;")

# Uygulamayı başlat
app = QtWidgets.QApplication(sys.argv)
ana_pencere = AnaPencere()
ana_pencere.show()
sys.exit(app.exec_())
# # Create the application
# app = QApplication(sys.argv)

# # Load the UI file

# ui = loadUi("C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\EEGAnalyzer\\EEG-Real-Time-Analyzer\\eeganalyzergui.ui")

# # Create the main window
# window = QMainWindow()
# window.setCentralWidget(ui)
# window.show()

# # Start the event loop
# sys.exit(app.exec_())