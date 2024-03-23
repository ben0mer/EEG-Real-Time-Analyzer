from pylsl import StreamInlet, resolve_stream
from scipy.io import savemat

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    # Collect a set number of samples for export
    eeg_data = []
    for _ in range(128 * 10):  # 10 Saniyelik veri toplama
        sample, timestamp = inlet.pull_sample()
        sample = [el / 1000000 for el in sample] # microvolt a çevirme
        eeg_data.append(sample)
        

    # Save the data to a .mat file
    savemat('eeg_data1.mat', {'eeg_data': eeg_data})

if __name__ == '__main__':
    main()