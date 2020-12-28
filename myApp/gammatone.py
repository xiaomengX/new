import numpy as np
import pywt
import scipy.io.wavfile as wf
from itertools import chain
def cochleagram_fft_coefs(sr, win_len, channel_number):
    min_freq = 50.0
    max_freq = sr//2
    max_len = win_len
    nfilts = channel_number
    nfft = win_len

    wts = np.zeros((nfilts, nfft // 2 + 1))
    ear_q = 9.26449
    min_bw = 24.7
    order = 1.0
    cfreqs = -(ear_q * min_bw) + np.exp(np.arange(1, nfilts+1, 1) * (-np.log(max_freq+ear_q*min_bw) + np.log(min_freq + ear_q*min_bw)) / nfilts) * (max_freq + ear_q*min_bw)
    cfreqs = np.flipud(cfreqs)
    GTord = 4.0
    ucirc = np.exp(2j * np.pi * np.arange(0, nfft//2+1, 1)/nfft)

    for i in range(nfilts):
        cf = cfreqs[i]
        erb = 1.0 * np.power((np.power(cf/ear_q, order) + min_bw ** order), 1.0/order)
        b = 1.019 * 2 * np.pi * erb
        r = np.exp(-b / sr)
        theta = 2 * np.pi * cf / sr
        pole = r * np.exp(1j * theta)

        t = 1. / sr

        a11 = -(2 * t * np.cos(2 * cf * np.pi * t) / np.exp(b * t) + 2 * np.sqrt(3 + 2 ** 1.5) * t * np.sin(
            2 * cf * np.pi * t) / np.exp(b * t)) / 2
        a12 = -(2 * t * np.cos(2 * cf * np.pi * t) / np.exp(b * t) - 2 * np.sqrt(3 + 2 ** 1.5) * t * np.sin(
            2 * cf * np.pi * t) / np.exp(b * t)) / 2
        a13 = -(2 * t * np.cos(2 * cf * np.pi * t) / np.exp(b * t) + 2 * np.sqrt(3 - 2 ** 1.5) * t * np.sin(
            2 * cf * np.pi * t) / np.exp(b * t)) / 2
        a14 = -(2 * t * np.cos(2 * cf * np.pi * t) / np.exp(b * t) - 2 * np.sqrt(3 - 2 ** 1.5) * t * np.sin(
            2 * cf * np.pi * t) / np.exp(b * t)) / 2

        zros = -1 * np.column_stack((a11, a12, a13, a14))/t
        p1 = (-2 * np.exp(4j * cf * np.pi * t) * t + 2 * np.exp(-(b * t) + 2j * cf * np.pi * t) * t *
              (np.cos(2 * cf * np.pi * t) - np.sqrt(3 - 2 ** (3 / 2)) * np.sin(2 * cf * np.pi * t)))
        p2 = (-2 * np.exp(4j * cf * np.pi * t) * t + 2 * np.exp(-(b * t) + 2j * cf * np.pi * t) * t *
              (np.cos(2 * cf * np.pi * t) + np.sqrt(3 - 2 ** (3 / 2)) * np.sin(2 * cf * np.pi * t)))
        p3 = (-2 * np.exp(4j * cf * np.pi * t) * t + 2 * np.exp(-(b * t) + 2j * cf * np.pi * t) * t *
              (np.cos(2 * cf * np.pi * t) - np.sqrt(3 + 2 ** (3 / 2)) * np.sin(2 * cf * np.pi * t)))
        p4 = (-2 * np.exp(4j * cf * np.pi * t) * t + 2 * np.exp(-(b * t) + 2j * cf * np.pi * t) * t *
              (np.cos(2 * cf * np.pi * t) + np.sqrt(3 + 2 ** (3 / 2)) * np.sin(2 * cf * np.pi * t)))
        p5 = np.power(
            -2 / np.exp(2 * b * t) - 2 * np.exp(4j * cf * np.pi * t) + 2 * (1 + np.exp(4j * cf * np.pi * t)) / np.exp(
                b * t), 4)
        gain = np.abs(p1 * p2 * p3 * p4 / p5)

        wts[i, :] = ((t ** 4) / gain) * np.abs(ucirc - zros[:, 0]) * np.abs(ucirc - zros[:, 1]) * \
                    np.abs(ucirc - zros[:, 2]) * np.abs(ucirc - zros[:, 3]) * \
                    np.power(np.abs((pole - ucirc) * (np.conj(pole) - ucirc)), -1*GTord)

    return wts
def spectrum_extractor(x, win_len, shift_len, win_type, is_log):
    samples = x.shape[0]
    frames = (samples - win_len) // shift_len
    stft = np.zeros((win_len, frames), dtype=np.complex64)
    spectrum = np.zeros((win_len // 2 + 1, frames), dtype=np.float64)

    if win_type == 'hanning':
        window = np.hanning(win_len)
    elif win_type == 'hamming':
        window = np.hamming(win_len)
    elif win_type == 'triangle':
        window = (1 - (np.abs(win_len - 1 - 2 * np.arange(1, win_len + 1, 1)) / (win_len + 1)))
    else:
        window = np.ones(win_len)
    for i in range(frames):
        one_frame = x[i*shift_len: i*shift_len+win_len]
        windowed_frame = np.multiply(one_frame, window)
        stft[:, i] = np.fft.fft(windowed_frame, win_len)
        if is_log:
            spectrum[:, i] = np.log(np.abs(stft[0: win_len//2+1, i]))
        else:
            spectrum[:, i] = np.abs(stft[0: win_len // 2 + 1:, i])

    return spectrum
def walet_gmm(sound,sr):
    # emphasized_signal = np.append(sound[0], sound[1:] - 0.97 * sound[:-1])

    wp=pywt.WaveletPacket(data=sound,wavelet='db6',mode='symmetric')

    new_wp=pywt.WaveletPacket(data=None,wavelet='db6',mode='symmetric')
    paths=[node.path for node in wp.get_level(3,'freq')]

    for i,path in enumerate(paths):
    #     if i==0:
    #         c=wp[path].data
    #     else:
    #         c=np.hstack(wp[path].data)

        new_wp[path]=wp[path].data

    return new_wp.reconstruct(update=True)

if __name__=='__main__':
    sample_rate, wave = wf.read("E:\\音乐样本整理版(3s)-未分离\\李荣浩\\李荣浩-不将就\\李荣浩-不将就-3.wav")
    # sample_rate,wave=wf.read("D:\\研究\\语音数据\\OSR_us_000_0010_8k.wav")
    # print(sample_rate,wave)
    wave=list(chain.from_iterable(wave))
    mfcc=walet_gmm(wave,sample_rate)
    fft2gammatone_coef = cochleagram_fft_coefs(sample_rate, 320, 64)
    print(fft2gammatone_coef.shape)
    spect = spectrum_extractor(mfcc, 320, 160, 'hanning', False)
    print(spect.shape)
    mfcc = np.flipud(np.sqrt(np.matmul(fft2gammatone_coef, spect)))
    print(mfcc)
