import numpy as np
import pandas as pd
from scipy.signal import cheby2, filtfilt,cheb2ord
from scipy.stats import kurtosis, skew, iqr, gmean, hmean
from scipy.linalg import svd

"""
Bu modül eğitim verilerini hazırlamak için kullanılır.
"""

def createFeatures(data):
    features = []
    # Basıklık
    features.append(kurtosis(data))
    # Çarpıklık
    features.append(skew(data))
    # *IQR
    features.append(iqr(data))
    # DK
    features.append(100*np.mean(data)/np.std(data))

    # # Geometrik Ortalama
    # features.append(gmean(data))


    # # Harmonik Ortalama
    # features.append(hmean(data))


    # Hjort Parametreleri Aktivite - Hareketlilik - Karmaşıklık
        # Activity is the variance of the signal
    activity = np.var(data)
    # Mobility is the square root of the variance of the first derivative
    # divided by the activity
    first_derivative = np.diff(data)
    mobility = np.sqrt(np.var(first_derivative) / activity)
    
    # Complexity is the mobility of the first derivative divided by the mobility
    # of the original signal
    second_derivative = np.diff(first_derivative)
    complexity = np.sqrt(np.var(second_derivative) / np.var(first_derivative)) / mobility
    features.append(activity)
    features.append(mobility)
    features.append(complexity)
    # Maxiumum
    features.append(np.max(data))
    # Minimum
    features.append(np.min(data))
    # Medyan
    features.append(np.median(data))
    # Ortalama Mutlak Sapma
    features.append(np.mean(np.absolute(data - np.mean(data))))
    # Merkezi Moment
    features.append(np.mean((data - np.mean(data))**10))
    # Ortalama
    features.append(np.mean(data))
    # Ortalama Eğri Uzunluğu
    features.append(np.mean(np.diff(data)))
    # Ortalama Enerji
    features.append(np.mean(data**2))
    # Ortalama Karekök
    rms = np.sqrt(np.mean(np.square(data)))
    features.append(rms)
    # Standart Hata
    features.append(np.std(data, ddof=1) / np.sqrt(len(data)))
    # Standart Sapma
    features.append(np.std(data, ddof=1))
    # Şekil Faktörü
    mean_power = np.mean(np.square(data))
    features.append((rms ** 2) / mean_power)

    # Tekil Değer Ayrışımı
    data_array = np.array(data).reshape(-1, 1)
    # Tekil değer ayrışımını uygula
    U, s, Vt = svd(data_array, full_matrices=False)
    features.append(s[0])

    # %25 Kırpılmış Ortalama
    # features.append(np.mean(data[np.abs(data - np.mean(data)) < (0.25 * np.std(data))]))
    # %50 Kırpılmış Ortalama
    features.append(np.mean(data[np.abs(data - np.mean(data)) < (0.50 * np.std(data))]))
    # Ortalama Teager Enerjisi
    teager_energy = [data[i]**2 - data[i-1] * data[i+1] for i in range(1, len(data) - 1)]
    
    # Ortalama Teager enerjisini hesapla
    features.append(np.mean(teager_energy))
    return np.array(features)

def filtrele(data):
    """
    Bu fonksiyon, verilen data DataFrame'ini filtreler.
        fs = 256     --> Örnekleme frekansı (Hz)
        fpass = 40  --> Geçirme bandı frekansı (Hz)
        n = 4        --> Filtre derecesi
    """
    fs = 256  # Örnekleme frekansı (Hz)
    fpass = 90  # Geçirme bandı frekansı (Hz)
    fstop = 100  # Duran frekans (Hz)
    Rp = 1  # Geçiş bölgesi ripleme (dB)
    Rs = 60  # Duruş bölgesi sönümleme (dB)
    n, Wn = cheb2ord(fpass / (fs / 2), fstop / (fs / 2), Rp, Rs) #min order ve Wn değerinin tespiti
                                                            # n= 4 de seçilebilir.
    # Chebyshev Type II alçak geçiren filtre tasarımı
    b, a = cheby2(n, Rs,Wn, 'low')

    eeg_data_filtered = filtfilt(b, a, data) # Filtreleme işlemi
    return eeg_data_filtered

# Veriyi epoklama
def ornekle(data, sample):
    """
    Bu fonksiyon, verilen data DataFrame'ini sample boyutunda parçalara ayırır
    ve her parçayı yeni bir sütuna yerleştirir.
    """
    # Data'nın boyutunu alalım
    x, y = data.shape
    
    # Tam bölünebilmesi için kırpma işlemleri yapalım
    satir_yeni = x // sample
    data = data.iloc[0:(satir_yeni * sample), :]
    
    # Data'yı sample boyutunda parçalara ayıralım
    data = data.values.reshape(satir_yeni, sample, y)
    
    # Her bir parçayı yeni bir sütuna yerleştirelim
    data_out = pd.DataFrame(data.reshape(-1, y * sample))
    
    return data_out
def ozellikCikar(data):
    """
    Bu fonksiyon, verilen data DataFrame'inden özellikler çıkarır.
    """
    # Özellikleri saklamak için bir liste oluşturalım
    features = []
    
    # Her bir epok için özellikleri çıkaralım
    for i in range(data.shape[0]):
        # Özellikleri çıkaralım
        features.append(createFeatures(data.iloc[i, :]))
    
    # Özellikleri bir DataFrame'e dönüştürelim
    features = pd.DataFrame(features)
    
    return features

def cevapHazirla(data, cevap):
    """
    Bu fonksiyon, verilen data ve cevap DataFrame'lerini birleştirir.
    """
    # Data boyutu ile aynı satır sayısına sahip bir cevap DataFrame'i oluşturalım
    cevap = pd.DataFrame(np.full((data.shape[0], 1), cevap))
    # Data ve cevap DataFrame'lerini birleştirelim
    data = pd.concat([data, cevap], axis=1) 

    return data

def temizle(data):
    """
    NaN inf vs. içeren sütunları temizler.
    """
    # NaN, inf vs. içeren sütunları temizler.
    data = data.replace([np.inf, -np.inf], np.nan)
    #hangi sütunlarda nan var
    nan_columns = data.columns[data.isna().any()].tolist()
    print("NaN içeren sütunlar: ", nan_columns)
    data = data.dropna(axis=1)
    
    return data