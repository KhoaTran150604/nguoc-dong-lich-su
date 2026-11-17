"""Âm thanh hiệu ứng (SFX) tổng hợp bằng code – không dùng file của người khác nên không vướng bản quyền.

Có file thật (vd tải từ YouTube Audio Library) thì đặt ở assets/sfx/<ten>.wav|mp3, sẽ được ưu tiên.
Tên hiệu ứng: kiem (kiếm chạm), lua (lửa cháy, dài), vo (thuyền vỡ), nuoc (nước bắn), trong (trống trận),
rut (nước rút ào), song (nền sóng nước, dài), roi (vật đổ).
"""
import os, subprocess
import numpy as np

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
rng = np.random.default_rng(3)

def _t(d): return np.arange(int(d * SR)) / SR
def _env(n, a=0.005, d=0.5):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def _lp(x, cut):
    """Lọc thông thấp 1 cực (đơn giản, đủ dùng cho tiếng động)."""
    a = np.exp(-2 * np.pi * cut / SR); y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
def _lp_fast(x, cut):
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * cut / SR); return lfilter([1 - a], [1, -a], x)
try:
    import scipy.signal  # noqa
    LP = _lp_fast
except Exception:
    LP = _lp
def _hp(x, cut): return x - LP(x, cut)
def _norm(x, peak=0.9): m = np.max(np.abs(x)) or 1; return x / m * peak

def kiem():
    t = _t(1.1); x = np.zeros_like(t)
    for f, g, dc in [(1180, 1, .45), (2630, .7, .35), (3910, .5, .25), (5370, .35, .18), (7020, .2, .12)]:
        x += g * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / dc)
    x += _hp(rng.normal(0, 1, len(t)), 2000) * np.exp(-t / 0.015) * 1.5   # tiếng chát lúc chạm
    return _norm(x, 0.8)

def lua(d=4.0):
    n = int(d * SR); base = LP(rng.normal(0, 1, n), 500) * 3
    base *= 0.6 + 0.4 * LP(rng.normal(0, 1, n), 3) * 20
    cr = np.zeros(n)
    for p in rng.integers(0, n - 2000, int(d * 35)):          # tiếng tí tách
        k = rng.integers(200, 1400); cr[p:p + k] += _hp(rng.normal(0, 1, k), 1500) * np.exp(-np.arange(k) / rng.uniform(40, 200)) * rng.uniform(.3, 1)
    x = base + cr
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.3 * SR))
    return _norm(x * fade, 0.7)

def vo():
    t = _t(1.6); n = len(t)
    thump = np.sin(2 * np.pi * (90 - 40 * t) * t) * np.exp(-t / 0.18)
    crack = np.zeros(n)
    for p in [0, 0.05, 0.12, 0.22, 0.4, 0.55]:
        i = int(p * SR); k = int(0.08 * SR)
        crack[i:i + k] += _hp(rng.normal(0, 1, k), 900) * np.exp(-np.arange(k) / (0.012 * SR)) * rng.uniform(.5, 1)
    creak_t = t[: int(0.7 * SR)]; f = 160 - 60 * creak_t / 0.7
    creak = ((np.mod(np.cumsum(f) / SR, 1) * 2 - 1) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * creak_t))) * np.exp(-creak_t / 0.4) * 0.35
    x = thump * 1.2 + crack; x[int(0.25 * SR): int(0.25 * SR) + len(creak)] += LP(creak, 1800)
    return _norm(x + 0.6 * nuoc()[: n] * (t > 0.3), 0.9)

def nuoc():
    t = _t(1.6); x = LP(_hp(rng.normal(0, 1, len(t)), 300), 3000)
    return _norm(x * np.minimum(1, t / 0.02) * np.exp(-t / 0.35), 0.7)

def trong():
    t = _t(1.2); f = 62 + 50 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35) + LP(rng.normal(0, 1, len(t)), 700) * np.exp(-t / 0.04) * 0.6
    return _norm(x, 0.95)

def rut():
    t = _t(3.0); x = LP(rng.normal(0, 1, len(t)), 900) * np.sin(np.pi * t / 3.0) ** 2
    return _norm(x, 0.6)

def song(d=60.0):
    n = int(d * SR); x = LP(rng.normal(0, 1, n), 700)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * np.arange(n) / SR / 5.5)       # sóng vỗ chậm
    return _norm(x, 0.35)

