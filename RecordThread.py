from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from scipy.io import savemat
class EEGRecorder(QThread):
    durumDegisti = pyqtSignal(str)
    kalanSureDegisti = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.record_time = 0
        self.record_title = ""
        self.status = "stopped"
        self.new_eeg_data = pyqtSignal(list)
        self.timestamp = pyqtSignal(float)
        self.update_remaining_time = pyqtSignal(int)
        
        self.eeg_data = []
        self.start_time = 0
        self.kalan_sure = 0
        self.paused_time = 0
        self.newData = False

    def run(self):
        self.start_time = self.timestamp
        self.eeg_data = []
        while True:
            if self.status == "stopped":
                # Thread'i durdur
                savemat(f'{self.record_title}.mat', {'eeg_data': self.eeg_data})
                print("Recording stop1")
                self.paused_time = 0
                #self.terminate()
                break
            if self.status == "paused":
                #kayıt durdurulduğu zaman geçen süreyi kaydet
                self.paused_time = self.timestamp - self.start_time
                print("Recording paused")
                continue
            if self.status == "recording":
                if self.paused_time != 0:
                    self.start_time = self.start_time+(self.paused_time - self.kalan_sure)
                    self.paused_time = 0
                if self.newData:
                    self.eeg_data.append(self.new_eeg_data)
                    self.newData = False
                print(f"{self.new_eeg_data} ****")
                self.kalan_sure = self.timestamp - self.start_time
                #self.update_remaining_time.emit(self.kalan_sure)
                print(self.kalan_sure)
                self.kalanSureDegisti.emit(str(self.kalan_sure))
                if self.kalan_sure > self.record_time:
                    savemat(f'{self.record_title}.mat', {'eeg_data': self.eeg_data})
                    self.status = "stopped"
                    print("Recording end")
                    self.durumDegisti.emit("Kayit Hazir")
                    break
    
    # EEG DATA KAYIT VE LİSTEYE EKLEME İŞLEMLERİNİ AŞAĞIDAKİ FONKSİYONLARIN İÇİNDE YAP!
    @pyqtSlot(list)
    def update_eeg_data(self, data):
        self.new_eeg_data = data
        self.newData = True
        # Gelen EEG verilerini işle
        pass

    @pyqtSlot(float)
    def update_timestamp(self, time):
        self.timestamp = time
        # Gelen zaman damgasını işle
        pass

    def startRecording(self, record_time, record_title):
        self.record_time = record_time
        self.record_title = record_title
        self.status = "recording"
        print("Recording started")
        self.durumDegisti.emit("Kayit Ediliyor")
        self.start()


        pass
    def pauseRecording(self):
        if self.status == "paused":
            self.status = "recording"
            print("Recording resumed")
            self.durumDegisti.emit("Kayit Ediliyor")
        else:
            self.status = "paused"
            self.durumDegisti.emit("Kayit Duraklatildi")
        print("Recording paused")
        pass
    def stopRecording(self):
        self.status = "stopped"
        print("Recording stopped")
        self.durumDegisti.emit("Kayit Hazir")
        pass



