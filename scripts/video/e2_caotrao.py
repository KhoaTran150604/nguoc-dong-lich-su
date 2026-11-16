"""Đoạn thử ~1 phút: cao trào E2 Bạch Đằng 938 (cảnh s35–s46), khung 16:9.

Chạy trong thư mục làm việc có map_big.png (từ scripts/bandoco/build.py):
    python3 e2_caotrao.py <voice.json> <voice.mp3> [--final]
- Thời lượng mỗi cảnh lấy từ mốc từng câu trong voice.json (skill giong-doc).
- Chèn 2 giây lặng trước "Và rồi, bước thứ ba" (s40) vào cả hình lẫn tiếng.
- Mỗi cảnh một clip, có cache theo nội dung → sửa cảnh nào render lại cảnh đó.
Bản đồ trận là hình MINH HỌA: vị trí cọc, luồng sông, số thuyền không theo tỉ lệ thật.
"""
import hashlib, io, json, math, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hieuung'))
import demo as L                    # thư viện hiệu ứng H1–H12 đã duyệt
import cairosvg
from PIL import Image

W, H, FPS, U = L.W, L.H, L.FPS, L.U
MUC, DONG, DONG2, DO, KEM, TA, DICH = L.MUC, L.DONG, L.DONG2, L.DO, L.KEM, L.TA, L.DICH
ease, seg, lerp = L.ease, L.seg, L.lerp
SIL = 2.0                            # lặng s40

# ---------------- Bản đồ trận: cửa sông (toạ độ khung 960×540, nhân U) ----------------
RIVER = [(-20, 150), (140, 175), (280, 220), (420, 250), (560, 268), (700, 280), (800, 285)]
COAST_X = 720                        # bên phải là biển
STAKES = [(x, y) for x in range(530, 691, 20) for y in (236, 252, 268, 284, 300)]  # vùng cọc ở cửa sông (minh họa)

def pts(p): return ' '.join(f'{x*U:.1f},{y*U:.1f}' for x, y in p)

def battle_bg(tide):
    """tide 1 = nước lên (lòng sông rộng, bãi bồi ngập), 0 = nước rút (bãi bùn lộ)."""
    w_mud, w_water = 150, lerp(70, 150, tide)
    o = [f'<rect width="{W}" height="{H}" fill="#D4B88A"/>']
    for i, (x, y) in enumerate([(80, 60), (230, 420), (420, 80), (120, 470), (520, 430), (330, 470)]):
        o.append(L.tree(x*U, y*U, 1.1) if i % 2 else L.mountain(x*U, y*U, 1.3))
    sea = f'M{COAST_X*U:.0f},0 Q{(COAST_X-40)*U:.0f},{140*U:.0f} {(COAST_X-10)*U:.0f},{280*U:.0f} Q{(COAST_X+30)*U:.0f},{420*U:.0f} {(COAST_X-20)*U:.0f},{H} L{W},{H} L{W},0 Z'
    o.append(f'<polyline points="{pts(RIVER)}" fill="none" stroke="#9C8A6A" stroke-width="{w_mud*U:.0f}" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<path d="{sea}" fill="#9C8A6A"/>')
    water = '#3E6F86' if tide > 0.5 else '#4F8296'
    o.append(f'<polyline points="{pts(RIVER)}" fill="none" stroke="{water}" stroke-width="{w_water*U:.0f}" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<path d="{sea}" fill="{water}" transform="translate({(1-tide)*25*U:.1f} 0)"/>')
    for k in range(3):   # sóng ven bờ
        o.append(f'<path d="{sea}" fill="none" stroke="#B8D2D8" stroke-width="{2*U:.1f}" opacity="{0.5-0.12*k:.2f}" transform="translate({(18+16*k+(1-tide)*25)*U:.1f} 0)"/>')
    o.append(f'<text x="{870*U:.0f}" y="{90*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{26*U:.0f}" fill="#E8EEF0" text-anchor="middle">BIỂN</text>')
    o.append(f'<text x="{250*U:.0f}" y="{150*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{24*U:.0f}" fill="#2A1A10" text-anchor="middle" transform="rotate(14 {250*U:.0f} {150*U:.0f})">Sông Bạch Đằng</text>')
    return ''.join(o)

