"""Dựng một khối (Short 9:16) từ file cấu hình JSON.

Cách chạy (từ thư mục gốc repo):
    python3 scripts/khoi/render.py scripts/khoi/e2_k1.json --voice <model.onnx> --out assets/e2/E2-K1.mp4
    python3 scripts/khoi/render.py scripts/khoi/e2_k1.json --vbee assets/e2/k1-vbee.mp3 --out ...   (khi có giọng Vbee)

- Giọng tạm: Piper (pip install piper-tts) + model tiếng Việt, mỗi câu một file → biết chính xác thời điểm.
- Giọng Vbee: một file MP3 cho cả khối; script cắt câu theo khoảng lặng (silencedetect).
- Hình: vẽ bằng PIL theo bảng màu kênh; mỗi segment một "scene".
"""
import argparse, io, json, math, os, random, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cairosvg

W, H, FPS = 1080, 1920, 30
INK = (20, 17, 15); GOLD = (201, 162, 74); GOLD2 = (243, 210, 122); RED = (179, 38, 30); CREAM = (242, 230, 204); COPPER = (201, 145, 94)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = lambda n, s: ImageFont.truetype(os.path.join(ROOT, 'fonts', f'{n}.ttf'), s)
F_TITLE = lambda s: F('PlayfairDisplay-ExtraBold', s)
F_SEMI = lambda s: F('BeVietnamPro-SemiBold', s)
F_MED = lambda s: F('BeVietnamPro-Medium', s)
F_REG = lambda s: F('BeVietnamPro-Regular', s)

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def clamp01(x): return max(0.0, min(1.0, x))

# ---------- nền ----------
def make_bg():
    rnd = np.random.default_rng(7)
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.42) / H) ** 2)
    glow = np.clip(1 - d * 1.9, 0, 1) ** 2
    base = np.array(INK, float)[None, None, :] * (0.75 + 0.25 * (1 - d))[..., None]
    base += np.array([60, 40, 14], float)[None, None, :] * glow[..., None] * 0.55
    base += rnd.normal(0, 4.0, (H, W, 1))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # vân trống đồng mờ
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(ov)
    cx, cy = W / 2, H * 0.42
    for r in (430, 470, 520, 600, 690):
        d2.ellipse([cx - r, cy - r, cx + r, cy + r], outline=COPPER + (22,), width=2)
    for k in range(48):
        a1 = 2 * math.pi * k / 48; a2 = 2 * math.pi * (k + 0.5) / 48
        d2.line([(cx + 600 * math.cos(a1), cy + 600 * math.sin(a1)), (cx + 690 * math.cos(a2), cy + 690 * math.sin(a2))], fill=COPPER + (18,), width=2)
    im = im.convert('RGBA'); im.alpha_composite(ov)
    return im

# ---------- avatar tách lớp ----------
def avatar_layers():
    h = open(os.path.join(ROOT, 'assets/brand/design-canvas/AvatarV2.dc.html'), encoding='utf-8').read()
    svg = re.search(r'<svg.*?</svg>', h, re.S).group(0)
    head = re.search(r'<svg[^>]*>', svg).group(0)
    defs = re.search(r'<defs>.*?</defs>', svg, re.S).group(0)
    body = svg[svg.index('</defs>') + 7: svg.rindex('</svg>')]
    els = re.findall(r'<(?:path|circle|polygon|rect|line|polyline|ellipse)\b[^>]*/>', body)
    ring, mapl = [], []
    for e in els:
        (mapl if ('url(#gold)' in e) else ring).append(e)
    def render(parts, size=760):
        s = f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="760" viewBox="0 0 760 760">{defs}{"".join(parts)}</svg>'
        return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=size, output_height=size))).convert('RGBA')
    return render(ring), render(mapl), render(ring + mapl)

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); al = im.getchannel('A').point(lambda v: int(v * a)); im.putalpha(al); return im

# ---------- chữ ----------
def text_center(d, y, s, font, fill, spacing=0):
    if spacing:
        w = sum(d.textlength(c, font=font) + spacing for c in s) - spacing; x = (W - w) / 2
        for c in s:
            d.text((x, y), c, font=font, fill=fill); x += d.textlength(c, font=font) + spacing
    else:
        w = d.textlength(s, font=font); d.text(((W - w) / 2, y), s, font=font, fill=fill)

