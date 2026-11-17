"""Cắt SHORT 9:16 từ video dài đã render – dùng cho mọi tập/phần.

    python3 scripts/video/short.py e2 1          # cấu hình ở SHORTS bên dưới (hoặc tap/<mã>.py: SHORTS)
Cấu trúc một Short:  [HOOK câu hỏi ~3s] → [đoạn cắt từ video dài, có phụ đề] → [DẪN sang phần sau] → [ĐĂNG KÝ 4,5s]
- Hình: khung 1080×1920; giữa là video dài (cắt giữa, phóng to), nền là chính video đó làm mờ, trên có nhãn tập/phần.
- Tiếng: giữ nguyên tiếng video dài (giọng + hiệu ứng); hook và câu dẫn là giọng Gia Huy tạo thêm (tts.py).
- Phụ đề lấy từ mốc từng câu trong <giọng>.json → không phải căn tay.
- Thumbnail 1080×1920 xuất kèm (dùng cho Shorts/TikTok/Reels).
"""
import io, json, math, os, subprocess, sys
import numpy as np
import cairosvg
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import dung as D            # đọc lời đọc + mốc thời gian giống hệt lúc dựng video dài
import amthanh as AT

W, H, FPS = 1080, 1920, 60
MUC, DONG, DONG2, KEM, DO = '#14110F', '#C9A24A', '#F3D27A', '#F2E6CC', '#B3261E'
AVATAR = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'AVATAR-YouTube-800x800.png')
FG = dict(cw=1260, y=380)          # cắt giữa video 16:9 rộng 1260px → phóng thành 1080 rộng, đặt ở y=380

SHORTS = {
    ('e2', 1): dict(
        video='build/e2/E2-1080p60.mp4', loi_doc='docs/videos/E2-loi-doc.txt', giong='assets/e2/E2-GiaHuy-v2', tail=7.0,
        tu='s02', den='s06',                                   # cắt từ đầu cảnh s02 đến trước cảnh s06
        nhan='BẠCH ĐẰNG 938', phan='PHẦN 1',
        hook='MỘT HÀNG CỌC GỖ\nĐÁNH CHÌM CẢ HẠM ĐỘI?',          # chữ trên màn hình mở đầu
        dan='XEM TIẾP\nPHẦN 2',                               # chữ trên màn hình dẫn
        them='build/short/e2-p1/them',                         # giọng thêm: câu 1 = hook, các câu sau = dẫn
        thumb_t=12.0,                                          # giây (trong đoạn cắt) lấy hình thumbnail
        thumb_chu='MỘT HÀNG\nCỌC GỖ\nĐÁNH CHÌM\nCẢ HẠM ĐỘI?'),
}

def sh(cmd): subprocess.run(cmd, check=True)
def svg_png(svg): return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')

def _lines_text(t, size, col, y, stroke=MUC, sw=10, anchor='middle', x=W / 2, fam='Playfair Display', weight='800', ls=2):
    o = []
    for i, ln in enumerate(t.split('\n')):
        yy = y + i * size * 1.12
        o.append(f'<text x="{x}" y="{yy:.0f}" font-family="{fam}" font-weight="{weight}" font-size="{size}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" text-anchor="{anchor}" letter-spacing="{ls}">{ln}</text>'
                 f'<text x="{x}" y="{yy:.0f}" font-family="{fam}" font-weight="{weight}" font-size="{size}" fill="{col}" text-anchor="{anchor}" letter-spacing="{ls}">{ln}</text>')
    return ''.join(o)

def title_band(c):
    """Nhãn trên cùng: tên trận + PHẦN n + avatar nhỏ."""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
         f'<rect x="0" y="0" width="{W}" height="330" fill="{MUC}" opacity="0.55"/>',
         _lines_text(c['nhan'], 92, DONG2, 205, sw=12),
         f'<rect x="{W/2-120}" y="238" width="240" height="64" rx="32" fill="{DO}" stroke="{DONG2}" stroke-width="4"/>',
         f'<text x="{W/2}" y="283" font-family="Be Vietnam Pro SemiBold" font-size="38" fill="#FFFFFF" text-anchor="middle">{c["phan"]}</text>']
    import base64; av = 'data:image/png;base64,' + base64.b64encode(open(AVATAR, 'rb').read()).decode()
    o.append(f'<defs><clipPath id="a"><circle cx="{W/2}" cy="1810" r="58"/></clipPath></defs><image href="{av}" x="{W/2-58}" y="1752" width="116" height="116" clip-path="url(#a)"/>')
    o.append(f'<text x="{W/2}" y="1735" font-family="Be Vietnam Pro SemiBold" font-size="30" fill="{KEM}" text-anchor="middle" opacity="0.85">Song Tử Kể Sử</text>')
    return ''.join(o) + '</svg>'