def stakes(vis, ghost=0.0):
    """vis: mức nhô lên (0 chìm – 1 lộ hẳn); ghost: viền mờ cho người xem biết chỗ cọc khi đang chìm."""
    o = []
    for i, (x, y) in enumerate(STAKES):
        a = max(0, min(1, vis * 1.6 - (i % 7) * 0.08))
        if a > 0:
            o.append(f'<g transform="translate({x*U:.1f} {y*U:.1f}) scale({U*(0.6+0.4*a):.2f})"><circle r="5" fill="#5A3A20" stroke="#2A1A10" stroke-width="1.5" opacity="{a:.2f}"/><circle r="2" fill="#C8CED2" opacity="{a:.2f}"/></g>')
        elif ghost > 0:
            o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{4*U:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{1*U:.1f}" stroke-dasharray="2 2" opacity="{ghost:.2f}"/>')
    return ''.join(o)

def on_river(u):
    """Điểm trên luồng sông theo tỉ lệ u (0 = thượng nguồn trái, 1 = ngoài biển phải)."""
    x, y = L.path_at(RIVER, u); return x * U, y * U

FLEET = [(0.0, 0, 0), (0.035, -14, 14), (0.035, 16, -12), (0.07, 0, 24), (0.07, 4, -26), (0.105, -10, 6)]
def fleet(u, sink=0.0, stuck=0.0, t=0.0, op=1.0):
    o = []
    for j, (lag, dx, dy) in enumerate(FLEET):
        x, y = on_river(min(1.12, u + lag)); x += dx*U; y += dy*U
        jit = math.sin(t * 22 + j) * 2 * U * stuck
        s = max(0, min(1, sink * 1.6 - j * 0.12))
        o.append(f'<g opacity="{op*(1 - 0.85*s):.2f}" transform="translate({jit:.1f} {s*10*U:.1f}) rotate({s*(25 if j%2 else -22):.1f} {x:.1f} {y:.1f})">{L.boat(x, y, 170, DICH, 0.62)}</g>')
    return ''.join(o)

def light_boats(u, facing=0, op=1.0):
    o = []
    for j, (lag, dy) in enumerate([(0, -10), (0.03, 12), (0.06, -2)]):
        x, y = on_river(max(-0.1, u - lag)); y += dy*U
        o.append(f'<g opacity="{op:.2f}">{L.boat(x, y, facing, TA, 0.42)}</g>')
    return ''.join(o)

def clash(x, y, tl):
    """H3 rút gọn: hai kiếm chém vào nhau + lửa nhỏ, tl = giây kể từ lúc bắt đầu."""
    if tl < 0: return ''
    g = seg(tl, 0.0, 0.5); f = min(1, tl / 0.5); hit = tl - 0.5; o = []
    for i in range(5): o.append(L.flame(x + (i-2)*10*U, y + 4*U, (0.8 - abs(i-2)*0.15) * f, tl, i))
    shake = 4 * math.sin(tl * 40) * max(0, 1 - hit * 2) if hit > 0 else 0
    o.append(f'<g transform="translate({x:.1f} {y:.1f})"><g transform="translate({-20*U:.1f} 0)">{L.sword(lerp(-75, 32, g)+shake, 0.75*U)}</g>'
             f'<g transform="translate({20*U:.1f} 0)">{L.sword(lerp(75, -32, g)-shake, 0.75*U)}</g>')
    if 0 < hit < 0.6: o.append(f'<circle cx="0" cy="{-62*U:.1f}" r="{(8+28*hit)*U:.1f}" fill="{DONG2}" opacity="{0.85*(1-hit/0.6):.2f}"/>')
    return ''.join(o) + '</g>'

def chip(text):
    return (f'<rect x="{16*U:.0f}" y="{16*U:.0f}" width="{(len(text)*13+34)*U:.0f}" height="{40*U:.0f}" rx="{6*U:.0f}" fill="{MUC}" opacity="0.88" stroke="{DONG}" stroke-width="{2*U:.1f}"/>'
            f'<text x="{30*U:.0f}" y="{43*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{20*U:.0f}" fill="{DONG2}">{text}</text>')

def note():
    return f'<text x="{W-12*U:.0f}" y="{H-10*U:.0f}" font-family="Be Vietnam Pro" font-size="{12*U:.0f}" fill="{KEM}" text-anchor="end" opacity="0.8">Hình minh họa, vị trí gần đúng</text>'

# ---------------- Sa bàn mặt cắt (dùng cho bước 3) ----------------
def saban(level, t, boat_shift=0.0):
    """level 1 = nước cao, 0 = nước rút. Thuyền mắc cọc khi nước xuống thấp."""
    x0, y0, w, h = 140*U, 70*U, 680*U, 400*U; bed = y0 + h - 60*U
    o = [f'<rect width="{W}" height="{H}" fill="#1E1A16"/>',
         f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{KEM}" stroke="{DONG}" stroke-width="{4*U:.1f}" rx="{10*U:.0f}"/>',
         f'<rect x="{x0:.0f}" y="{bed:.0f}" width="{w:.0f}" height="{60*U:.0f}" fill="#8A6A44"/>']
    wl = bed - lerp(90, 270, level) * U
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#3A7CA5" opacity="0.8"/>')
    top = bed - 190 * U
    for i in range(9):
        sx = x0 + (90 + i * 62) * U
        o.append(f'<polygon points="{sx-10*U:.1f},{bed+14*U:.1f} {sx+10*U:.1f},{bed+14*U:.1f} {sx+10*U:.1f},{top+24*U:.1f} {sx:.1f},{top:.1f} {sx-10*U:.1f},{top+24*U:.1f}" fill="#6A4428" stroke="#2A1A10" stroke-width="{2*U:.1f}"/>')
        o.append(f'<polygon points="{sx-10*U:.1f},{top+24*U:.1f} {sx:.1f},{top:.1f} {sx+10*U:.1f},{top+24*U:.1f}" fill="#C8CED2"/>')
    for k in range(3):
        bx = x0 + w*(0.3 + 0.22*k) + boat_shift*U; by = min(wl, top + 6*U) - 2*U
        tilt = (-14 if k % 2 else 12) * seg(top - wl, -10*U, 20*U) if wl > top else 0
        o.append(f'<g transform="rotate({tilt:.1f} {bx:.1f} {by:.1f})">{L.boat(bx, by, 0, DICH, 2.0)}</g>')
    o.append(f'<rect x="{x0:.0f}" y="{wl:.1f}" width="{w:.0f}" height="{bed-wl:.1f}" fill="#2F6E96" opacity="0.62"/>')   # cọc dưới nước bị che mờ
    o.append(f'<text x="{x0+w/2:.0f}" y="{bed+40*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{18*U:.0f}" fill="{KEM}" text-anchor="middle">MẶT CẮT CỬA SÔNG (MINH HỌA)</text>')
    return ''.join(o)

# ---------------- Các cảnh: (mã, dòng bắt đầu (1-based), hàm vẽ(tl, dur)) ----------------
def s35(tl, d):
    tide = seg(tl, 0, d*0.8)
    return battle_bg(0.3 + 0.7*tide) + stakes(1 - tide, ghost=0.5*tide) + chip('BƯỚC 1 · NƯỚC TRIỀU LÊN') + note()

def s36(tl, d):
    return battle_bg(1) + stakes(0, 0.35) + light_boats(lerp(0.25, 0.62, seg(tl, 0, d)), 0) + fleet(1.0) + chip('THUYỀN NHẸ RA KHIÊU CHIẾN') + note()

def s37(tl, d):
    x, y = on_river(0.74)
    return battle_bg(1) + stakes(0, 0.35) + light_boats(0.66, 0) + fleet(lerp(1.0, 0.86, seg(tl, 0, d))) + clash(x, y - 20*U, tl - 0.1) + note()

def s38(tl, d):
    u = seg(tl, 0, d)
    return battle_bg(1) + stakes(0, 0.35) + light_boats(lerp(0.66, 0.45, u), 180) + fleet(lerp(0.86, 0.80, u)) + chip('GIẢ VỜ THUA CHẠY') + note()

def s39(tl, d):
    u = seg(tl, 0, d*0.85)
    return (battle_bg(1) + stakes(0, 0.5) + light_boats(lerp(0.45, 0.12, u), 180) + fleet(lerp(0.80, 0.40, u))
            + chip('BƯỚC 2 · GIẶC VÀO TRONG HÀNG CỌC') + note())

def ripples(vis, t):
    """Gợn nước quanh mũi cọc vừa nhô lên."""
    o = []
    for i, (x, y) in enumerate(STAKES):
        a = max(0, min(1, vis * 1.6 - (i % 7) * 0.08))
        if 0.05 < a < 1:
            r = (4 + 10 * a) * U
            o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{r:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{1.2*U:.1f}" opacity="{0.7*(1-a):.2f}"/>')
    return ''.join(o)

def s40(tl, d):      # lặng 2 giây: vẫn trên bản đồ trận, thuyền giặc tiếp tục tiến, nước bắt đầu hạ rất chậm
    tide = 1 - 0.08 * seg(tl, 0, d)
    return battle_bg(tide) + stakes(0, 0.5) + light_boats(0.12, 180, op=0.9) + fleet(lerp(0.40, 0.37, seg(tl, 0, d))) + chip('BƯỚC 3 · NƯỚC RÚT') + note()

def s41(tl, d):      # nước rút ngay trên bản đồ: lòng sông hẹp lại, cọc nhô lên tại chỗ, thuyền vẫn đang chạy
    fall = seg(tl, d * 0.2, d * 0.8)
    tide = 0.92 * (1 - fall)
    return (battle_bg(tide) + stakes(fall, 0.5 * (1 - fall)) + ripples(fall, tl) + light_boats(0.12, 180, op=0.9)
            + fleet(lerp(0.37, 0.33, seg(tl, 0, d * 0.6))) + chip('BƯỚC 3 · NƯỚC RÚT') + note())

def s42(tl, d):
    u = seg(tl, 0, d)
    o = battle_bg(0) + stakes(1) + fleet(lerp(0.40, 0.52, u)) + light_boats(lerp(-0.05, 0.22, u), 0)
    for j, uu in enumerate([0.18, 0.28]):   # quân bộ hai cờ tiến theo bờ (không phải phục binh)
        x, y = on_river(lerp(uu - 0.12, uu, u)); o += L.banner(x, y + 110*U, 'NGÔ QUYỀN' if j == 0 else 'QUÂN TA', TA, 0.3)
    return o + chip('NGÔ QUYỀN TUNG QUÂN TIẾN ĐÁNH') + note()

def s43(tl, d):
    o = battle_bg(0) + stakes(1) + fleet(lerp(0.52, 0.66, seg(tl, 0, 1.4)), stuck=seg(tl, 1.2, 1.6), t=tl) + light_boats(lerp(0.25, 0.45, seg(tl, 0, 2)), 0)
    for k, uu in enumerate([0.62, 0.70, 0.76]):
        x, y = on_river(uu); o += clash(x, y - 26*U, tl - 0.6*k)
    return o + chip('THUYỀN VƯỚNG CỌC, KHÔNG QUAY RA ĐƯỢC') + note()

def s44(tl, d):
    return battle_bg(0) + stakes(1) + fleet(0.66, sink=seg(tl, 0.2, d*0.9), stuck=0.4, t=tl) + light_boats(0.45, 0) + chip('THUYỀN VỠ, THUYỀN ĐẮM') + note()

def s45(tl, d):
    x, y = on_river(0.70)
    fall = seg(tl, 0.6, 1.8)
    o = battle_bg(0) + stakes(1) + fleet(0.66, sink=1)
    o += L.banner(x, y - 10*U, 'HOẰNG THÁO', DICH, 0.5, tilt=80*fall, grey=seg(tl, 1.4, 2.6))
    return o + chip('HOẰNG THÁO TỬ TRẬN') + note()

def s46(tl, d):
    x, y = W*0.62, H*0.42                  # bản đồ vùng quanh Quảng Châu; Hải Môn chỉ là vị trí minh họa
    u = seg(tl, 0.8, d)
    return (L.banner(lerp(x, x + 120*U, u), lerp(y + 70*U, y - 40*U, u), 'LƯU CUNG', DICH, 0.42, tilt=-15*seg(tl, 0.2, 0.8), op=1 - 0.7*seg(tl, d*0.5, d))
            + f'<text x="{x:.0f}" y="{y+100*U:.0f}" font-family="Playfair Display" font-weight="800" font-size="{20*U:.0f}" fill="#2A1A10" text-anchor="middle">Hải Môn (vị trí minh họa)</text>'
            + chip('LƯU CUNG RÚT QUÂN') + note())

SCENES = [('s35', 1, s35), ('s36', 3, s36), ('s37', 4, s37), ('s38', 5, s38), ('s39', 6, s39), ('s40', None, s40),
          ('s41', 10, s41), ('s42', 16, s42), ('s43', 17, s43), ('s44', 20, s44), ('s45', 22, s45), ('s46', 24, s46)]
REGION_SCENES = {'s46'}

def subtitle(text):
    if not text: return ''
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        if len(cur) + len(w_) + 1 > 34 and cur: lines.append(cur); cur = w_
        else: cur = (cur + ' ' + w_).strip()
    lines.append(cur); fs = 24 * U; o = []
    for k, ln in enumerate(lines[-2:]):
        yy = H - (24 + (len(lines[-2:]) - 1 - k) * 32) * U
        base = f'x="{W/2:.0f}" y="{yy:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{fs:.0f}" text-anchor="middle"'
        o.append(f'<text {base} fill="{MUC}" stroke="{MUC}" stroke-width="{6*U:.1f}" stroke-linejoin="round">{ln}</text>')
        o.append(f'<text {base} fill="#FFFFFF">{ln}</text>')
    return ''.join(o)

def main():
    js, mp3 = sys.argv[1], sys.argv[2]
    meta = json.load(open(js)); lines = meta['lines']
    t10 = lines[9]['start']                  # chèn lặng trước câu 10
    def T(t): return t + (SIL if t >= t10 - 0.05 else 0)
    total = T(meta['duration']) + 0.8
    starts = []
    for code, ln, fn in SCENES:
        starts.append(t10 if code == 's40' else (0.0 if ln == 1 else T(lines[ln - 1]['start']) - 0.15))
    starts.append(total)
    region = L.base_frame((112.3, 22.3, 1400.0)).convert('RGBA')
    src = open(__file__, 'rb').read() + open(L.__file__, 'rb').read()
    os.makedirs('clips', exist_ok=True); files = []
    subs = [(T(x['start']), T(x['end']) + 0.2, x['text']) for x in lines]
    for k, (code, ln, fn) in enumerate(SCENES):
        a, b = starts[k], starts[k + 1]; d = b - a
        key = hashlib.sha1(src + f'{code}{a:.2f}{d:.2f}{W}'.encode() + json.dumps(subs).encode()).hexdigest()[:10]
        out = f'clips/E2c-{code}-{W}-{key}.mp4'; files.append(out)
        if os.path.exists(out): print(code, 'cache'); continue
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast' if L.FINAL else 'ultrafast', '-crf', '20' if L.FINAL else '26', out], stdin=subprocess.PIPE)
        n = round(b * FPS) - round(a * FPS)
        for i in range(n):
            tg = (round(a * FPS) + i) / FPS; tl = tg - a
            sub = next((s for s0, s1, s in subs if s0 <= tg < s1), '')
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{fn(tl, d)}{subtitle(sub)}</svg>'
            ov = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
            if code in REGION_SCENES: fr = region.copy(); fr.alpha_composite(ov)
            else: fr = ov
            fa = min(1, tl / 0.2, (d - tl) / 0.2) if code in ('s46',) else 1
            if fa < 1: fr = Image.blend(Image.new('RGBA', (W, H), (20, 17, 15, 255)), fr, max(0, fa))
            p.stdin.write(fr.convert('RGB').tobytes())
        p.stdin.close(); p.wait(); print(code, f'ok {d:.1f}s')
    open('list.txt', 'w').write(''.join(f"file '{f}'\n" for f in files))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'hinh.mp4'], check=True)
    # tiếng: chèn 2 giây lặng tại t10
    af = (f"[0:a]atrim=0:{t10},asetpts=PTS-STARTPTS[a1];[0:a]atrim={t10},asetpts=PTS-STARTPTS[a2];"
          f"anullsrc=r=44100:cl=mono,atrim=0:{SIL}[s];[a1][s][a2]concat=n=3:v=0:a=1[a]")
    name = 'E2-thu-caotrao-' + ('1080p' if L.FINAL else 'nhap') + '.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'hinh.mp4', '-i', mp3, '-filter_complex', af.replace('[0:a]', '[1:a]'),
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', name], check=True)
    print('->', name, f'{total:.1f}s')

if __name__ == '__main__':
    main()
