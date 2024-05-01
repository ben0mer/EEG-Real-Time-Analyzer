from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from modelapi import ModelAPI
import pandas as pd
import trainfunctions as tf


class EEGAnalyzeThread(QThread):
    predictResult = pyqtSignal(list)
    dataCounter = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.isRunning = False
        self.saveMode = False
        self.number_of_data = 1
        self.data_counter = 0
        self.eeg_data = []
        self.allResults = []

    def run(self):
        pass

    def processData(self):
        if not self.isRunning:
            return
        if self.saveMode:
            self.eeg_data.append(self.new_eeg_data)
            if len(self.eeg_data) == self.frequency:
                self.eeg_data = self.preprocess(self.eeg_data)
                self.result = self.model_api.tahmin(self.eeg_data, _probability=True, _threshold=self.threshold)
                print(self.result)
                self.allResults.append(self.result.tolist())
                self.data_counter += 1
                self.dataCounter.emit(self.data_counter)

                if len(self.allResults) == self.number_of_data:
                    #self.saveMode = False
                    self.allResults = self.processAllResults(self.allResults)
                    self.predictResult.emit(self.allResults)
                    self.allResults = []
                    self.eeg_data = []
                    self.data_counter = 0
                self.eeg_data = []
            return
        self.eeg_data.append(self.new_eeg_data)
        if len(self.eeg_data) == self.frequency:
            self.eeg_data = self.preprocess(self.eeg_data)
            self.result = self.model_api.tahmin(self.eeg_data, _probability=True, _threshold=self.threshold)
            print(self.result)
            self.predictResult.emit(self.result.tolist())
            self.eeg_data = []
    def processAllResults(self, allResults):
        zero_count = sum(1 for result in allResults if result[0][0] == 0)
        one_count = sum(1 for result in allResults if result[0][0] == 1)
        if zero_count > one_count:
            result_array= [0, zero_count/(zero_count+one_count)]
        elif zero_count == one_count:
            result_array = [-1,0.5]
        else:
            result_array = [1, one_count/(zero_count+one_count)]
        return result_array

    def startModel(self, model_path, frequency, _filter, channel, threshold):
        self.model_path = model_path
        self.frequency = frequency
        self.filter = _filter
        self.channel = channel
        self.threshold = threshold
        self.model_api = ModelAPI(self.model_path)
        self.isRunning = True
        # print("Model Başlatılıyor1")
        # self.start()
        # print("Model start edildi")

    def stopModel(self):
        self.isRunning = False
    
    def saveMultipleData(self, number_of_data):
        if self.saveMode:
            self.saveMode = False
            self.data_counter = 0
            self.allResults = []
            self.number_of_data = number_of_data
            return
        else:
            self.saveMode = True
            self.data_counter = 0
            self.allResults = []
            self.number_of_data = number_of_data
            return
        

    def preprocess(self, data):
        # Implement your preprocessing logic here
        preprocessed_data = pd.DataFrame(data)
        preprocessed_data = preprocessed_data.iloc[:,self.channel]
        preprocessed_data = pd.DataFrame(preprocessed_data)
        preprocessed_data = tf.ornekle(preprocessed_data, self.frequency)
        return preprocessed_data

    @pyqtSlot(list)
    def update_eeg_data(self, data):
        self.new_eeg_data = data
        self.processData()
        # Gelen EEG verilerini işle
        pass

    @pyqtSlot(float)
    def update_timestamp(self, time):
        self.timestamp = time
        # Gelen zaman damgasını işle
        pass