def ass_subs(lines, path):
    """Phụ đề ASS: chữ trắng viền đen, tối đa 2 dòng, đặt ở ~80% chiều cao (quy ước kênh cho 9:16)."""
    def ts(t): t = max(0, t); return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
    def wrap(s, n=24):
        w, out, cur = s.split(), [], ''
        for x in w:
            if len(cur) + len(x) + 1 > n and cur: out.append(cur); cur = x
            else: cur = (cur + ' ' + x).strip()
        out.append(cur)
        if len(out) > 2: out = [' '.join(out[:len(out)//2]), ' '.join(out[len(out)//2:])]
        return r'\N'.join(out)
    hdr = ('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n'
           'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
           'Style: S,Be Vietnam Pro SemiBold,62,&H00FFFFFF,&H00FFFFFF,&H000F1114,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,60,60,330,1\n\n'
           '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
    ev = ''.join(f'Dialogue: 0,{ts(a)},{ts(b)},S,,0,0,0,,{wrap(t)}\n' for a, b, t in lines)
    open(path, 'w', encoding='utf-8').write(hdr + ev)

def compose(src, t0, dur, subs, overlay_png, out):
    """Video dài [t0, t0+dur] → khung dọc: nền mờ + video giữa phóng to + nhãn + phụ đề."""
    cw, y = FG['cw'], FG['y']; fh = round(1080 * 1080 / cw / 2) * 2
    fc = (f'[0:v]split[a][b];[a]scale=-2:{H},crop={W}:{H},gblur=sigma=28,eq=brightness=-0.18[bg];'
          f'[b]crop={cw}:1080:(iw-{cw})/2:0,scale={W}:{fh}[fg];[bg][fg]overlay=0:{y}[v1];[v1][1:v]overlay=0:0[v2];'
          f"[v2]ass='{subs}'[v]")
    sh(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', src, '-i', overlay_png, '-filter_complex', fc,
        '-map', '[v]', '-map', '0:a', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '1', out])

def still_clip(base, overlay_fn, dur, audio, out):
    """Clip từ ảnh nền + lớp phủ động (overlay_fn(t) -> svg phần thân) + tiếng (mảng numpy)."""
    wav = out + '.wav'; AT.write_wav(np.pad(audio, (0, max(0, int(dur * AT.SR) - len(audio))))[: int(dur * AT.SR)], wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '1', '-shortest', out],
                         stdin=subprocess.PIPE)
    prev = None
    for i in range(int(round(dur * FPS))):
        t = i / FPS; svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{overlay_fn(t)}</svg>'
        if svg != prev:
            fr = base.copy(); fr.alpha_composite(svg_png(svg)); buf = fr.convert('RGB').tobytes(); prev = svg
        p.stdin.write(buf)
    p.stdin.close(); p.wait()

def pop(t, t0=0.0, d=0.35):
    u = min(1, max(0, (t - t0) / d)); return 1 + 0.25 * math.sin(u * math.pi) * (1 - u) if u < 1 else 1, u

def hook_overlay(text):
    def f(t):
        k, u = pop(t, 0.05)
        return (f'<rect width="{W}" height="{H}" fill="{MUC}" opacity="{0.55*min(1, t/0.2):.2f}"/>'
                f'<g opacity="{u:.2f}" transform="translate({W/2} 820) scale({k:.3f}) translate({-W/2} -820)">'
                f'<rect x="60" y="640" width="{W-120}" height="{90 + 90*len(text.split(chr(10)))}" rx="36" fill="{MUC}" stroke="{DONG}" stroke-width="6"/>'
                + _lines_text(text, 74, DONG2, 765, sw=0) + '</g>')
    return f

def lead_overlay(text):
    def f(t):
        k, u = pop(t, 0.1); a = 0.5 + 0.5 * math.sin(t * 6)
        return (f'<rect width="{W}" height="{H}" fill="{MUC}" opacity="{0.6*min(1, t/0.25):.2f}"/>'
                f'<g opacity="{u:.2f}" transform="translate({W/2} 900) scale({k:.3f}) translate({-W/2} -900)">'
                + _lines_text(text, 112, DONG2, 860, sw=14) +
                f'<polygon points="{W/2+250},{1010} {W/2+250},{1090} {W/2+320},{1050}" fill="{DO}" opacity="{a:.2f}"/>' +
                f'<rect x="{W/2-260}" y="1040" width="520" height="12" rx="6" fill="{DO}" opacity="{a:.2f}"/></g>')
    return f

def subscribe_vertical(t):
    """Màn hình đăng ký khung dọc: avatar + Thích / ĐĂNG KÝ / Chuông, nhấp nháy như video dài."""
    import base64
    av = 'data:image/png;base64,' + base64.b64encode(open(AVATAR, 'rb').read()).decode()
    pk = min(1, t / 0.5); s = 520 * (0.6 + 0.4 * pk); cx, ay = W / 2, 700
    pl = max(0, math.sin((t - 1.0) * 2 * math.pi * 1.2)) if t > 1.0 else 0
    ps = max(0, math.sin((t - 1.6) * 2 * math.pi * 1.2)) if t > 1.6 else 0
    on = t > 1.6; done = t > 3.0
    o = [f'<rect width="{W}" height="{H}" fill="{MUC}"/>',
         f'<defs><clipPath id="c"><circle cx="{cx}" cy="{ay}" r="{s/2:.0f}"/></clipPath></defs>',
         f'<image href="{av}" x="{cx-s/2:.0f}" y="{ay-s/2:.0f}" width="{s:.0f}" height="{s:.0f}" clip-path="url(#c)" opacity="{pk:.2f}"/>']
    by = 1150; o.append(f'<rect x="90" y="{by}" width="{W-180}" height="190" rx="48" fill="{KEM}" stroke="{DONG}" stroke-width="6"/>')
    lk = 1 + 0.25 * pl; lc = '#2F7BEA' if t > 1.0 else '#3A3A3A'
    o.append(f'<g transform="translate(230 {by+95}) scale({2.2*lk:.2f})"><circle r="40" fill="#2F7BEA" opacity="{0.25*pl:.2f}"/><rect x="-22" y="-4" width="11" height="26" rx="3" fill="{lc}"/><path d="M-8,-4 L2,-24 Q6,-32 12,-26 Q14,-20 10,-8 L22,-8 Q28,-7 26,0 L22,18 Q20,22 15,22 L-8,22 Z" fill="{lc}"/></g>')
    sk = 1 + 0.1 * ps; bg = '#CC1F1A' if on else MUC
    o.append(f'<g transform="translate(600 {by+95}) scale({sk:.3f})"><rect x="-200" y="-55" width="400" height="110" rx="55" fill="{bg}"/>'
             f'<rect x="-175" y="-26" width="70" height="52" rx="14" fill="#FFFFFF"/><polygon points="-150,-14 -150,14 -124,0" fill="{bg}"/>'
             f'<text x="50" y="16" font-family="Be Vietnam Pro SemiBold" font-size="{40 if done else 46}" fill="#FFFFFF" text-anchor="middle">{"ĐÃ ĐĂNG KÝ" if done else "ĐĂNG KÝ"}</text>'
             f'<rect x="-212" y="-67" width="424" height="134" rx="67" fill="none" stroke="#CC1F1A" stroke-width="6" opacity="{0.8*ps:.2f}"/></g>')
    wob = 18 * math.sin(t * 18) * max(0, 1 - abs(t - 3.4) * 2) if t > 3.0 else 0
    o.append(f'<g transform="translate(905 {by+95}) rotate({wob:.1f} 0 -50) scale(2.1)"><path d="M-18,12 Q-18,-20 0,-22 Q18,-20 18,12 L24,18 L-24,18 Z" fill="#2A2A2A"/><circle cy="24" r="6" fill="#2A2A2A"/><rect x="-3" y="-30" width="6" height="8" rx="2" fill="#2A2A2A"/></g>')
    o.append(_lines_text('SONG TỬ KỂ SỬ', 70, DONG2, 1520, sw=0, ls=4))
    o.append(f'<text x="{W/2}" y="1600" font-family="Be Vietnam Pro SemiBold" font-size="40" text-anchor="middle"><tspan fill="{DONG2}">Văn kể sử</tspan></text>')
    o.append(f'<text x="{W/2}" y="1660" font-family="Be Vietnam Pro SemiBold" font-size="40" fill="#E8604A" text-anchor="middle">Võ dẫn trận</text>')
    return ''.join(o)

def thumbnail(frame, c, out):
    """Thumbnail 1080×1920: khung hình đắt + câu hỏi lớn + PHẦN n + avatar."""
    im = frame.copy()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
           f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MUC}" stop-opacity="0.92"/><stop offset="0.45" stop-color="{MUC}" stop-opacity="0.15"/>'
           f'<stop offset="0.7" stop-color="{MUC}" stop-opacity="0.15"/><stop offset="1" stop-color="{MUC}" stop-opacity="0.9"/></linearGradient></defs>'
           f'<rect width="{W}" height="{H}" fill="url(#g)"/>' + _lines_text(c['thumb_chu'], 112, DONG2, 230, sw=16, ls=2) +
           f'<rect x="{W/2-170}" y="1520" width="340" height="96" rx="48" fill="{DO}" stroke="{DONG2}" stroke-width="5"/>'
           f'<text x="{W/2}" y="1586" font-family="Be Vietnam Pro SemiBold" font-size="56" fill="#FFFFFF" text-anchor="middle">{c["phan"]}</text>'
           + _lines_text(c['nhan'], 80, KEM, 1750, sw=10) + '</svg>')
    im.alpha_composite(svg_png(svg)); im.convert('RGB').save(out, quality=92)