def roi():
    t = _t(0.8); x = np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.12) + LP(rng.normal(0, 1, len(t)), 1200) * np.exp(-t / 0.06)
    return _norm(x, 0.7)

GEN = dict(kiem=kiem, lua=lua, vo=vo, nuoc=nuoc, trong=trong, rut=rut, song=song, roi=roi)


# ---------- Bản làm lại (16/11): trống trận to, vang; thuyền gỗ vỡ không còn tiếng "chích điện" ----------
def BLP(x, cut, order=4):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(order, cut, 'low', fs=SR, output='sos'), x)
def BHP(x, cut, order=2):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(order, cut, 'high', fs=SR, output='sos'), x)
def _bp(x, lo, hi): return BLP(BHP(x, lo), hi)
def _reverb(x, d=1.2, mix=0.35):
    from scipy.signal import fftconvolve
    t = _t(d); ir = rng.normal(0, 1, len(t)) * np.exp(-t / (d / 4)); ir = BLP(ir, 2500); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - mix) + fftconvolve(x, ir)[: len(x)] * mix
def _modes(d, freqs, decay):
    t = _t(d); x = np.zeros_like(t)
    for f, g in freqs: x += g * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / decay)
    return x

def _trong_hit(big=1.0):
    t = _t(2.0); f = 52 * big ** -0.2 + 38 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.75)
    body += 0.35 * np.sin(2 * np.pi * np.cumsum(f * 1.6) / SR) * np.exp(-t / 0.4)
    skin = _bp(rng.normal(0, 1, len(t)), 80, 600) * np.exp(-t / 0.04) * 0.6
    return (body + skin) * big

def _place(n, hits):
    out = np.zeros(n)
    for t0, g in hits:
        h = _trong_hit(g); i = int(t0 * SR); k = min(len(h), n - i); out[i:i + k] += h[:k]
    return out

def trong_a():   # từng tiếng trống lớn, vang xa
    return _norm(_reverb(_place(int(4.5 * SR), [(0, 1), (1.1, 1), (2.2, 1)]), 1.6, 0.4), 0.95)

def trong_b():   # nhịp trận dồn dập: tùng… tùng… tùng tùng tùng – TÙNG
    hits = [(0, .9), (0.8, .9), (1.6, .8), (1.95, .8), (2.3, .85), (2.75, 1.1)]
    return _norm(_reverb(_place(int(4.8 * SR), hits), 1.4, 0.35), 0.95)

def trong_c():   # trống + chiêng
    x = _place(int(5.0 * SR), [(0, 1), (0.7, .9), (1.4, 1), (2.1, 1.1)])
    t = _t(3.2); g = _modes(3.2, [(196, 1), (233, .6), (392, .5), (466, .35), (588, .25)], 1.2) * np.minimum(1, t / 0.01)
    g *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    i = int(2.1 * SR); x[i:i + len(g)] += g[: len(x) - i] * 0.55
    return _norm(_reverb(x, 1.8, 0.4), 0.95)

def _wood_crack(d=0.35):
    t = _t(d); n = len(t)
    x = _modes(d, [(rng.uniform(180, 320), 1), (rng.uniform(420, 700), .6), (rng.uniform(800, 1300), .35)], 0.06)
    x += _bp(rng.normal(0, 1, n), 200, 1800) * np.exp(-t / 0.03) * 1.0
    return x * np.minimum(1, t / 0.002)

def _splash(d=2.2, big=1.0):
    t = _t(d); x = _bp(rng.normal(0, 1, len(t)), 120, 1500 * big)
    env = np.minimum(1, t / 0.05) * np.exp(-t / (0.5 * big)); bub = np.zeros_like(t)
    for p in rng.uniform(0.2, d - 0.3, 30):   # bọt nước lục bục
        i = int(p * SR); k = int(0.04 * SR); f = rng.uniform(300, 900)
        bub[i:i + k] += np.sin(2 * np.pi * np.cumsum(np.linspace(f, f * 1.6, k)) / SR) * np.exp(-np.arange(k) / (0.012 * SR)) * 0.25
    return x * env + bub

