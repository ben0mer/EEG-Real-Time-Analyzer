import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QGridLayout, QScrollArea, QLabel, QLineEdit)
import pyqtgraph as pg
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import QThread, pyqtSignal
from pylsl import StreamInlet, resolve_stream
from scipy.signal import cheby2, filtfilt
from scipy.io import savemat
import time
class EEGStreamThread(QThread):
    new_eeg_data = pyqtSignal(list)
    def run(self):
        streams = resolve_stream('type', 'EEG')
        inlet = StreamInlet(streams[0])
        while True:
            sample, timestamp = inlet.pull_sample()
            sample = [el / 1000000 for el in sample]
            self.new_eeg_data.emit(sample)

#EEG verilerini kaydedecek thread
class EEGSaveThread(QThread):
    update_remaining_time = pyqtSignal(int)
    def run(self):
        streams = resolve_stream('type', 'EEG')
        inlet = StreamInlet(streams[0])
        sample, timestamp = inlet.pull_sample()
        start_time = timestamp
        eeg_data = []
        sample = [el / 1000000 for el in sample]
        eeg_data.append(sample)
        while True:
            sample, timestamp = inlet.pull_sample()
            sample = [el / 1000000 for el in sample]
            eeg_data.append(sample)
            self.kalan_sure = timestamp - start_time
            self.update_remaining_time.emit(self.kalan_sure)
            if self.kalan_sure > self.record_time:
                savemat(f'{self.record_title}.mat', {'eeg_data': eeg_data})
                break
name = "omer"
class UpdatePlotThread(QThread):
    def __init__(self, num_graphs, data_lines):
        super().__init__()
        self.num_graphs = num_graphs
        self.data_lines = data_lines
        self.fs = 128  # Örnekleme frekansı (Hz)
        self.fpass = 100  # Geçirme bandı frekansı (Hz)
        self.n = 4  # Filtre derecesi
        self.filtreStatus = False

        # Chebyshev Type II alçak geçiren filtre tasarımı
        self.b, self.a = cheby2(self.n, 40, self.fpass / (self.fs), 'low')
        #eeg_data_filtered = filtfilt(b, a, eeg_data)
        self.data = [[] for _ in range(num_graphs)]

    def update_plot_data(self, eeg_data):
        for i in range(self.num_graphs):
            if len(self.data[i]) < 800:  # Eğer liste boyutu 800'den küçükse
                self.data[i].append(eeg_data[i])  # Yeni EEG değeri ekle
            else:  # Eğer liste boyutu 800'e ulaştıysa
                self.data[i] = self.data[i][1:]  # İlk değeri at
                self.data[i].append(eeg_data[i])  # Yeni EEG değeri ekle
            if self.filtreStatus:
                self.data_lines[i].setData(filtfilt(self.b,self.a,self.data[i]))  # Grafiği güncelle
            else:
                self.data_lines[i].setData(self.data[i])
            #self.data_lines[i].setData(filtfilt(self.b,self.a,self.data[i]))  # Grafiği güncelle
    def run(self):
        pass  # Bu thread, sinyaller üzerinden veri alacak

class LiveGraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)


        # Kontrol paneli için widget'lar
        self.start_button = QPushButton('Başlat')
        self.stop_button = QPushButton('Durdur')
        self.reset_button = QPushButton('Sıfırla')
        self.core_start_button = QPushButton('Core Başlat')
        self.filtre_button = QPushButton('Filtrele')
        
        # Kayıt süresi için değişken girilecek text box öğesi
        self.record_time = 0
        self.record_title = "Basliksiz"
        self.record_time_text = QLineEdit(parent=self)
        self.record_time_label = QLabel('Kayıt Süresi: ', parent=self)
        self.record_title_text = QLineEdit(parent=self)
        self.record_title_label = QLabel('Kayıt İsmi: ', parent=self)
        self.record_button = QPushButton('Kayıt Al')
        self.remaining_time_label = QLabel('Kalan Süre: ', parent=self)

        # Butonların tıklanma olaylarını bağla
        self.start_button.clicked.connect(self.start_threads)
        self.stop_button.clicked.connect(self.stop_threads)
        self.reset_button.clicked.connect(self.reset_plot)
        self.core_start_button.clicked.connect(self.start_core)
        self.filtre_button.clicked.connect(self.filtrele)
        self.record_button.clicked.connect(self.record)

        self.process = QProcess(self)  # QProcess nesnesi oluştur
        
        # Kontrol panelini layout'a ekle
        self.layout.addWidget(self.start_button, 0, 0)
        self.layout.addWidget(self.stop_button, 1, 0)
        self.layout.addWidget(self.reset_button, 2, 0)
        self.layout.addWidget(self.core_start_button, 3, 0)
        self.layout.addWidget(self.filtre_button, 4, 0)
        self.layout.addWidget(self.record_button, 7, 0,1,2)
        self.layout.addWidget(self.record_time_label, 5, 0)
        self.layout.addWidget(self.record_time_text, 5, 1)
        self.layout.addWidget(self.record_title_label, 6, 0)
        self.layout.addWidget(self.record_title_text, 6, 1)
        self.layout.addWidget(self.remaining_time_label, 8, 0, 1, 2)

        # Grafikler için widget
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.graphWidget.setBackground('w')  # Arka planı beyaz yap
        self.graphWidget.setFixedHeight(1920)  # Genişliği ayarla
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)  # Widget'in boyutunu otomatik ayarla
        self.scroll.setWidget(self.graphWidget)
        self.layout.addWidget(self.scroll, 0, 3, 14, 5)  # 14 
        #self.layout.addWidget(self.graphWidget, 0, 1, 14, 1)  # 14 satırı ve 1 sütunu kaplasın

        self.num_graphs = 14
        self.data_lines = []
        self.max_points = 800
        self.data = [[random.randint(0, 100) for _ in range(self.max_points)] for _ in range(self.num_graphs)]

        for i in range(self.num_graphs):
            p = self.graphWidget.addPlot(row=i, col=0)
            # vb = p.getViewBox()
            # vb.setBackgroundColor('w')  # ViewBox arka planını beyaz yapar
            pen = pg.mkPen(color=(255, 0, 0))
            data_line = p.plot(self.data[i], pen=pen)
            self.data_lines.append(data_line)

        
        # EEG veri akışı için thread
        self.eeg_stream_thread = EEGStreamThread()
        # Plot güncelleme için thread
        self.update_plot_thread = UpdatePlotThread(self.num_graphs, self.data_lines)

        # EEG veri akışı thread'inden gelen veriyi plot güncelleme thread'ine bağla
        self.eeg_stream_thread.new_eeg_data.connect(self.update_plot_thread.update_plot_data)
        
        self.eeg_save_thread = EEGSaveThread()
        self.eeg_save_thread.update_remaining_time.connect(self.update_remaining_label)

        #self.timer.start()

    def update_remaining_label(self, kalan_sure):
        self.remaining_time_label.setText(f'Kalan Süre: {self.record_time-kalan_sure}')
    def record(self):
        # Küçük bir kayıt penceresi aç
        self.record_time = int(self.record_time_text.text())
        self.record_title = self.record_title_text.text()


        self.eeg_save_thread.record_time = self.record_time
        self.eeg_save_thread.record_title = self.record_title
        self.eeg_save_thread.start()
        print("Kayıt Başladı")

    def filtrele(self):
        self.update_plot_thread.filtreStatus = not self.update_plot_thread.filtreStatus

    def start_threads(self):
        if not self.eeg_stream_thread.isRunning():
            self.eeg_stream_thread.start()
        if not self.update_plot_thread.isRunning():
            self.update_plot_thread.start()
    def start_core(self):
        self.process.start('powershell.exe', ['-NoExit', '-Command', 'cd C:\\Users\\omerg\\Desktop\\BITIRME\\DenemeDosyalar\\emotiv-lsl; python -m pipenv run python main.py'])
        print("Core Başlatıldı")
    def stop_threads(self):
        if self.eeg_stream_thread.isRunning():
            self.eeg_stream_thread.terminate()
        if self.update_plot_thread.isRunning():
            self.update_plot_thread.terminate()
    def reset_plot(self):
        self.data = [[random.randint(0, 100) for _ in range(self.max_points)] for _ in range(self.num_graphs)]
        for i in range(self.num_graphs):
            self.data_lines[i].setData(self.data[i])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LiveGraphWindow()
    main.show()
    sys.exit(app.exec_())
