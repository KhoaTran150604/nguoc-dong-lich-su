"""Đoạn thử cao trào E2 Bạch Đằng 938 (cảnh s35–s46), khung 16:9, không phụ đề, không nhãn.

Chạy trong thư mục làm việc có map_big.png (từ scripts/bandoco/build.py):
    python3 e2_caotrao.py <loi-doc.txt> --stills                 # ảnh tĩnh để duyệt khung hình (thời lượng ước)
    python3 e2_caotrao.py <loi-doc.txt> <voice.json> <voice.mp3> [--final]
- File lời đọc: "# sNN" gán câu cho cảnh; "# lặng 2" chèn 2 giây lặng (hình + tiếng).
- Thời lượng cảnh lấy từ mốc từng câu trong voice.json (skill giong-doc).
- Mỗi cảnh một clip, có cache → sửa cảnh nào render lại cảnh đó.
Bản đồ trận là MINH HỌA: vị trí cọc, luồng sông, số thuyền không theo tỉ lệ thật.
"""
import hashlib, io, json, math, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hieuung')); sys.path.insert(0, HERE)
import demo as L                    # thư viện hiệu ứng H1–H12 đã duyệt
import bando_tran as BT             # bản đồ trận cửa sông
import cairosvg
from PIL import Image

W, H, FPS, U = L.W, L.H, L.FPS, L.U
TA, DICH, DONG2 = L.TA, L.DICH, L.DONG2
seg, lerp = L.seg, L.lerp

# ---------------- Lớp phủ trên bản đồ trận ----------------
RIVER = BT.RIVER
def on_river(u):
    x, y = L.path_at(RIVER, u); return x * U, y * U
