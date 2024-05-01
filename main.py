

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtGui

from EEGStreamThread import EEGStreamThread
from UpdatePlotThread import UpdatePlotThread
from RecordThread import EEGRecorder
from EEGAnalyzeThread import EEGAnalyzeThread
from EEGModelGame import EEGModelGame

class eegGraphWidget(QtWidgets.QWidget):
    # EEG verilerini çizmek için kullanılacak widget
    # 14 adet EEG verisi çizilecek 14 adet grafik alt alta olacak

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Arayüzün özelliklerini ayarla
        #ikon ayarla
        
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
        self.channelNames = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
        self.labelLayout = QVBoxLayout()
        for i in range(14):
            self.labelLayout.addWidget(QtWidgets.QLabel(self.channelNames[i]))

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
        self.setWindowIcon(QtGui.QIcon("C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\EEGAnalyzer\\EEG-Real-Time-Analyzer\\resources\\eeglogo3.png"))
        self.process = QtCore.QProcess(self) # Core'u başlatmak için QProcess kullan

        self.eegVeri_sideBarButton.clicked.connect(self.setPage0)
        self.eegKayit_sideBarButton.clicked.connect(self.setPage1)
        self.modelTest_sideBarButton.clicked.connect(self.setPage2)
        self.robotKol_sideBarButton.clicked.connect(self.setPage3)
        self.cihazaBaglanButton.clicked.connect(self.startCore)
        self.cikisButton.clicked.connect(self.close)
        #self.eegVeriAkisiButton.clicked.connect(self.startStream)


        ''' EEG verilerini çizdirmek için widget işlemleri'''
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

        ''' EEG kayıt işlemleri için thread ayarları'''
        self.eeg_save_thread = EEGRecorder()
        self.kayitBaslat.clicked.connect(self.startRecording)
        self.kayitDuraklat.clicked.connect(self.pauseRecording)
        self.kayitBitir.clicked.connect(self.stopRecording)
        self.kayitDuraklat.setEnabled(False)
        self.kayitBitir.setEnabled(False)
        self.eeg_stream_thread.new_eeg_data.connect(self.eeg_save_thread.update_eeg_data)
        self.eeg_stream_thread.timestamp.connect(self.eeg_save_thread.update_timestamp)
        self.eeg_save_thread.durumDegisti.connect(self.updateDurumLabel)
        self.eeg_save_thread.kalanSureDegisti.connect(self.updateKalanSureLabel)
        self.kayitButonAyar(False)

        ''' EEG model test işlemleri için thread ayarları'''
        self.eeg_analyze_thread = EEGAnalyzeThread()
        self.eeg_analyze_thread.predictResult.connect(self.updatePredictions)
        self.eeg_stream_thread.new_eeg_data.connect(self.eeg_analyze_thread.update_eeg_data)
        self.eeg_stream_thread.timestamp.connect(self.eeg_analyze_thread.update_timestamp)
        # Butonları bağlama
        self.modelBaslat.clicked.connect(self.startModel)
        self.modelDurdur.clicked.connect(self.stopModel)
        self.tahminValue = "0"
        self.tahminYuzdeValue = "0"
        self.tahminSonucValue = "0"
        self.prevTahminValue = "0"
        self.prevTahminYuzdeValue = "0"
        self.prevTahminSonucValue = "0"
        self.tahminLabel.setText(self.tahminValue)
        self.tahminYuzdeLabel.setText(self.tahminYuzdeValue)
        self.tahminSonucLabel.setText(self.tahminSonucValue)
        #Renkleri 8BFF00 yap
        self.tahminLabel.setStyleSheet("color: #8BFF00;")
        self.tahminYuzdeLabel.setStyleSheet("color: #8BFF00;")
        self.tahminSonucLabel.setStyleSheet("color: #8BFF00;")
        self.prevTahminLabel.setText(self.prevTahminValue)
        self.prevTahminYuzdeLabel.setText(self.prevTahminYuzdeValue)
        self.prevTahminSonucLabel.setText(self.prevTahminSonucValue)
        #Renkleri F3FF00 yap
        self.prevTahminLabel.setStyleSheet("color: #F3FF00;")
        self.prevTahminYuzdeLabel.setStyleSheet("color: #F3FF00;")
        self.prevTahminSonucLabel.setStyleSheet("color: #F3FF00;")
        # VERİ KAYDET BUTONU
        self.modelVeriKaydet.clicked.connect(self.saveModelData)
        self.modelVeriSayisiLabel.setText("0")
        self.eeg_analyze_thread.dataCounter.connect(self.updateDataCounterLabel)

        # Model teste oyun widgetını ekleme
        self.oyunWidget = EEGModelGame()
        self.modelOyun.setWidget(self.oyunWidget)
        self.modelAyarlaButon.clicked.connect(self.modelKontrolAyarla)
        self.modelKonumSifirla.clicked.connect(self.oyunWidget.konumSifirla)
        self.oyunWidget.hedefeUlasti.connect(self.hedefSinyal)
        self.SagMesaj = "<SAG>"
        self.SolMesaj = "<SOL>"
        self.robotSinyalGonder = 0
        self.topHareket = 0
        self.modelTopHareket.stateChanged.connect(self.topHareketAyarla)
        self.modelRobotSinyal.stateChanged.connect(self.robotSinyalAyarla)
        self.modelSolBtn.clicked.connect(self.oyunWidget.moveLeft)
        self.modelSagBtn.clicked.connect(self.oyunWidget.moveRight)

    def close(self):
        self.process.kill()
        sys.exit()
    def topHareketAyarla(self, state):
        self.topHareket = state
        print(f"Top Hareket Ayarlandı: {self.topHareket}")
    
    def robotSinyalAyarla(self, state):
        self.robotSinyalGonder = state
        print(f"Robot Sinyal Ayarlandı: {self.robotSinyalGonder}")

    def sendUartCommand(self, command):
        pass
    @pyqtSlot(int)
    def hedefSinyal(self, hedef):
        print(f"Hedefe Ulaşıldı {hedef}")
        if self.robotSinyalGonder == 2:
            self.sendUartCommand(hedef)
        pass

    def modelKontrolAyarla(self):

        self.adimSayisi = int(self.modelAdimSayisi.text())
        self.SagMesaj = str(self.modelSagMesaj.text())
        self.SolMesaj = str(self.modelSolMesaj.text())
        self.oyunWidget.setGameSettings(self.adimSayisi)

    @pyqtSlot(list)
    def updatePredictions(self, predictions):
        print(predictions)
        self.modelLabelSet(predictions)
        if self.topHareket == 2:
            try:
                if predictions[0][0] == 0:
                    self.oyunWidget.moveLeft()
                elif predictions[0][0] == 1:
                    self.oyunWidget.moveRight()
            except:
                if predictions[0] == 0:
                    self.oyunWidget.moveLeft()
                elif predictions[0] == 1:
                    self.oyunWidget.moveRight()
        pass

    @pyqtSlot(int)
    def updateDataCounterLabel(self, counter):
        self.modelVeriSayisiLabel.setText(str(counter))

    def saveModelData(self):

        self.eeg_analyze_thread.saveMultipleData(int(self.modelVeriSayisi.text()))

    def modelLabelSet(self, prediction):
        self.prevTahminValue = self.tahminValue
        self.prevTahminYuzdeValue = self.tahminYuzdeValue
        self.prevTahminSonucValue = self.tahminSonucValue
        self.prevTahminLabel.setText(self.prevTahminValue)
        self.prevTahminYuzdeLabel.setText(self.prevTahminYuzdeValue)
        self.prevTahminSonucLabel.setText(self.prevTahminSonucValue)
        try:
            self.tahminValue = str(prediction[0][0])
            self.tahminYuzdeValue = str(prediction[0][1])
            if prediction[0][0]==0:
                self.tahminSonucValue = "Sol"
            elif prediction[0][0]==1:
                self.tahminSonucValue = "Sağ"
            else:
                self.tahminSonucValue = "Bilinmiyor"
        except:
            self.tahminValue = str(prediction[0])
            self.tahminYuzdeValue = str(prediction[1])
            if prediction[0]==0:
                self.tahminSonucValue = "Sol"
            elif prediction[0]==1:
                self.tahminSonucValue = "Sağ"
            else:
                self.tahminSonucValue = "Bilinmiyor"

        self.tahminLabel.setText(self.tahminValue)
        self.tahminYuzdeLabel.setText(self.tahminYuzdeValue)
        self.tahminSonucLabel.setText(self.tahminSonucValue)

    def startModel(self):
        self.modelPathValue = self.modelPath.text()
        self.modelFrequencyValue = int(self.modelFrequency.text())
        self.modelFilterValue = self.modelFilter.text()
        self.modelChannelValue = int(self.modelChannel.text())
        self.modelThresholdValue = float(self.modelThreshold.text())
        print("Model Başlatılıyor")
        self.eeg_analyze_thread.startModel(self.modelPathValue, self.modelFrequencyValue, self.modelFilterValue, self.modelChannelValue, self.modelThresholdValue)
        print("Model Başlatıldı")
        pass
    def stopModel(self):
        self.eeg_analyze_thread.stopModel()
        pass

    @pyqtSlot(str)
    def updateDurumLabel(self, text):
        if text == "Kayit Hazir":
            self.kayitButonAyar(False)
        self.kayitDurumLabel.setText(text)
    @pyqtSlot(str)
    def updateKalanSureLabel(self, text):
        self.kayitKalanSureLabel.setText(text)

    def startRecording(self):
        self.record_time = int(self.kayitSureLine.text())
        self.record_title = self.kayitBaslikLine.text()
        self.eeg_save_thread.startRecording(self.record_time, self.record_title)
        self.kayitButonAyar(True)
        pass
    def pauseRecording(self):
        self.eeg_save_thread.pauseRecording()
        pass
    def stopRecording(self):
        self.eeg_save_thread.stopRecording()
        self.kayitButonAyar(False)
        pass
    def kayitButonAyar(self, durum):
        if not durum:
            self.kayitBaslat.setEnabled(True)
            self.kayitDuraklat.setEnabled(False)
            self.kayitBitir.setEnabled(False)
            #Butonların renkkerşini ayarla
            #self.kayitBaslat.setStyleSheet("background-color: #4CAF50; color: white;")
            self.kayitDuraklat.setStyleSheet("background-color: #ADADAD; color: white;")
            self.kayitBitir.setStyleSheet("background-color: #ADADAD; color: white;")
            #kayit baslat butonunun rengini normal yap
            self.kayitBaslat.setStyleSheet("background-color: #3daee9; color: white;")
        else:
            self.kayitBaslat.setEnabled(False)
            self.kayitDuraklat.setEnabled(True)
            self.kayitBitir.setEnabled(True)
            self.kayitBaslat.setStyleSheet("background-color: #ADADAD; color: white;")
            self.kayitDuraklat.setStyleSheet("background-color: #EEAB2A; color: white;")
            self.kayitBitir.setStyleSheet("background-color: #C6423A; color: white;")
        pass

    def startStream(self):
        if not self.eeg_stream_thread.isRunning():
            self.eeg_stream_thread.start()
        if not self.update_plot_thread.isRunning():
            self.update_plot_thread.start()
    def startCore(self):
        self.process.start('powershell.exe', ['-NoExit', '-Command', 'cd C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\emotiv-lsl; python -m pipenv run python main.py'])
        self.startStream()
        self.updateConnectionStatus(1)
        print("Core Başlatıldı")
    def updateConnectionStatus(self, status):
        if status == 1:
            self.cihazDurum.setText("Bağlandı")
            self.cihazaBaglanButton.setEnabled(False)
        else:
            self.cihazDurum.setText("Bağlı Değil")
            self.cihazaBaglanButton.setEnabled(True)
        pass
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