def wrap(d, s, font, maxw):
    words, lines, cur = s.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def chunk_sub(s, font, maxw=900, maxlines=2):
    """Chia phụ đề thành các cụm tối đa 2 dòng."""
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    lines = wrap(d, s, font, maxw)
    return [' '.join(lines[i:i + maxlines]) for i in range(0, len(lines), maxlines)]

# ---------- cảnh ----------
SCENES = {}
def scene(name):
    def deco(fn): SCENES[name] = fn; return fn
    return deco

def fade_in(t, d=0.45): return ease(t / d)

@scene('chuky')
def sc_chuky(im, t, dur, ctx, seg):
    ring, mapl = ctx['ring'], ctx['map']
    size = 640; cx, cy = W // 2, int(H * 0.40)
    p = clamp01((t - 0.25) / 2.2)
    year = int(round(2026 - (2026 - 938) * ease(p)))
    ang = t * 22  # ngược chiều kim đồng hồ
    r = ring.resize((size, size), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC)
    m = with_alpha(mapl.resize((size, size), Image.LANCZOS), 1 - ease(clamp01((t - 0.9) / 1.6)) * 0.88)
    im.alpha_composite(r, (cx - size // 2, cy - size // 2)); im.alpha_composite(m, (cx - size // 2, cy - size // 2))
    d = ImageDraw.Draw(im, 'RGBA')
    text_center(d, cy + size // 2 + 40, str(year), F_TITLE(210), GOLD2 + (255,))
    text_center(d, 250, 'NGƯỢC DÒNG SỬ VIỆT', F_MED(40), GOLD + (255,), spacing=6)

@scene('chuky_hold')
def sc_hold(im, t, dur, ctx, seg):
    ring, mapl = ctx['ring'], ctx['map']
    size = 640; cx, cy = W // 2, int(H * 0.40)
    T = t + ctx['intro']
    r = ring.resize((size, size), Image.LANCZOS).rotate(T * 22, resample=Image.BICUBIC)
    im.alpha_composite(with_alpha(r, 1 - 0.5 * ease(t / dur)), (cx - size // 2, cy - size // 2))
    im.alpha_composite(with_alpha(mapl.resize((size, size), Image.LANCZOS), 0.12 * (1 - ease(t / dur))), (cx - size // 2, cy - size // 2))
    d = ImageDraw.Draw(im, 'RGBA')
    text_center(d, cy + size // 2 + 40, '938', F_TITLE(210), GOLD2 + (255,))

def big_title(im, t, title, sub=None, y=640, size=150, col=GOLD2, subcol=CREAM, note=None):
    a = int(255 * fade_in(t)); d = ImageDraw.Draw(im, 'RGBA')
    dy = int(30 * (1 - fade_in(t)))
    font = F_TITLE(size)
    while d.textlength(title, font=font) > W - 120: size -= 6; font = F_TITLE(size)
    text_center(d, y + dy, title, font, col + (a,))
    if sub: text_center(d, y + int(size * 1.3) + 30 + dy, sub, F_SEMI(60), subcol + (a,))
    if note: text_center(d, y + int(size * 1.3) + 120 + dy, note, F_REG(40), COPPER + (int(a * 0.9),))

def seal(im, t, cx, cy, s, lines, col=RED):
    sc = 1.25 - 0.25 * ease(t / 0.5); a = fade_in(t, 0.35)
    tile = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(tile, 'RGBA')
    d.rounded_rectangle([6, 6, s - 6, s - 6], radius=26, fill=col + (230,), outline=GOLD2 + (255,), width=8)
    d.rounded_rectangle([28, 28, s - 28, s - 28], radius=16, outline=GOLD2 + (160,), width=3)
    f = F_TITLE(int(s * 0.2)); tot = len(lines) * s * 0.24
    for i, l in enumerate(lines):
        w = d.textlength(l, font=f); d.text(((s - w) / 2, s / 2 - tot / 2 + i * s * 0.24), l, font=f, fill=CREAM + (255,))
    tile = tile.rotate(-6, resample=Image.BICUBIC, expand=True)
    ns = int(tile.width * sc); tile = with_alpha(tile.resize((ns, ns), Image.LANCZOS), a)
    im.alpha_composite(tile, (int(cx - ns / 2), int(cy - ns / 2)))

@scene('giao_vuong')
def sc_giao(im, t, dur, ctx, seg):
    seal(im, t, W // 2, 760, 430, ['GIAO', 'VƯƠNG'])
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * fade_in(t - 0.6))
    text_center(d, 1060, '« vua đất Giao »', F_SEMI(60), CREAM + (a,))
    a2 = int(255 * fade_in(t - dur * 0.55))
    text_center(d, 1160, 'khi đất Giao còn chưa về tay', F_REG(46), COPPER + (a2,))

@scene('hai_mon')
def sc_haimon(im, t, dur, ctx, seg):
    d = ImageDraw.Draw(im, 'RGBA'); a = fade_in(t); A = lambda k: int(255 * a * k)
    dy = int(24 * (1 - a))
    text_center(d, 470 + dy, 'HẢI MÔN', F_TITLE(150), GOLD2 + (A(1),))
    text_center(d, 680 + dy, 'nơi vua Nam Hán đóng quân tiếp ứng', F_SEMI(46), CREAM + (A(1),))
    text_center(d, 750 + dy, '(vị trí chưa rõ)', F_REG(36), COPPER + (A(0.9),))
    # lầu canh nhỏ, quay lưng, đặt giữa phía dưới
    cx, base = W // 2, 1330; c = (6, 5, 4, A(1)); edge = GOLD + (A(0.55),)
    body = [(cx - 120, base), (cx - 95, 1030), (cx + 95, 1030), (cx + 120, base)]
    roof = [(cx - 170, 1040), (cx, 940), (cx + 170, 1040)]
    d.polygon(body, fill=c, outline=edge); d.polygon(roof, fill=c, outline=edge)
    d.ellipse([cx - 16, 975, cx + 16, 1007], fill=c)  # bóng người quay lưng
    d.line([(cx + 130, 925), (cx + 130, 1035)], fill=edge, width=4)
    d.polygon([(cx + 130, 925), (cx + 205, 940 + 6 * math.sin(t * 3)), (cx + 130, 958)], fill=RED + (A(0.9),))
    d.line([(150, base), (W - 150, base)], fill=GOLD + (A(0.5),), width=3)

def river_svg(t, dur):
    random.seed(4); w, h = W, H
    s = ''
    s += f'<rect x="0" y="980" width="{w}" height="{h-980}" fill="#0E161C"/>'
    for i in range(30):
        yy = 1000 + i * 26; x = (random.randint(-100, w) + t * 30 * (1 + i % 3)) % (w + 200) - 200
        s += f'<line x1="{x:.0f}" y1="{yy}" x2="{x+random.randint(80,240):.0f}" y2="{yy}" stroke="#C9915E" stroke-width="3" opacity="{0.10+0.18*random.random():.2f}"/>'
    p = ease(clamp01(t / (dur * 0.6)))  # nước rút
    wl = 980 + 120 * p
    for i, x in enumerate((180, 330, 470, 610, 760, 900)):
        top = 900 + (i % 2) * 40
        s += f'<polygon points="{x-16},1250 {x+16},1250 {x+16},{top+40} {x},{top} {x-16},{top+40}" fill="#4A3020" stroke="#1A0F08" stroke-width="3"/>'
        s += f'<polygon points="{x-14},{top+40} {x},{top} {x+14},{top+40}" fill="#9AA3A8"/>'
    s += f'<rect x="0" y="{wl:.0f}" width="{w}" height="{h-wl:.0f}" fill="#0E161C" opacity="0.92"/>'
    tilt = 8 + 14 * p; col = '#5A3E2A'
    s += (f'<g transform="translate(600 {1060+50*p:.0f}) rotate({tilt:.1f}) scale(0.8)">'
          f'<path d="M-200,0 L200,0 L150,70 L-160,70 Z" fill="{col}" stroke="#C9A24A" stroke-width="3"/>'
          f'<line x1="-40" y1="0" x2="-40" y2="-300" stroke="{col}" stroke-width="9"/>'
          f'<path d="M-40,-290 L70,-278 L48,-24 L-40,-24 Z" fill="#7A5638" stroke="#C9A24A" stroke-width="3" opacity="0.95"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{s}</svg>'

@scene('bach_dang')
def sc_bachdang(im, t, dur, ctx, seg):
    layer = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=river_svg(t, dur).encode()))).convert('RGBA')
    im.alpha_composite(with_alpha(layer, fade_in(t)))
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * fade_in(t - dur * 0.45))
    text_center(d, 400, 'quá nửa', F_TITLE(140), GOLD2 + (a,))
    text_center(d, 570, 'chết đuối', F_SEMI(66), CREAM + (a,))
    text_center(d, 1290, 'minh họa', F_REG(30), COPPER + (150,))

@scene('doi_dau')
def sc_doidau(im, t, dur, ctx, seg):
    d = ImageDraw.Draw(im, 'RGBA')
    a1 = int(255 * fade_in(t)); a2 = int(255 * fade_in(t - dur * 0.5))
    text_center(d, 560, 'NAM HÁN', F_TITLE(140), RED + (a1,))
    d.line([(240, 800), (840, 800)], fill=GOLD + (a1,), width=3)
    for k in range(7):
        x = 300 + k * 80; d.polygon([(x, 800), (x + 40, 770), (x + 80, 800)], outline=GOLD + (a1,))
    text_center(d, 860, 'NGÔ QUYỀN', F_TITLE(140), GOLD2 + (a2,))

def year_label(y):
    return f'{-y} TCN' if y < 0 else str(y)

@scene('lui')
def sc_lui(im, t, dur, ctx, seg):
    d = ImageDraw.Draw(im, 'RGBA')
    p = ease(clamp01((t - 0.3) / (dur - 0.6)))
    y = int(round(938 - (938 + 111) * p)); y = y if y != 0 else -1
    text_center(d, 640, year_label(y), F_TITLE(200), GOLD2 + (255,))
    # thước thời gian chạy lùi
    off = (t * 220) % 120
    for k in range(-1, 11):
        x = k * 120 + off; d.line([(x, 980), (x, 1020 if k % 2 else 1040)], fill=COPPER + (160,), width=3)
    d.line([(0, 980), (W, 980)], fill=COPPER + (160,), width=3)
    text_center(d, 1090, '◀  ngược dòng thời gian', F_MED(42), CREAM + (200,))

@scene('so1050')
def sc_1050(im, t, dur, ctx, seg):
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * fade_in(t))
    p = ease(clamp01(t / 0.9)); x0, x1 = 150, 930; xm = x0 + (x1 - x0) * p
    d.line([(x0, 990), (xm, 990)], fill=RED + (a,), width=14)
    d.line([(x0, 960), (x0, 1020)], fill=GOLD2 + (a,), width=5); d.line([(xm, 960), (xm, 1020)], fill=GOLD2 + (a,), width=5)
    d.text((x0 - 40, 1040), '111 TCN', font=F_SEMI(40), fill=CREAM + (a,))
    if p > 0.95: d.text((x1 - 70, 1040), '938', font=F_SEMI(40), fill=CREAM + (a,))
    n = int(1050 * ease(clamp01((t - 0.3) / 1.2)))
    text_center(d, 560, f'~{n:,}'.replace(',', '.'), F_TITLE(190), GOLD2 + (a,))
    text_center(d, 830, 'NĂM', F_MED(54), CREAM + (a,), spacing=10)
    text_center(d, 1130, '(theo cách tính của Trần Trọng Kim)', F_REG(38), COPPER + (a,))

@scene('van_xuan')
def sc_vanxuan(im, t, dur, ctx, seg):
    big_title(im, t, '544', 'VẠN XUÂN', y=560, size=210, note='Lý Bí xưng đế, đặt tên nước')

@scene('thanh_62')
def sc_62(im, t, dur, ctx, seg):
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * fade_in(t))
    unit = 2.4; x0 = 110; y1, y2 = 700, 960
    p1 = ease(clamp01((t - 0.2) / 1.0)); p2 = ease(clamp01((t - dur * 0.55) / 1.6))
    d.rectangle([x0, y1, x0 + 62 * unit * p1, y1 + 70], fill=GOLD2 + (a,))
    d.text((x0, y1 - 80), '62 năm tự chủ', font=F_SEMI(50), fill=GOLD2 + (a,))
    d.text((x0, y1 + 90), 'Lý Nam Đế · Triệu Việt Vương · Hậu Lý', font=F_REG(34), fill=CREAM + (a,))
    if p2 > 0:
        a2 = int(255 * fade_in(t - dur * 0.55))
        d.rectangle([x0, y2, x0 + 304 * unit * p2, y2 + 70], fill=RED + (a2,))
        d.text((x0, y2 - 80), 'Tùy, Đường: hơn 300 năm', font=F_SEMI(50), fill=CREAM + (a2,))

@scene('phung_hung')
def sc_phung(im, t, dur, ctx, seg):
    big_title(im, t, '791', 'PHÙNG HƯNG', y=560, size=210, note='người Đường Lâm · dấy binh vây phủ thành')

@scene('ran_vo')
def sc_ranvo(im, t, dur, ctx, seg):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer, 'RGBA')
    a = int(255 * fade_in(t))
    text_center(d, 620, 'THẾ KỶ X', F_TITLE(170), GOLD2 + (a,))
    text_center(d, 860, 'phương Bắc rạn vỡ', F_SEMI(60), CREAM + (a,))
    p = ease(clamp01((t - dur * 0.45) / 1.0))
    if p > 0:
        pts = [(300, 560), (470, 700), (420, 760), (600, 820), (560, 900), (760, 1000)]
        n = max(2, int(len(pts) * p) + 1)
        # tách đôi: phần phải lệch xuống
        mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
        md.polygon([(300, 0)] + pts + [(760, H), (W, H), (W, 0)], fill=255)
        right = Image.new('RGBA', (W, H), (0, 0, 0, 0)); right.paste(layer, (0, 0), mask)
        left = layer.copy(); left.paste((0, 0, 0, 0), (0, 0), mask)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); layer.alpha_composite(left); layer.alpha_composite(right, (int(14 * p), int(18 * p)))
        ImageDraw.Draw(layer, 'RGBA').line(pts[:n], fill=RED + (230,), width=6)
    im.alpha_composite(layer)

@scene('end')
def sc_end(im, t, dur, ctx, seg):
    av = ctx['full'].resize((460, 460), Image.LANCZOS)
    im.alpha_composite(with_alpha(av, fade_in(t)), (W // 2 - 230, 460))
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * fade_in(t - 0.3))
    text_center(d, 1000, 'Ngược Dòng Sử Việt', F_TITLE(96), CREAM + (a,))
    text_center(d, 1150, ctx['end_next'], F_SEMI(46), GOLD2 + (a,))

# ---------- lớp chung ----------
def overlay_common(im, seg, sub_text, t_seg, ctx, show_label=True):
    d = ImageDraw.Draw(im, 'RGBA')
    if show_label and seg.get('label'):
        a = int(255 * fade_in(t_seg, 0.3))
        text_center(d, 230, seg['label'], F_MED(40), GOLD + (a,), spacing=6)
        d.line([(440, 296), (640, 296)], fill=RED + (a,), width=4)
    if sub_text:
        f = F_SEMI(54); lines = wrap(d, sub_text, f, 900); lh = 72
        y0 = int(H * 0.80); top = y0 - 22; bot = y0 + lh * len(lines) + 10
        d.rounded_rectangle([70, top, W - 70, bot], radius=24, fill=(10, 8, 6, 175))
        for i, l in enumerate(lines): text_center(d, y0 + i * lh, l, f, (245, 235, 215, 255))
    if seg.get('src'):
        text_center(d, H - 120, 'Nguồn: ' + seg['src'], F_REG(28), COPPER + (190,))
    im.alpha_composite(ctx['wm'], (W - ctx['wm'].width - 40, 150))
    if ctx.get('part'):
        d.text((48, 178), ctx['part'], font=F_MED(30), fill=COPPER + (200,))

# ---------- âm thanh ----------
def tts_piper(model, text, out, length_scale):
    subprocess.run([sys.executable, '-m', 'piper', '-m', model, '-f', out, '--length-scale', str(length_scale)],
                   input=text.encode('utf-8'), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_wav(p):
    with wave.open(p) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a, sr

def split_vbee(mp3, segs, work, sr=44100, manual_cuts=None):
    """Cắt file giọng của cả khối thành từng câu theo khoảng lặng gần vị trí dự kiến (tỷ lệ số ký tự)."""
    wav = os.path.join(work, 'vbee.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ac', '1', '-ar', str(sr), wav], check=True)
    a, sr = read_wav(wav)
    r = subprocess.run(['ffmpeg', '-i', wav, '-af', 'silencedetect=noise=-35dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r)]
    total = len(a) / sr
    sil = [((s0 + e0) / 2, e0 - s0) for s0, e0 in zip(st, en) if s0 > 0.05 and e0 < total - 0.1]; L = [len(s.get('tts') or s['sub']) for s in segs]; cum = np.cumsum(L) / sum(L)
    print('Khoảng lặng (giữa, độ dài):', [(round(m, 2), round(dd, 2)) for m, dd in sil])
    K = len(segs) - 1
    if manual_cuts:
        if len(manual_cuts) != K: sys.exit(f'--cuts cần đúng {K} điểm cắt')
        cuts = list(manual_cuts)
    else:
        cuts = auto_cuts(sil, K, total, segs)
    edges = [0.0] + cuts + [total]; clips = []
    for x0, x1 in zip(edges[:-1], edges[1:]):
        seg = a[int(x0 * sr):int(x1 * sr)]
        nz = np.where(np.abs(seg) > 0.01)[0]
        seg = seg[max(0, nz[0] - int(0.05 * sr)):nz[-1] + int(0.08 * sr)] if len(nz) else seg
        clips.append(seg)
    print('Cắt Vbee tại (giây):', [round(c, 2) for c in cuts])
    return clips, sr

def auto_cuts(sil, K, total, segs):
    L = [len(s.get('tts') or s['sub']) for s in segs]; cum = np.cumsum(L) / sum(L)
    longp = [x for x in sil if x[1] >= 0.75]
    if len(longp) >= K: sil = longp  # giọng có ngắt đoạn rõ: chỉ xét các khoảng lặng dài
    M = len(sil)
    if M < K: sys.exit('Không đủ khoảng lặng để cắt câu – kiểm tra file Vbee (mỗi câu nên cách nhau ≥0,25s).')
    # so khớp trên 'thời gian có tiếng' (bỏ các khoảng lặng) để độ dài ngắt nghỉ không làm lệch tỷ lệ
    sp_total = total - sum(dd for _, dd in sil); acc = 0.0; sp_pos = []
    for m, dd in sil: sp_pos.append(m - acc - dd / 2); acc += dd
    targets = [c * sp_total for c in cum[:-1]]
    # quy hoạch động: chọn K khoảng lặng theo thứ tự, gần vị trí dự kiến, ưu tiên khoảng lặng dài
    cost = lambda k, i: ((sp_pos[i] - targets[k]) / sp_total) ** 2 * 400 - min(sil[i][1], 1.2)
    INF = 1e18; dp = [[INF] * M for _ in range(K)]; bk = [[-1] * M for _ in range(K)]
    for i in range(M): dp[0][i] = cost(0, i)
    for k in range(1, K):
        best, bi = INF, -1
        for i in range(M):
            if i > 0 and dp[k - 1][i - 1] < best: best, bi = dp[k - 1][i - 1], i - 1
            if bi >= 0: dp[k][i] = best + cost(k, i); bk[k][i] = bi
    i = min(range(M), key=lambda j: dp[K - 1][j]); idx = []
    for k in range(K - 1, -1, -1): idx.append(i); i = bk[k][i]
    cuts = [sil[j][0] for j in reversed(idx)]
    return cuts

def tick(sr, dur=0.035, f=1600):
    t = np.arange(int(sr * dur)) / sr; return 0.35 * np.sin(2 * np.pi * f * t) * np.exp(-t * 90)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config'); ap.add_argument('--voice', help='model Piper .onnx (giọng tạm)'); ap.add_argument('--vbee', help='file MP3 Vbee đọc cả khối'); ap.add_argument('--out', required=True)
    ap.add_argument('--cuts', type=float, nargs='*', help='điểm cắt (giây) giữa các câu, nếu tự động cắt sai')
    ap.add_argument('--length-scale', type=float, default=1.2); ap.add_argument('--work', default=None)
    ap.add_argument('--preview', type=float, nargs='*', help='chỉ xuất ảnh tĩnh tại các giây này')
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding='utf-8'))
    work = args.work or os.path.splitext(args.out)[0] + '_work'; os.makedirs(work, exist_ok=True)
    segs = cfg['segments']; gap = cfg.get('gap', 0.35); intro = cfg.get('intro_seconds', 2.7)

    # 1) giọng
    clips = []
    if args.vbee:
        clips, sr = split_vbee(args.vbee, segs, work, manual_cuts=args.cuts or cfg.get('vbee_cuts'))
    else:
        for i, s in enumerate(segs):
            p = os.path.join(work, f'v{i:02d}.wav')
            if not os.path.exists(p): tts_piper(args.voice, s['tts'], p, args.length_scale)
            a, sr = read_wav(p); clips.append(a)
    # 2) dòng thời gian
    t = intro; timeline = []
    for s, a in zip(segs, clips):
        dur = len(a) / sr; timeline.append((t, dur)); t += dur + gap
    end0 = t; total = end0 + cfg.get('end_seconds', 3.5)
    audio = np.zeros(int(total * sr) + sr, np.float32)
    for (st, dur), a in zip(timeline, clips):
        i0 = int(st * sr); audio[i0:i0 + len(a)] += a * 0.95
    # tiếng tích tắc phần chữ ký: dày rồi thưa dần
    k = 0.15
    while k < intro - 0.2:
        i0 = int(k * sr); tk = tick(sr); audio[i0:i0 + len(tk)] += tk; k += 0.06 + 0.22 * (k / intro) ** 2
    wav = os.path.join(work, 'audio.wav')
    with wave.open(wav, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())

    # 3) phụ đề theo cụm
    subs = []
    for s, (st, dur) in zip(segs, timeline):
        chunks = chunk_sub(s['sub'], F_SEMI(54)); L = sum(len(c) for c in chunks); x = st
        for c in chunks:
            dd = dur * len(c) / L; subs.append((x, x + dd + (gap if c is chunks[-1] else 0), c)); x += dd

    ring, mapl, full = avatar_layers()
    wm = with_alpha(Image.open(os.path.join(ROOT, 'assets/brand/watermark-trong-suot-vong.png')).convert('RGBA').resize((96, 96), Image.LANCZOS), 0.7)
    ctx = dict(ring=ring, map=mapl, full=full, wm=wm, intro=intro, end_next=cfg.get('end_next', ''), part=cfg.get('part', ''))
    bg = make_bg()

    def frame(T):
        z = 1.0 + 0.04 * ((T % 12) / 12)
        cw, ch = int(W / z), int(H / z); im = bg.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H))
        if T < intro:
            SCENES['chuky'](im, T, intro, ctx, {}); return im
        if T >= end0:
            SCENES['end'](im, T - end0, total - end0, ctx, {}); return im
        idx = max(i for i, (st, _) in enumerate(timeline) if st <= T + 1e-6)
        st, dur = timeline[idx]; seg = segs[idx]; tl = T - st
        SCENES[seg['scene']](im, tl, dur + gap, ctx, seg)
        sub = next((c for a, b, c in subs if a <= T < b), None)
        overlay_common(im, seg, sub, tl, ctx, show_label=seg['scene'] != 'chuky_hold')
        return im

    if args.preview:
        for T in args.preview: frame(T).convert('RGB').save(os.path.join(work, f'preview_{T:05.1f}.png'))
        print('preview ->', work); return

    n = int(total * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', wav, '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-shortest', args.out], stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(frame(f / FPS).convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    json.dump({'timeline': timeline, 'total': total, 'subs': subs}, open(os.path.join(work, 'timing.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'OK {args.out}  {total:.1f}s')

if __name__ == '__main__':
    main()