def river_y(x):
    for (x0, y0), (x1, y1) in zip(RIVER, RIVER[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return RIVER[-1][1]
STAKES = [(x, river_y(x) + dy) for x in range(556, 631, 8) for dy in (-14, -7, 0, 7, 14)]   # gần cửa biển (minh họa)

STATE = {}
def tide(v):
    """Đặt mức nước cho khung hình này (nền được trộn sẵn theo mức này)."""
    STATE['tide'] = v; return ''

def stakes(vis, ghost=0.0):
    o = []
    for i, (x, y) in enumerate(STAKES):
        a = max(0, min(1, vis * 1.7 - ((i * 7) % 11) * 0.06))
        if a > 0:
            o.append(f'<g opacity="{a:.2f}" transform="translate({x*U:.1f} {y*U:.1f}) scale({U*(0.55+0.45*a):.2f})"><circle r="2.6" fill="#4A2E18" stroke="#1E120A" stroke-width="0.8"/><circle r="1.1" fill="#D6DCE0"/></g>')
            if a < 1: o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{(2+7*a)*U:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{0.7*U:.1f}" opacity="{0.8*(1-a):.2f}"/>')
        elif ghost > 0:
            o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{2.2*U:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{0.6*U:.1f}" opacity="{ghost:.2f}"/>')
    return ''.join(o)

FLEET = [(0.0, 0, 0), (0.025, -5, 7), (0.025, 6, -6), (0.05, 0, 11), (0.05, 2, -11), (0.075, -4, 3), (0.09, 5, 8)]
def fleet(u, sink=0.0, stuck=0.0, t=0.0, facing=170):
    o = []
    for j, (lag, dx, dy) in enumerate(FLEET):
        x, y = on_river(min(1.15, u + lag)); x += dx*U; y += dy*U
        jit = math.sin(t * 22 + j) * 1.2 * U * stuck
        s = max(0, min(1, sink * 1.6 - j * 0.1))
        o.append(f'<g opacity="{1 - 0.85*s:.2f}" transform="translate({jit:.1f} {s*5*U:.1f}) rotate({s*(25 if j%2 else -22):.1f} {x:.1f} {y:.1f})">{L.boat(x, y, facing, DICH, 0.34)}</g>')
    return ''.join(o)

def light_boats(u, facing=0, op=1.0):
    o = []
    for j, (lag, dy) in enumerate([(0, -5), (0.02, 6), (0.04, -1)]):
        x, y = on_river(max(-0.1, u - lag)); y += dy*U
        o.append(f'<g opacity="{op:.2f}">{L.boat(x, y, facing, TA, 0.24)}</g>')
    return ''.join(o)

def clash(x, y, tl, s=0.45):
    """H3 thu nhỏ: hai kiếm chém vào nhau + lửa nhỏ."""
    if tl < 0: return ''
    g = seg(tl, 0.0, 0.5); f = min(1, tl / 0.5); hit = tl - 0.5; o = []
    for i in range(5): o.append(L.flame(x + (i-2)*6*U, y + 3*U, (0.5 - abs(i-2)*0.09) * f, tl, i))
    sh = 4 * math.sin(tl * 40) * max(0, 1 - hit * 2) if hit > 0 else 0
    o.append(f'<g transform="translate({x:.1f} {y:.1f})"><g transform="translate({-12*U:.1f} 0)">{L.sword(lerp(-75, 32, g)+sh, s*U)}</g>'
             f'<g transform="translate({12*U:.1f} 0)">{L.sword(lerp(75, -32, g)-sh, s*U)}</g>')
    if 0 < hit < 0.6: o.append(f'<circle cx="0" cy="{-38*U:.1f}" r="{(5+18*hit)*U:.1f}" fill="{DONG2}" opacity="{0.85*(1-hit/0.6):.2f}"/>')
    return ''.join(o) + '</g>'

def flag(x, y, name, side, s=0.22, **kw): return L.banner(x, y, name, side, s, **kw)

# ---------------- Các cảnh (tl = giây trong cảnh, d = độ dài cảnh) ----------------
def s35(tl, d):
    v = seg(tl, 0, d * 0.8)
    return tide(0.25 + 0.75 * v) + stakes(1 - v, ghost=0.45 * v) + fleet(1.02)

def s36(tl, d):
    return tide(1) + stakes(0, 0.3) + light_boats(lerp(0.35, 0.74, seg(tl, 0, d)), 0) + fleet(lerp(1.02, 0.94, seg(tl, 0, d)))

def s37(tl, d):
    x, y = on_river(0.82)
    return tide(1) + stakes(0, 0.3) + light_boats(0.78, 0) + fleet(lerp(0.94, 0.88, seg(tl, 0, d))) + clash(x, y - 14*U, tl - 0.1)

def s38(tl, d):
    u = seg(tl, 0, d)
    return tide(1) + stakes(0, 0.3) + light_boats(lerp(0.78, 0.55, u), 180) + fleet(lerp(0.88, 0.80, u))

def s39(tl, d):
    u = seg(tl, 0, d * 0.9)
    return tide(1) + stakes(0, 0.45) + light_boats(lerp(0.55, 0.22, u), 180) + fleet(lerp(0.80, 0.42, u))

def s40(tl, d):          # 2 giây lặng: thuyền giặc vẫn tiến, nước bắt đầu hạ rất chậm
    return tide(1 - 0.08 * seg(tl, 0, d)) + stakes(0, 0.45) + light_boats(0.22, 180) + fleet(lerp(0.42, 0.40, seg(tl, 0, d)))

def s41(tl, d):          # nước rút ngay trên bản đồ, cọc nhô lên tại chỗ, thuyền vẫn chạy
    fall = seg(tl, d * 0.15, d * 0.85)
    return tide(0.92 * (1 - fall)) + stakes(fall, 0.45 * (1 - fall)) + light_boats(0.22, 180) + fleet(lerp(0.40, 0.36, seg(tl, 0, d * 0.6)))

def s42(tl, d):
    u = seg(tl, 0, d)
    o = tide(0) + stakes(1) + fleet(0.36) + light_boats(lerp(0.10, 0.28, u), 0)
    for j, (uu, dy) in enumerate([(0.30, 34), (0.40, -40)]):     # quân bộ tiến dọc hai bên bờ sông
        x, y = on_river(lerp(uu - 0.1, uu, u)); o += flag(x, y + dy*U, 'NGÔ QUYỀN' if j == 0 else 'QUÂN TA', TA)
    return o

def s43(tl, d):
    o = tide(0) + stakes(1) + fleet(lerp(0.40, 0.62, seg(tl, 0, 1.6)), stuck=seg(tl, 1.4, 1.8), t=tl, facing=0)
    o += light_boats(lerp(0.30, 0.50, seg(tl, 0, 2.0)), 0)
    for j, (uu, dy) in enumerate([(0.42, 34), (0.52, -40)]):
        x, y = on_river(uu); o += flag(x, y + dy*U, 'NGÔ QUYỀN' if j == 0 else 'QUÂN TA', TA)
    for k, uu in enumerate([0.64, 0.70, 0.75]):
        x, y = on_river(uu); o += clash(x, y - 12*U, tl - 0.8 - 0.5*k)
    return o

def s44(tl, d):
    return tide(0) + stakes(1) + fleet(0.62, sink=seg(tl, 0.2, d * 0.9), stuck=0.4, t=tl, facing=0) + light_boats(0.52, 0)

def s45(tl, d):
    x, y = on_river(0.68); fall = seg(tl, 0.6, 1.8)
    return tide(0) + stakes(1) + fleet(0.62, sink=1, facing=0) + light_boats(0.52, 0) + flag(x, y - 4*U, 'HOẰNG THÁO', DICH, 0.32, tilt=80*fall, grey=seg(tl, 1.4, 2.6))

def s46(tl, d):          # bản đồ vùng quanh Quảng Châu; Hải Môn chỉ là vị trí minh họa
    STATE['region'] = True
    x, y = W*0.62, H*0.42; u = seg(tl, 0.8, d)
    return (flag(lerp(x, x + 120*U, u), lerp(y + 70*U, y - 40*U, u), 'LƯU CUNG', DICH, 0.42, tilt=-15*seg(tl, 0.2, 0.8), op=1 - 0.7*seg(tl, d*0.5, d))
            + f'<text x="{x:.0f}" y="{y+100*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{20*U:.0f}" fill="#2A1A10" text-anchor="middle">Hải Môn (vị trí minh họa)</text>')

SCENE_FN = {k: v for k, v in globals().items() if re.fullmatch(r's\d\d', k)}

# ---------------- Đọc lời đọc + mốc thời gian ----------------
def read_script(path):
    """→ danh sách (cảnh, câu, lặng_trước) theo đúng thứ tự tool giọng đọc đánh số."""
    out, scene, pause = [], None, 0.0
    for raw in open(path, encoding='utf-8'):
        t = raw.strip()
        m = re.match(r'#\s*(s\d\d)\b', t); p = re.match(r'#\s*lặng\s*([\d.]+)', t)
        if m: scene = m.group(1)
        elif p: pause = float(p.group(1))
        elif t and not t.startswith('#'): out.append((scene, t, pause)); pause = 0.0
    return out

def timeline(items, meta=None):
    """Mốc (start, end) từng câu sau khi chèn lặng; không có meta thì ước 0,33 s/từ."""
    if meta: base = [(x['start'], x['end']) for x in meta['lines']]
    else:
        base, t = [], 0.3
        for _, txt, _ in items:
            d = len(txt.split()) * 0.33 + 0.3; base.append((t, t + d)); t += d + 0.35
    shift, res, pauses = 0.0, [], []
    for (a, b), (_, _, p) in zip(base, items):
        if p: pauses.append((a + shift, p)); shift += p
        res.append((a + shift, b + shift))
    end = (meta['duration'] if meta else base[-1][1] + 0.3) + shift + 0.8
    return res, pauses, end

def scenes_from(items, times, pauses, end):
    seq = []
    for (sc, _, _), (a, _) in zip(items, times):
        if not seq or seq[-1][0] != sc: seq.append([sc, max(0.0, a - 0.15)])
    for t0, p in pauses:            # cảnh lặng s40 nằm ngay trước câu sau khoảng lặng
        k = next(i for i, s in enumerate(seq) if s[1] >= t0 - 0.2)
        seq.insert(k, ['s40', t0]); seq[k + 1][1] = t0 + p - 0.15
    seq[0][1] = 0.0
    return [(sc, a, (seq[i + 1][1] if i + 1 < len(seq) else end)) for i, (sc, a) in enumerate(seq)]

REGION = None
def frame(code, tl, d):
    global REGION
    STATE.clear()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{SCENE_FN[code](tl, d)}</svg>'
    ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    if STATE.get('region'):
        if REGION is None: REGION = L.base_frame((112.3, 22.3, 1400.0)).convert('RGBA')
        fr = REGION.copy()
    else:
        fr = BT.background(W, H, U, STATE.get('tide', 1)).copy()
    fr.alpha_composite(ov)
    fa = min(1, tl / 0.25, (d - tl) / 0.25) if code == 's46' else 1
    if fa < 1: fr = Image.blend(Image.new('RGBA', (W, H), (20, 17, 15, 255)), fr, max(0, fa))
    return fr.convert('RGB')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    items = read_script(args[0])
    if '--stills' in sys.argv:
        times, pauses, end = timeline(items)
        os.makedirs('stills', exist_ok=True); shots = []
        for code, a, b in scenes_from(items, times, pauses, end):
            for frac in ((0.15, 0.85) if code in ('s35', 's41', 's43', 's44') else (0.7,)):
                im = frame(code, (b - a) * frac, b - a); fn = f'stills/{code}-{int(frac*100)}.png'
                im.save(fn); shots.append(fn); print(fn)
        return
    meta = json.load(open(args[1])); mp3 = args[2]
    assert len(meta['lines']) == len(items), 'Số câu trong voice.json khác file lời đọc – tạo lại giọng'
    times, pauses, end = timeline(items, meta)
    plan = scenes_from(items, times, pauses, end)
    src = open(__file__, 'rb').read() + open(L.__file__, 'rb').read() + open(BT.__file__, 'rb').read()
    os.makedirs('clips', exist_ok=True); files = []
    for code, a, b in plan:
        d = b - a
        key = hashlib.sha1(src + f'{code}{a:.2f}{d:.2f}{W}'.encode()).hexdigest()[:10]
        out = f'clips/E2c-{code}-{W}-{key}.mp4'; files.append(out)
        if os.path.exists(out): print(code, 'cache'); continue
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast' if L.FINAL else 'ultrafast', '-crf', '20' if L.FINAL else '26', out], stdin=subprocess.PIPE)
        for i in range(round(b * FPS) - round(a * FPS)):
            tl = (round(a * FPS) + i) / FPS - a
            p.stdin.write(frame(code, tl, d).tobytes())
        p.stdin.close(); p.wait(); print(code, f'ok {d:.1f}s')
    open('list.txt', 'w').write(''.join(f"file '{f}'\n" for f in files))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'hinh.mp4'], check=True)
    # tiếng: chèn các khoảng lặng
    fc, prev, parts = '', 0.0, []
    for k, (t0, p) in enumerate(pauses):
        orig = t0 - sum(pp for tt, pp in pauses[:k])
        fc += f'[1:a]atrim={prev}:{orig},asetpts=PTS-STARTPTS[a{k}];anullsrc=r=44100:cl=mono,atrim=0:{p}[z{k}];'
        parts += [f'[a{k}]', f'[z{k}]']; prev = orig
    fc += f'[1:a]atrim={prev},asetpts=PTS-STARTPTS[aend];'; parts.append('[aend]')
    fc += ''.join(parts) + f'concat=n={len(parts)}:v=0:a=1[a]'
    name = 'E2-thu-caotrao-' + ('1080p' if L.FINAL else 'nhap') + '.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'hinh.mp4', '-i', mp3, '-filter_complex', fc,
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', name], check=True)
    print('->', name, f'{end:.1f}s')

if __name__ == '__main__':
    main()
