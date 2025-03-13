import pandas as pd
from pylab import *
import pywt

def delete_VCH(X_raw):
    signal = X_raw
    v = 'bior4.4'
    thres = [0.6]
    for w in thres:
        def lowpassfilter(signal, thresh, wavelet=v):
            thresh = thresh * nanmax(signal)
            coeff = pywt.wavedec(signal, wavelet, level=8, mode="per")
            coeff[1:] = (pywt.threshold(i, value=thresh, mode='soft') for i in coeff[1:])
            reconstructed_signal = pywt.waverec(coeff, wavelet, mode="per")
            return reconstructed_signal

        #fig, ax = subplots(figsize=(8, 4))
        #ax.plot(signal, color="b", alpha=0.5, label='Оригинальный сигнал')
        rec = lowpassfilter(signal, w)
        #ax.plot(rec, 'r', label='DWT преобразование сигнала', linewidth=2)
        #ax.legend()
        #ax.set_title('Удаление высокочастотного шума с помощью вейвлета :%s\n для порога детализации %s' % (v, w),
        #             fontsize=12)
        #ax.set_ylabel('Амплитуда сигнала', fontsize=12)
        #ax.set_xlabel('Время', fontsize=12)
    return rec