def get_cfg(tap, n):
    if (tap, n) in SHORTS: return SHORTS[(tap, n)]
    import importlib; sys.modules['dung'] = D
    ep = importlib.import_module('tap.' + tap); c = dict(ep.SHORTS[n]); c.setdefault('thumb_t', None); return c

def ensure_voice(c):
    """Tạo giọng câu hook + câu dẫn nếu chưa có (giọng Gia Huy, có kiểm tra phát âm)."""
    if os.path.exists(c['them'] + '.json') or 'hook_doc' not in c: return
    os.makedirs(os.path.dirname(c['them']), exist_ok=True)
    open(c['them'] + '.txt', 'w', encoding='utf-8').write(c['hook_doc'] + '\n\n' + '\n'.join(c['dan_doc']) + '\n')
    env = dict(os.environ, HF_HUB_DISABLE_XET='1')
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'voice', 'tts.py'), c['them'] + '.txt', '-o', c['them'], '--check'],
                   check=True, env=env, stdout=open(c['them'] + '.log', 'w'), stderr=subprocess.STDOUT)

def progress(done, total, t0, label, path=os.path.join(ROOT, 'build', 'short', 'tien-do.txt')):
    import time
    f = done / total; el = time.time() - t0; eta = el / f * (1 - f) if f else 0
    line = f'Short {"█" * int(f * 20)}{"░" * (20 - int(f * 20))} {f*100:3.0f}%  ({done}/{total} bước)  đã {el/60:.1f} phút · còn ~{eta/60:.1f} phút  [{label}]'
    print(line, flush=True); os.makedirs(os.path.dirname(path), exist_ok=True); open(path, 'w').write(line + '\n')

