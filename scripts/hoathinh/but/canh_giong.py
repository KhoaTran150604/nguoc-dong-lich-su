"""CẢNH THỬ CÓ GIỌNG THẬT + LIP-SYNC – ghép âm thanh vào KHUNG ẢNH THẬT.

Nguyên tắc (một bản nhạc chung): tạo GIỌNG trước → lấy đường BIÊN ĐỘ → suy ra ĐỘ MỞ MIỆNG từng khung
→ render lại khung ảnh thật với miệng khớp giọng → trộn giọng + tiếng động theo cùng mốc → mux MP4.

Chạy:  HF_HUB_DISABLE_XET=1 python scripts/hoathinh/but/canh_giong.py [--ma ngo-khong] [--voice giahuy]
Ra:    build/thu-hoathinh/but-canh/canh-giong.mp4
"""
import argparse
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
import soundfile as sf
import scipy.signal as S
import canh_thu as CA
import tieng_canh as T

FPS = CA.FPS
OUT = CA.OUT
LINE = 'Ta là Tôn Ngộ Không!'
# ngưỡng biên độ → trạng thái miệng (đóng → há to)
def mouth_of(a):
    if a < 0.10: return 'm_mim'
    if a < 0.32: return 'm_o'
    if a < 0.58: return 'm_noi'
    return 'm_mo'


def make_voice(text, voice):
    from zerotts import ZeroTTS, normalize_vi_text
    tts = ZeroTTS.from_pretrained('zeroweight-ai/ZeroTTS')
    sr = tts.sample_rate
    best = None
    for k in range(3):                          # vài seed, giữ bản dài nhất (đọc trọn câu)
        np.random.seed(7 + k)
        a = tts.synthesize(normalize_vi_text(text), voice=voice, cfg_scale=1.0).reshape(-1).astype(np.float32)
        idx = np.where(np.abs(a) > 0.01)[0]
        if idx.size:
            a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        if best is None or a.size > best.size:
            best = a
    return best, sr


def frame_mouths(voice, sr):
    """RMS mỗi khung (1/FPS) → chuẩn hoá → trạng thái miệng; thêm vài khung ngậm ở cuối."""
    hop = sr // FPS
    rms = np.array([np.sqrt(np.mean(voice[k:k + hop] ** 2)) for k in range(0, voice.size, hop)])
    rms = rms / (rms.max() or 1)
    keys = [mouth_of(a) for a in rms]
    keys += ['m_mim', 'm_mim']                  # ngậm miệng cuối câu
    return keys


def seg_times(talk_n):
    t, d = 0, {}
    for name, n in CA.SEG:
        nn = talk_n if name == 'talk' else n
        d[name] = (t, nn); t += nn
    return d, t


def build_audio(voice44, talk_n):
    seg, total = seg_times(talk_n)
    dur = total / FPS
    buf = np.zeros(int(dur * T.SR) + T.SR)
    # nhạc nền ngũ cung nhẹ
    penta = [523.25, 587.33, 659.25, 783.99, 880.0]
    tt, i = 0.0, 0
    while tt < dur:
        f = penta[i % 5] / (2 if (i // 5) % 2 else 1)
        T.put(buf, tt, T.tone(f, 0.4, amp=0.05, r=0.3)); tt += 0.42; i += 1
    # tiếng chân chạy
    r0, rn = seg['run']; tt = r0 / FPS
    while tt < (r0 + rn) / FPS:
        T.put(buf, tt, T.tap(amp=0.2)); tt += 0.17
    # bịch dừng
    s0, _ = seg['settle']; T.put(buf, s0 / FPS + 0.05, T.thud())
    # GIỌNG THẬT đặt đúng đoạn nói
    t0, _ = seg['talk']; T.put(buf, t0 / FPS, 0.95 * voice44)
    # boing ngạc nhiên + chuông cười
    g0, _ = seg['ngac']; T.put(buf, g0 / FPS + 0.03, T.boing())
    v0, _ = seg['vui']
    for j, f in enumerate([659.25, 783.99, 1046.5]):
        T.put(buf, v0 / FPS + j * 0.12, T.tone(f, 0.5, amp=0.18, r=0.4))
    buf = 0.9 * buf / (np.max(np.abs(buf)) or 1)
    return buf


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    ap.add_argument('--voice', default='giahuy')
    ap.add_argument('--fps', type=int, default=CA.FPS)
    a = ap.parse_args()
    fps = a.fps
    # đặt fps cho cả pipeline (giữ nguyên thời lượng giây)
    FPS = fps
    CA.FPS = fps
    T.FPS = fps
    CA.SEG = [(nm, max(2, round(s * fps))) for nm, s in CA._SEC]
    CA.L.FAR, CA.L.NEAR = 22.0, 9.0
    work = os.path.join(OUT, f'f{fps}')
    os.makedirs(work, exist_ok=True)

    print(f'• [{fps}fps] Tạo giọng thật…', flush=True)
    voice, sr = make_voice(LINE, a.voice)
    print('  giọng %.2fs @ %dHz' % (voice.size / sr, sr))
    keys = frame_mouths(voice, sr)
    print('  số khung nói:', len(keys))

    print(f'• [{fps}fps] Render khung ảnh thật (lip-sync)…', flush=True)
    frames = CA.render(a.ma, talk_keys=keys)
    for i, f in enumerate(frames):
        f.save(os.path.join(work, f'khung_{i:04d}.png'))
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ff = 'ffmpeg'
    cam = os.path.join(work, 'cam.mp4')
    subprocess.run([ff, '-y', '-framerate', str(fps), '-i', os.path.join(work, 'khung_%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', cam],
                   check=True, capture_output=True)

    print(f'• [{fps}fps] Trộn giọng + tiếng động…', flush=True)
    voice44 = S.resample_poly(voice, T.SR, sr).astype(np.float32)
    buf = build_audio(voice44, len(keys))
    wav = os.path.join(work, 'tieng.wav')
    sf.write(wav, buf.astype(np.float32), T.SR)
    out = T.mux(wav, cam, os.path.join(OUT, f'canh-giong-{fps}fps.mp4'))
    print('XONG', fps, 'fps →', out, '| khung:', len(frames))
