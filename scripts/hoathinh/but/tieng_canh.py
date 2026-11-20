"""TIẾNG cho cảnh thử – tổng hợp 100% bằng code theo ĐÚNG timeline của canh_thu.py, rồi mux vào MP4.

Minh hoạ nguyên tắc: ÂM THANH & HÌNH DÙNG CHUNG MỘT "BẢN NHẠC" (cùng mốc khung) → khớp tuyệt đối.
Gồm: nhạc nền ngũ cung nhẹ · tiếng chân khi chạy · "bịch" lúc dừng · blip theo miệng khi nói ·
     "boing" lúc ngạc nhiên · chuông lúc cười. (Giọng thật để sau: thoai_song_tu.py.)

Chạy:  python scripts/hoathinh/but/tieng_canh.py      (cần đã chạy canh_thu.py trước)
Ra:    build/thu-hoathinh/but-canh/canh-thu-tieng.mp4
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import numpy as np
import soundfile as sf
import canh_thu as CA
import dung_tho_noi as D

SR = 44100
FPS = CA.FPS
OUT = CA.OUT


def seg_times():
    """trả dict tên đoạn → (khung_bắt_đầu, số_khung) và tổng khung."""
    t, d = 0, {}
    for name, n in CA.SEG:
        d[name] = (t, n)
        t += n
    return d, t


def env(n, a=0.01, r=0.1):
    """bao biên attack–release (giây)."""
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def put(buf, start_s, wave):
    i = int(start_s * SR)
    j = min(len(buf), i + len(wave))
    if i < len(buf):
        buf[i:j] += wave[:j - i]


def tone(f, dur, amp=0.3, a=0.01, r=0.1, harm=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t)
    if harm:
        w += 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)
    return amp * w * env(n, a, r)


def tap(dur=0.09, amp=0.25, f=180):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = (np.random.randn(n) * 0.5 + np.sin(2 * np.pi * f * t))
    return amp * w * env(n, 0.001, 0.07)


def thud(dur=0.25, amp=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(150, 60, n)
    w = np.sin(2 * np.pi * f * t) + 0.4 * np.random.randn(n)
    return amp * w * env(n, 0.002, 0.2)


def blip(dur=0.07, f=430, amp=0.22):
    n = int(dur * SR)
    t = np.arange(n) / SR
    w = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t)
    return amp * w * env(n, 0.004, 0.05)


def boing(dur=0.35, amp=0.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 260 + 500 * np.sin(np.pi * t / dur)
    w = np.sin(2 * np.pi * f * t)
    return amp * w * env(n, 0.005, 0.15)


def build():
    seg, total = seg_times()
    dur = total / FPS
    buf = np.zeros(int(dur * SR) + SR)

    # nhạc nền ngũ cung nhẹ (C D E G A), lặp cả cảnh
    penta = [523.25, 587.33, 659.25, 783.99, 880.0]
    step = 0.42
    i = 0
    tt = 0.0
    while tt < dur:
        f = penta[i % len(penta)] / (2 if (i // len(penta)) % 2 else 1)
        put(buf, tt, tone(f, step * 0.95, amp=0.06, r=0.3))
        tt += step; i += 1

    # tiếng chân khi CHẠY
    r0, rn = seg['run']; run_t0 = r0 / FPS; run_t1 = (r0 + rn) / FPS
    tt = run_t0
    while tt < run_t1:
        put(buf, tt, tap(amp=0.22))
        tt += 0.17

    # "bịch" lúc DỪNG
    s0, sn = seg['settle']
    put(buf, s0 / FPS + 0.05, thud())

    # blip theo MIỆNG khi NÓI (chỉ các khung miệng há)
    t0, tn = seg['talk']
    for k in range(tn):
        tloc = k / (tn - 1)
        key = D.TALK[int(tloc * (len(D.TALK) - 1) * 2) % len(D.TALK)]
        if key in ('m_o', 'm_noi', 'm_mo'):
            f = {'m_o': 400, 'm_noi': 470, 'm_mo': 540}[key]
            put(buf, (t0 + k) / FPS, blip(f=f))

    # "boing" lúc NGẠC NHIÊN
    g0, gn = seg['ngac']
    put(buf, g0 / FPS + 0.03, boing())

    # chuông đi lên lúc CƯỜI
    v0, vn = seg['vui']
    for j, f in enumerate([659.25, 783.99, 1046.5]):
        put(buf, v0 / FPS + j * 0.12, tone(f, 0.5, amp=0.18, r=0.4))

    # chuẩn hoá nhẹ
    peak = np.max(np.abs(buf)) or 1.0
    buf = 0.9 * buf / peak
    return buf


def mux(wav_path, mp4_in, mp4_out):
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ff = 'ffmpeg'
    cmd = [ff, '-y', '-i', mp4_in, '-i', wav_path, '-c:v', 'copy', '-c:a', 'aac',
           '-b:a', '160k', '-shortest', mp4_out]
    subprocess.run(cmd, check=True, capture_output=True)
    return mp4_out


if __name__ == '__main__':
    buf = build()
    wav = os.path.join(OUT, 'canh-tieng.wav')
    sf.write(wav, buf.astype(np.float32), SR)
    out = mux(wav, os.path.join(OUT, 'canh-thu.mp4'), os.path.join(OUT, 'canh-thu-tieng.mp4'))
    print('WAV:', wav)
    print('MP4 có tiếng:', out)
