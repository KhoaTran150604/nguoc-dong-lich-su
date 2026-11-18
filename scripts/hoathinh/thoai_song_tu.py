"""Tạo giọng đối thoại Anh Văn (Gia Huy) – Em Võ (Tiến Đạt) cho cảnh thử 10s.

Cần Python ≥3.10 có zerotts (máy local: ~/.venvs/zerotts, tạo bằng `uv venv --python 3.12`).
Chạy:  HF_HUB_DISABLE_XET=1 ~/.venvs/zerotts/bin/python scripts/hoathinh/thoai_song_tu.py
Ra:    build/thu-hoathinh/song-tu/thoai.wav + thoai.json (mốc từng câu + đường biên độ cho khẩu hình)

Lời thoại chỉ dùng dữ kiện ✅ trong kb/E2-bach-dang-938.md (F17 cọc bịt sắt ở cửa biển, F19 triều rút).
"""
import json
import os

import numpy as np
import soundfile as sf
from zerotts import ZeroTTS, normalize_vi_text

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'song-tu')
VOICE = {'vo': 'tiendat', 'van': 'giahuy'}
LINES = [
    ('vo', 'Anh Văn! Một hàng cọc gỗ mà đánh chìm được cả đoàn thuyền giặc á?'),
    ('van', 'Sử chép rằng, Ngô Quyền cho cắm cọc lớn, vót nhọn, bịt sắt ở cửa biển.'),
    ('vo', 'Rồi sao nữa anh?'),
    ('van', 'Chờ nước triều rút.'),
]
GAP, LEAD = 0.35, 0.4


def trim(a, sr, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if idx.size == 0:
        return a
    return a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]


def main():
    import sys
    global OUT, LINES
    if len(sys.argv) > 1:          # thoai_song_tu.py <loi.json> : [[ai, câu, đoạn], …] → ghi cạnh file
        LINES = [tuple(x) for x in json.load(open(sys.argv[1]))]
        OUT = os.path.dirname(os.path.abspath(sys.argv[1]))
    os.makedirs(OUT, exist_ok=True)
    tts = ZeroTTS.from_pretrained('zeroweight-ai/ZeroTTS')
    sr = tts.sample_rate
    pieces = [np.zeros(int(LEAD * sr), np.float32)]
    t = LEAD
    meta = []
    from faster_whisper import WhisperModel
    import scipy.signal as S
    wm = WhisperModel('medium', compute_type='int8')

    def heard(a):
        b = S.resample_poly(a, 16000, sr).astype(np.float32)
        return ' '.join(x.text for x in wm.transcribe(b, language='vi')[0]).lower()

    def score(h, text):
        want = [w.strip('!?,.').lower() for w in text.split()]
        got = [w.strip('!?,.') for w in h.split()]
        return sum(w in got for w in want) / len(want)

    for i, (who, text, *rest) in enumerate(LINES):
        best = None
        for k in range(14):  # thử nhiều lần, giữ bản Whisper nghe đúng nhất
            np.random.seed(11 + i + 100 * k)
            a = trim(tts.synthesize(normalize_vi_text(text), voice=VOICE[who], cfg_scale=1.0)
                     .reshape(-1).astype(np.float32), sr)
            h = heard(a)
            sc = score(h, text)
            if best is None or sc > best[0]:
                best = (sc, a, h)
            if sc >= 0.99:
                break
        print('  %.2f  %s' % (best[0], best[2]))
        a = best[1]
        meta.append(dict(who=who, text=text, seg=(rest[0] if rest else ''), start=round(t, 3),
                         end=round(t + a.size / sr, 3), score=round(best[0], 2)))
        pieces += [a, np.zeros(int(GAP * sr), np.float32)]
        t += a.size / sr + GAP
    audio = np.concatenate(pieces)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.9
    sf.write(os.path.join(OUT, 'thoai.wav'), audio, sr)
    # biên độ mỗi 1/30 giây → độ mở miệng
    hop = sr // 30
    env = [float(np.sqrt(np.mean(audio[k:k + hop] ** 2))) for k in range(0, audio.size, hop)]
    mx = max(env) or 1
    json.dump(dict(sr=sr, dur=audio.size / sr, lines=meta, env=[round(e / mx, 3) for e in env]),
              open(os.path.join(OUT, 'thoai.json'), 'w'), ensure_ascii=False, indent=1)
    print('xong: %.2fs' % (audio.size / sr))
    for x in meta:
        print(x)


if __name__ == '__main__':
    main()
