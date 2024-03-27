from PyQt5.QtCore import QThread, pyqtSignal
from pylsl import StreamInlet, resolve_stream
class EEGStreamThread(QThread):
    new_eeg_data = pyqtSignal(list)
    def run(self):
        streams = resolve_stream('type', 'EEG')
        inlet = StreamInlet(streams[0])
        while True:
            sample, timestamp = inlet.pull_sample()
            sample = [el / 1000000 for el in sample]
            self.new_eeg_data.emit(sample)