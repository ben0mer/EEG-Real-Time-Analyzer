import joblib
import trainfunctions as tf
import numpy as np
import pandas as pd
import scipy.io
from pylsl import StreamInlet, resolve_stream
class ModelAPI:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
    
    def tahmin(self, input_data, _probability=False, _threshold=-1.0):
        # Preprocess the input data if needed
        preprocessed_data = self.preprocess(input_data)
        
        # Make predictions using the loaded model
        if _probability:
            predictions = self.model.predict_proba(preprocessed_data)
            print(predictions)
            # Apply thresholding if needed
            predictions = self.threshold(predictions, _threshold)
                
        else:
            predictions = self.model.predict_proba(preprocessed_data)
            # Apply thresholding if needed
            predictions = self.threshold(predictions, _threshold)
            #sadece 0. sütunu al
            predictions = predictions[:,0]

        # Postprocess the predictions if needed
        postprocessed_predictions = self.postprocess(predictions)
        
        return postprocessed_predictions
    
    def preprocess(self, input_data):
        # Implement your preprocessing logic here
        preprocessed_data = tf.ozellikCikar(input_data)
        preprocessed_data = preprocessed_data.dropna()
        return preprocessed_data
    
    def threshold(self, predictions, threshold):
        if not threshold == -1:
            # 0. ve 1. sütunları threshold'a göre karşılaştır ve büyük olanı 0. sütundaki ise geçici değişkene 0 ata, büyük olan 1. sütundaki ise geçici değişkene 1 ata, şart sağlanmazsa -1 yaz
            predictions_new = np.where(predictions[:, 0] > threshold, 0, np.where(predictions[:, 1] > threshold, 1, -1))
            # 0. ve 1. sütunları karşılaştır, büyük olanı 1. sütuna ata
            predictions[:, 1] = np.where(predictions[:, 0] > predictions[:, 1], predictions[:, 0], predictions[:, 1])                # predictions_new'deki değeri predictions'ın 0. sütununa ata
            predictions[:, 0] = predictions_new
        else:
            
            # 0. ve 1. sütunları karşılaştır, büyük olanı 1. sütuna ata
            predictions_new = np.where(predictions[:, 0] > predictions[:, 1], predictions[:, 0], predictions[:, 1])
            # predictions değişkeninde 0. ve 1. sütundaki değerleri karşılaştır, 0. sütundaki değer büyükse 0. sütundaki değeri 0 yap, 1. sütundaki değer büyükse 0. sütundaki değeri 1 yap
            predictions[:, 0] = np.where(predictions[:, 0] > predictions[:, 1], 0, 1)
            predictions[:, 1] = predictions_new
            # predictions_new'deki değeri predictions'ın 1. sütununa ata                predictions[:, 1] = predictions_new
        return predictions

    def postprocess(self, predictions):
        # Implement your postprocessing logic here
        postprocessed_predictions = predictions
        
        return postprocessed_predictions

# Usage
# model_path = "exported_models//RandomForestClassifier()-7-O2.pkl"
# model_api = ModelAPI(model_path)

# Test data
#yeni .mat dosyasını yükle
# yeni_veri = scipy.io.loadmat('data/sag_omer2.mat')
# #yeni verinin sadece eeg_data kısmını ve 6. sutunu al
# yeni_veri = pd.DataFrame(yeni_veri['eeg_data'])
# yeni_veri = yeni_veri.iloc[:,7]
# yeni_veri = pd.DataFrame(yeni_veri)
# yeni_veri = tf.ornekle(yeni_veri, 160)

# Veri streamden başlat

# def make_prediction(yeni_veri):
#     predictions = model_api.tahmin(yeni_veri,_probability=True)
#     print(predictions)

    
# streams = resolve_stream('type', 'EEG')
# inlet = StreamInlet(streams[0])
# sample, timestamp = inlet.pull_sample()
# eeg_data = []
# while True:
#     sample, timestamp = inlet.pull_sample()
#     sample = [el / 1000000 for el in sample]
#     eeg_data.append(sample)
#     # EEG verisi 160 satır olup olmadığını kontrol et
#     if len(eeg_data) == 160:
#         # eeg_data verisinin 7. sütununu al
#         yeni_veri = pd.DataFrame(eeg_data)
#         yeni_veri = yeni_veri.iloc[:,7]
#         yeni_veri = pd.DataFrame(yeni_veri)
#         yeni_veri = tf.ornekle(yeni_veri, 160)
#         print(yeni_veri)
#         make_prediction(yeni_veri)
#         eeg_data = []


# Make predictions
# predictions = model_api.tahmin(yeni_veri, _threshold=0.8)
# print(predictions)
