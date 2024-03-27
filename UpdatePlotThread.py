from PyQt5.QtCore import QThread


class UpdatePlotThread(QThread):
    def __init__(self, num_graphs, data_lines):
        super().__init__()
        self.num_graphs = num_graphs
        self.data_lines = data_lines
        # self.fs = 128  # Örnekleme frekansı (Hz)
        # self.fpass = 100  # Geçirme bandı frekansı (Hz)
        # self.n = 4  # Filtre derecesi
        # self.filtreStatus = False

        # # Chebyshev Type II alçak geçiren filtre tasarımı
        # self.b, self.a = cheby2(self.n, 40, self.fpass / (self.fs), 'low')
        # #eeg_data_filtered = filtfilt(b, a, eeg_data)
        self.data = [[] for _ in range(num_graphs)]

    def update_plot_data(self, eeg_data):
        for i in range(self.num_graphs):
            if len(self.data[i]) < 800:  # Eğer liste boyutu 800'den küçükse
                self.data[i].append(eeg_data[i])  # Yeni EEG değeri ekle
            else:  # Eğer liste boyutu 800'e ulaştıysa
                self.data[i] = self.data[i][1:]  # İlk değeri at
                self.data[i].append(eeg_data[i])  # Yeni EEG değeri ekle
            # if self.filtreStatus:
            #     self.data_lines[i].setData(filtfilt(self.b,self.a,self.data[i]))  # Grafiği güncelle
            # else:
            self.data_lines[i].setData(self.data[i])
            #self.data_lines[i].setData(filtfilt(self.b,self.a,self.data[i]))  # Grafiği güncelle
    def run(self):
        pass  # Bu thread, sinyaller üzerinden veri alacak