def _groan(d=1.2):
    """Tiếng gỗ thân thuyền rên kẽo kẹt: nhiễu lọc dải hẹp, cao độ trượt – không dùng sóng răng cưa."""
    t = _t(d); x = rng.normal(0, 1, len(t))
    from scipy.signal import lfilter
    out = np.zeros_like(x); f0 = 140
    for k in range(0, len(x), 512):
        f = f0 + 40 * np.sin(2 * np.pi * 0.7 * k / SR); r = 0.995; w = 2 * np.pi * f / SR
        seg_ = lfilter([1 - r], [1, -2 * r * np.cos(w), r * r], x[k:k + 512]); out[k:k + 512] = seg_
    return BLP(out, 900) * np.sin(np.pi * t / d) ** 2

def _thud(d=1.0):
    t = _t(d); return np.sin(2 * np.pi * (70 - 25 * t) * t) * np.exp(-t / 0.25) + BLP(rng.normal(0, 1, len(t)), 250) * np.exp(-t / 0.1) * 0.8

def _lay(n, parts):
    out = np.zeros(n)
    for t0, x, g in parts:
        i = int(t0 * SR); k = min(len(x), n - i); out[i:i + k] += x[:k] * g
    return out

def vo_a():      # va cọc: thịch + gỗ gãy răng rắc + nước ào
    n = int(3.0 * SR)
    parts = [(0, _thud(), 1.0)] + [(0.04 + i * 0.07 + rng.uniform(0, .03), _wood_crack(), .7) for i in range(6)] + [(0.35, _splash(2.4), .9)]
    return _norm(_reverb(_lay(n, parts), 0.9, 0.25), 0.95)

def vo_b():      # gỗ rên kẽo kẹt → gãy → đổ ầm xuống nước
    n = int(3.6 * SR)
    parts = [(0, _groan(1.2), .9), (1.0, _thud(), 1.0)] + [(1.02 + i * 0.06, _wood_crack(), .8) for i in range(8)] + [(1.3, _splash(2.2, 1.2), 1.0)]
    return _norm(_reverb(_lay(n, parts), 1.0, 0.3), 0.95)

def vo_c():      # nặng hơn: hai cú va, nhiều mảnh vỡ, nước bắn lớn
    n = int(3.8 * SR)
    parts = [(0, _thud(), 1.0), (0.55, _thud(), 0.9)] + [(rng.uniform(0, 1.0), _wood_crack(0.3), .6) for _ in range(14)] + [(0.6, _splash(3.0, 1.4), 1.1), (1.5, _groan(0.9), .4)]
    return _norm(_reverb(_lay(n, parts), 1.1, 0.3), 0.95)

GEN.update(trong_a=trong_a, trong_b=trong_b, trong_c=trong_c, vo_a=vo_a, vo_b=vo_b, vo_c=vo_c)

def load_audio(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def get(name, d=None):
    for ext in ('wav', 'mp3'):
        p = os.path.join(ROOT, 'assets', 'sfx', f'{name}.{ext}')
        if os.path.exists(p): return _norm(load_audio(p), 0.8)
    return GEN[name](d) if d and name in ('lua', 'song') else GEN[name]()

def mix(voice, events, total, bed_gain=0.10, duck=0.35):
    """voice: mảng giọng (đã chèn lặng). events: [(giây, tên, độ lớn, độ dài|None)].
    Hiệu ứng tự hạ xuống khi có giọng đọc (ducking) để lời luôn rõ."""
    n = int(total * SR); out = np.zeros(n); fx = np.zeros(n)
    out[: min(n, len(voice))] += voice[:n]
    bed = get('song', total + 1)[:n]; fx[: len(bed)] += bed * bed_gain
    for t0, name, g, d in events:
        s = get(name, d); i = int(t0 * SR)
        if i >= n: continue
        k = min(len(s), n - i); fx[i:i + k] += s[:k] * g
    env = LP(np.abs(np.pad(voice, (0, max(0, n - len(voice))))[:n]), 8) * 6
    fx *= 1 - (1 - duck) * np.clip(env, 0, 1)
    y = out + fx
    return y / max(1.0, np.max(np.abs(y)) / 0.97)

def write_wav(y, path):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', path], stdin=subprocess.PIPE)
    p.stdin.write(y.astype(np.float32).tobytes()); p.stdin.close(); p.wait()
