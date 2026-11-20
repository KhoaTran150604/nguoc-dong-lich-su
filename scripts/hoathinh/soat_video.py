"""Soát video hoạt hình tự động – phần ĐO bằng máy cho skill `danh-gia-video`.

Đo: nhịp cắt cảnh, nháy hình (flicker), đứng hình, khung giật, độ sáng/tương phản, màu "gradient" (dải màu mịn),
âm thanh (đỉnh, rè/clipping, độ to, khoảng lặng chết), và xuất ẢNH GHÉP khung hình cho người/agent chấm bằng mắt.

Chạy: python scripts/hoathinh/soat_video.py <video.mp4> [--out <thư mục>] [--moi 1.0]
Ra:   <out>/bao-cao.json, <out>/bao-cao.md, <out>/tong-the-NN.jpg (16 khung/ảnh, mỗi `--moi` giây),
      <out>/cat-canh.jpg (khung trước/sau mỗi lần cắt cảnh – soát nối cảnh)
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'


def probe(path):
    r = subprocess.run([ffmpeg(), '-i', path], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    import re
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    fps = float(re.search(r'([\d.]+) fps', r.stderr).group(1))
    wh = re.search(r', (\d{3,5})x(\d{3,5})', r.stderr)
    return dur, fps, int(wh.group(1)), int(wh.group(2))


def frames(path, w, h, fps=None):
    """Đọc toàn bộ khung (thu nhỏ w x h) dạng mảng uint8."""
    cmd = [ffmpeg(), '-loglevel', 'error', '-i', path]
    if fps:
        cmd += ['-vf', 'fps=%g,scale=%d:%d' % (fps, w, h)]
    else:
        cmd += ['-vf', 'scale=%d:%d' % (w, h)]
    cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def audio(path, sr=24000):
    raw = subprocess.run([ffmpeg(), '-loglevel', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0, sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--out')
    ap.add_argument('--moi', type=float, default=1.0, help='khoảng giây giữa 2 khung trong ảnh ghép')
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.video)), 'soat')
    os.makedirs(out, exist_ok=True)
    dur, fps, W, H = probe(a.video)
    R = {'video': os.path.abspath(a.video), 'thoi_luong': round(dur, 2), 'fps': fps, 'co': [W, H]}
    canh_bao = []

    # ---------------- chuyển động: diff giữa các khung liên tiếp (ảnh nhỏ 160x90)
    fr = frames(a.video, 160, 90).astype(np.float32)
    diff = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2, 3))
    luma = (fr * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1)
    med = float(np.median(diff)) + 1e-3
    cut_thr = max(18.0, med * 8)
    cuts = [i + 1 for i in range(len(diff)) if diff[i] > cut_thr]
    # gộp cắt sát nhau (chuyển cảnh nhiều khung)
    merged = []
    for c in cuts:
        if not merged or c - merged[-1] > 3:
            merged.append(c)
    cut_t = [round(c / fps, 2) for c in merged]
    shots = np.diff([0.0] + cut_t + [dur])
    R['cat_canh'] = cut_t
    R['so_canh'] = len(shots)
    R['do_dai_canh'] = dict(tb=round(float(shots.mean()), 2), min=round(float(shots.min()), 2), max=round(float(shots.max()), 2))
    for i, s in enumerate(shots):
        t0 = 0 if i == 0 else cut_t[i - 1]
        if s > 8.0:
            canh_bao.append(dict(loai='canh_qua_dai', t=t0, chi_tiet='cảnh dài %.1fs (chuẩn sitcom: 3–6s, tối đa ~8s)' % s))
        if s < 0.35 and 0 < i < len(shots) - 1:
            canh_bao.append(dict(loai='canh_qua_ngan', t=t0, chi_tiet='cảnh chỉ %.2fs – có thể là khung lỗi chen giữa' % s))
    # nháy hình: khung i khác hẳn i-1 và i+1 nhưng i-1 ≈ i+1
    for i in range(1, len(fr) - 1):
        a_, b_ = diff[i - 1], diff[i]
        if a_ > max(10, med * 5) and b_ > max(10, med * 5):
            if np.abs(fr[i + 1] - fr[i - 1]).mean() < max(4, med * 2):
                canh_bao.append(dict(loai='nhay_hinh', t=round(i / fps, 2), chi_tiet='1 khung lạc (nháy) – kiểm tra hình ở giây này'))
    # đứng hình: diff ~0 kéo dài
    still = diff < 0.15
    run = 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run == int(2.5 * fps):
            canh_bao.append(dict(loai='dung_hinh', t=round((i - run + 1) / fps, 2), chi_tiet='hình đứng yên ≥2.5s (không chớp mắt/khẩu hình?)'))
    # giật: chuyển động trong cảnh đột ngột lớn nhưng chưa tới ngưỡng cắt
    jerk_thr = max(8.0, med * 4)
    for i in range(1, len(diff) - 1):
        if jerk_thr < diff[i] <= cut_thr and diff[i] > 3 * max(diff[i - 1], diff[i + 1], 0.5):
            canh_bao.append(dict(loai='giat', t=round((i + 1) / fps, 2), chi_tiet='bước nhảy hình đột ngột trong cảnh (vật/nhân vật nhảy vị trí?)'))
    # ---------------- ánh sáng
    per_s = [luma[int(k * fps):int((k + 1) * fps)] for k in range(int(dur))]
    sang = [round(float(x.mean()), 1) for x in per_s if len(x)]
    tuong_phan = [round(float(x.std()), 1) for x in per_s if len(x)]
    R['sang_moi_giay'] = sang
    R['tuong_phan_moi_giay'] = tuong_phan
    for k, (s, c) in enumerate(zip(sang, tuong_phan)):
        if s < 45:
            canh_bao.append(dict(loai='qua_toi', t=k, chi_tiet='độ sáng TB %.0f/255' % s))
        if s > 215:
            canh_bao.append(dict(loai='qua_sang', t=k, chi_tiet='độ sáng TB %.0f/255 (cháy sáng)' % s))
        if c < 22:
            canh_bao.append(dict(loai='it_tuong_phan', t=k, chi_tiet='tương phản thấp (std %.0f) – hình bệt/đục' % c))
    # dải màu mịn (gradient) – lối sitcom cấm: đếm số màu phân biệt trong 1 khung/giây (ảnh vẽ phẳng có ít màu)
    big = frames(a.video, 320, 180, fps=1)
    nmau = []
    for k, f in enumerate(big):
        q = (f // 8).reshape(-1, 3)
        u = np.unique(q[:, 0].astype(np.int32) * 1024 + q[:, 1] * 32 + q[:, 2]).size
        nmau.append(int(u))
    R['so_mau_moi_giay'] = nmau
    # màu ám toàn khung (cast) – kênh màu lệch mạnh
    for k, f in enumerate(big):
        m = f.reshape(-1, 3).mean(0)
        if m.max() - m.min() > 70:
            canh_bao.append(dict(loai='am_mau', t=k, chi_tiet='cả khung ám màu mạnh (R,G,B TB = %d,%d,%d)' % tuple(m)))

    # ---------------- âm thanh
    au, sr = audio(a.video)
    R['am_thanh'] = {}
    if au.size:
        peak = float(np.abs(au).max())
        clip = float((np.abs(au) > 0.985).mean())
        hop = sr // 10
        rms = np.array([np.sqrt(np.mean(au[k:k + hop] ** 2)) for k in range(0, au.size - hop, hop)])
        db = 20 * np.log10(rms + 1e-6)
        R['am_thanh'] = dict(dinh=round(peak, 3), ti_le_re=round(clip, 5), do_to_tb_db=round(float(db.mean()), 1),
                             do_to_p95_db=round(float(np.percentile(db, 95)), 1))
        if clip > 0.0005:
            canh_bao.append(dict(loai='re_tieng', t=None, chi_tiet='%.3f%% mẫu bị chạm trần (rè)' % (clip * 100)))
        if np.percentile(db, 95) < -22:
            canh_bao.append(dict(loai='tieng_nho', t=None, chi_tiet='tiếng nhỏ (p95 %.1f dBFS) – nên nâng tới ~-14' % np.percentile(db, 95)))
        silent = db < -45
        run = 0
        for i, s in enumerate(silent):
            run = run + 1 if s else 0
            if run == 15:
                canh_bao.append(dict(loai='lang_chet', t=round((i - 14) / 10, 1), chi_tiet='im lặng hoàn toàn ≥1.5s (thiếu nhạc/tiếng nền?)'))
        # cú sốc âm: tăng >18 dB trong 0.1s (có thể là SFX quá to)
        for i in range(1, len(db)):
            if db[i] - db[i - 1] > 18 and db[i] > -10:
                canh_bao.append(dict(loai='tieng_dot_ngot', t=round(i / 10, 1), chi_tiet='tiếng bật quá to đột ngột'))
    R['canh_bao'] = canh_bao

    # ---------------- ảnh ghép để chấm bằng mắt
    pick = frames(a.video, 480, int(480 * H / W), fps=1 / a.moi)
    per = 16
    sheets = []
    for k in range(0, len(pick), per):
        grp = pick[k:k + per]
        cw, ch = 480, int(480 * H / W)
        sh = Image.new('RGB', (4 * cw, ((len(grp) + 3) // 4) * (ch + 22)), (20, 20, 20))
        d = ImageDraw.Draw(sh)
        for j, f in enumerate(grp):
            x, y = (j % 4) * cw, (j // 4) * (ch + 22)
            sh.paste(Image.fromarray(f), (x, y + 22))
            d.text((x + 6, y + 4), '%.1fs' % ((k + j) * a.moi), fill=(255, 220, 0))
        p = os.path.join(out, 'tong-the-%02d.jpg' % (k // per + 1))
        sh.save(p, quality=85)
        sheets.append(p)
    R['anh_ghep'] = sheets
    # khung trước/sau mỗi lần cắt
    if merged:
        cw, ch = 320, int(320 * H / W)
        rows = len(merged)
        sh = Image.new('RGB', (2 * cw + 10, rows * (ch + 20)), (20, 20, 20))
        d = ImageDraw.Draw(sh)
        full = frames(a.video, cw, ch)
        for r, c in enumerate(merged):
            y = r * (ch + 20)
            sh.paste(Image.fromarray(full[max(0, c - 1)]), (0, y + 20))
            sh.paste(Image.fromarray(full[min(len(full) - 1, c + 1)]), (cw + 10, y + 20))
            d.text((6, y + 3), 'cắt ở %.2fs' % (c / fps), fill=(255, 220, 0))
        p = os.path.join(out, 'cat-canh.jpg')
        sh.save(p, quality=82)
        R['anh_cat_canh'] = p

    json.dump(R, open(os.path.join(out, 'bao-cao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lines = ['# Báo cáo đo tự động', '', '- Video: `%s` · %.1fs · %gfps · %dx%d' % (R['video'], dur, fps, W, H),
             '- Số cảnh: %d · độ dài cảnh TB %.1fs (min %.1f, max %.1f)' % (R['so_canh'], R['do_dai_canh']['tb'], R['do_dai_canh']['min'],
                                                                          R['do_dai_canh']['max']),
             '- Âm thanh: %s' % R['am_thanh'], '- Số màu/khung (thấp = vẽ phẳng; tăng vọt = có gradient/blur): TB %d, max %d'
             % (np.mean(nmau), max(nmau)), '', '## Cảnh báo (%d)' % len(canh_bao)]
    for c in canh_bao:
        lines.append('- `%s` @ %s: %s' % (c['loai'], c['t'], c['chi_tiet']))
    lines += ['', '## Ảnh để chấm bằng mắt'] + ['- `%s`' % p for p in sheets] + (['- `%s`' % R['anh_cat_canh']] if merged else [])
    open(os.path.join(out, 'bao-cao.md'), 'w', encoding='utf-8').write('\n'.join(lines))
    print(os.path.join(out, 'bao-cao.md'))
    print('canh bao: %d' % len(canh_bao))


if __name__ == '__main__':
    main()