def main():
    tap, spec = sys.argv[1], sys.argv[2]
    if '-' in spec or ',' in spec:          # nhiều phần: "2-8" hoặc "2,4,5" → giọng rồi dựng, có thanh tiến độ
        import time
        ns = list(range(int(spec.split('-')[0]), int(spec.split('-')[1]) + 1)) if '-' in spec else [int(x) for x in spec.split(',')]
        t0 = time.time(); total = 2 * len(ns); k = 0
        for n in ns:
            ensure_voice(get_cfg(tap, n)); k += 1; progress(k, total, t0, f'giọng P{n}')
        for n in ns:
            build(tap, n); k += 1; progress(k, total, t0, f'dựng P{n}')
        print('XONG TẤT CẢ', flush=True); return
    build(tap, int(spec))

def build(tap, n):
    c = get_cfg(tap, n); ensure_voice(c)
    od = os.path.join(ROOT, 'build', 'short', f'{tap}-p{n}'); os.makedirs(od, exist_ok=True)
    os.chdir(ROOT)
    # 1) mốc thời gian trong video dài
    items = D.read_script(c['loi_doc']); meta = json.load(open(c['giong'] + '.json'))
    times, pauses, end = D.timeline(items, meta, c['tail']); plan = D.plan_scenes(items, times, pauses, end)
    st = {code: a for code, a, b in plan}; t0, t1 = st[c['tu']], st[c['den']]
    subs = [(a - t0, b - t0 + 0.15, txt) for (a, b), (_, txt, _) in zip(times, items) if a >= t0 - 0.05 and a < t1]
    ass = os.path.join(od, 'phude.ass'); ass_subs(subs, ass)
    band = os.path.join(od, 'nhan.png'); svg_png(title_band(c)).save(band)
    main_mp4 = os.path.join(od, '2-doan-cat.mp4'); compose(c['video'], t0, t1 - t0, ass, band, main_mp4)
    print(f'đoạn cắt {t0:.1f}s → {t1:.1f}s ({t1-t0:.1f}s), {len(subs)} câu phụ đề')
    # 2) khung đầu/cuối làm nền cho hook và câu dẫn
    def grab(t, path):
        sh(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', main_mp4, '-frames:v', '1', path]); return Image.open(path).convert('RGBA')
    f_first = grab(0.05, os.path.join(od, 'f0.png')); f_last = grab(max(0, t1 - t0 - 0.1), os.path.join(od, 'f1.png'))
    # 3) giọng thêm: câu 1 = hook, các câu còn lại = dẫn
    m2 = json.load(open(c['them'] + '.json')); v2 = AT.load_audio(c['them'] + '.mp3'); L2 = m2['lines']
    hook_a = v2[int(L2[0]['start'] * AT.SR): int(L2[0]['end'] * AT.SR)]
    dan_a = v2[int(L2[1]['start'] * AT.SR): int(L2[-1]['end'] * AT.SR)]
    hook_a = np.concatenate([np.zeros(int(0.15 * AT.SR)), hook_a]); dan_a = np.concatenate([np.zeros(int(0.2 * AT.SR)), dan_a])
    hd = len(hook_a) / AT.SR + 0.5; dd = len(dan_a) / AT.SR + 0.6
    still_clip(f_first, hook_overlay(c['hook']), hd, hook_a + 0, os.path.join(od, '1-hook.mp4'))
    still_clip(f_last, lead_overlay(c['dan']), dd, dan_a, os.path.join(od, '3-dan.mp4'))
    sub_d = 4.5; ting = np.zeros(int(sub_d * AT.SR))
    for t, g in ((1.05, 0.25), (1.65, 0.3), (3.05, 0.2)):
        k = AT.get('kiem'); i = int(t * AT.SR); ting[i:i + len(k)] += k[: len(ting) - i] * g
    still_clip(Image.new('RGBA', (W, H), (20, 17, 15, 255)), subscribe_vertical, sub_d, ting, os.path.join(od, '4-dang-ky.mp4'))
    # 4) nối
    parts = ['1-hook.mp4', '2-doan-cat.mp4', '3-dan.mp4', '4-dang-ky.mp4']
    lst = os.path.join(od, 'list.txt'); open(lst, 'w').write(''.join(f"file '{os.path.join(od, p)}'\n" for p in parts))
    out = os.path.join(od, f'SHORT-{tap.upper()}-P{n}.mp4')
    sh(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-movflags', '+faststart', out])
    # 5) thumbnail
    # thumbnail dựng từ khung gốc của video dài (không dính phụ đề/nhãn)
    raw = os.path.join(od, 'f-thumb-goc.png'); tt = c['thumb_t'] if c.get('thumb_t') is not None else (t1 - t0) * 0.6
    sh(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t0 + tt:.3f}', '-i', c['video'], '-frames:v', '1', raw])
    g = Image.open(raw).convert('RGB'); bg = g.resize((int(g.width * H / g.height), H)).crop(((int(g.width * H / g.height) - W) // 2, 0, (int(g.width * H / g.height) - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(26))
    cw = FG['cw']; fg = g.crop(((g.width - cw) // 2, 0, (g.width + cw) // 2, g.height)).resize((W, int(W * g.height / cw)))
    bg.paste(fg, (0, 780)); thumbnail(bg.convert('RGBA'), c, os.path.join(od, f'THUMB-{tap.upper()}-P{n}.jpg'))
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    print('->', out, f'{dur:.1f}s')

if __name__ == '__main__':
    main()
