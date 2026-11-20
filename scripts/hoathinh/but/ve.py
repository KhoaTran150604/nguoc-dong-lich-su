"""Vẽ một nhân vật từ spec (scripts/hoathinh/but/nv/<ma>.py) bằng bộ Bút.

Chạy:
    python scripts/hoathinh/but/ve.py sa-tang                 # → build/thu-hoathinh/but/sa-tang.png
    python scripts/hoathinh/but/ve.py sa-tang --scale 2       # ảnh gấp đôi (nét vẫn sắc)
    python scripts/hoathinh/but/ve.py sa-tang --bieu-cam vui --mieng cuoi_mo
    python scripts/hoathinh/but/ve.py sa-tang --so-cu build/thu-hoathinh/nhan-vat/sa-tang.png   # ảnh so cũ/mới

Thứ tự LỚP (sau → trước) cố định cho mọi nhân vật – xem LOP.
"""
import argparse
import copy
import importlib
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import bo_phan as bp  # noqa: E402
from but import Buc, gop  # noqa: E402
from khung import Khung  # noqa: E402

# (khoá spec cần có, hàm vẽ) – None = luôn vẽ
LOP = [
    ('duoi', bp.duoi_xoan),
    ('mu', bp.day_mu),
    (None, bp.tai),
    ('co_nguoi', bp.co_nguoi),
    ('ao', bp.ao_giao_linh),
    ('chuoi_so', bp.chuoi_so),
    ('khan', bp.khan_co),
    ('vu_khi', bp.vu_khi),
    (None, bp.dau_da),
    ('mat_na', bp.mat_na),
    ('toc', bp.toc_chom),
    ('vong_tran', bp.vong_tran),
    ('mu', bp.mu),
    ('rau', bp.rau_quai_non),
    ('mat', bp.mat),
    ('vu_khi', bp.ban_tay),
]


def nap(ma):
    return copy.deepcopy(importlib.import_module('nv.' + ma.replace('-', '_')).NV)


def ve(NV, ra, scale=1.0, head_c=(413, 399), canvas=(800, 1000), nen='#F6F3EC', bong_den=False):
    k = Khung(head_c, dang=NV.get('dang', 'chuan'), K=NV.get('K'))
    b = Buc(*canvas, nen=nen, D=k.D(), scale=scale)
    for khoa, ham in LOP:
        if khoa is None or NV.get(khoa):
            ham(b, k, NV)
    u = b.chot_vien()
    os.makedirs(os.path.dirname(ra), exist_ok=True)
    if bong_den:                       # phép thử BÓNG DÁNG: tô đen cả nhân vật – vẫn phải nhận ra là ai
        s = Buc(*canvas, nen='#FFFFFF', D=k.D(), scale=scale)
        s.to((u + gop(*b.dang_phu)).phong(b.D['ngoai'] / 2) if b.dang_phu else u.phong(b.D['ngoai'] / 2), '#000000')
        for lo in b.lo:
            s.to(lo.phong(-b.D['trong'] / 2), '#FFFFFF')
        s.luu(ra.replace('.png', '-bong.png'))
    return b.luu(ra)


def so_sanh(cu, moi, ra, nhan=('BẢN CŨ', 'BỘ BÚT')):
    from PIL import Image, ImageDraw, ImageFont
    a, c = Image.open(cu).convert('RGB'), Image.open(moi).convert('RGB')
    c = c.resize((int(c.width * a.height / c.height), a.height))
    out = Image.new('RGB', (a.width + c.width, a.height + 60), (255, 255, 255))
    out.paste(a, (0, 60))
    out.paste(c, (a.width, 60))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 30)
    d.text((20, 14), nhan[0], font=f, fill=(150, 150, 150))
    d.text((a.width + 20, 14), nhan[1], font=f, fill=(40, 110, 200))
    out.save(ra)
    return ra


BIEU_CAM = [('hien', 'cuoi', 'Hiền'), ('vui', 'cuoi_mo', 'Vui'), ('quyet', 'mim', 'Quyết'),
            ('ngac', 'o', 'Ngạc nhiên'), ('buon', 'buon', 'Buồn'), ('cuoi_nham', 'cuoi_to', 'Cười híp')]


def bang_bieu_cam(NV, ra):
    """Lưới 6 biểu cảm (cắt khung quanh đầu) – kiểm tra mặt dùng được cho hoạt hình."""
    from PIL import Image, ImageDraw, ImageFont
    tmp = []
    for bc, mi, _ in BIEU_CAM:
        N = copy.deepcopy(NV)
        N['mat']['bieu_cam'], N['mat']['mieng'] = bc, mi
        p = ra.replace('.png', f'-{bc}.png')
        ve(N, p)
        tmp.append(p)
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    W, H = 360, 400
    out = Image.new('RGB', (W * 3, H * 2), (246, 243, 236))
    d = ImageDraw.Draw(out)
    for i, (p, (_, _, ten)) in enumerate(zip(tmp, BIEU_CAM)):
        im = Image.open(p).convert('RGB').crop((233, 239, 593, 599))
        out.paste(im, ((i % 3) * W, (i // 3) * H + 40))
        d.text(((i % 3) * W + 16, (i // 3) * H + 6), ten, font=f, fill=(60, 60, 60))
        os.remove(p)
    out.save(ra)
    return ra


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('ma')
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--bieu-cam')
    ap.add_argument('--mieng')
    ap.add_argument('--ra')
    ap.add_argument('--so-cu')
    ap.add_argument('--bieu-cam-bang', action='store_true', help='xuất thêm lưới 6 biểu cảm')
    ap.add_argument('--bong-den', action='store_true', help='xuất thêm ảnh bóng dáng tô đen (<ma>-bong.png)')
    a = ap.parse_args()
    NV = nap(a.ma)
    if a.bieu_cam:
        NV['mat']['bieu_cam'] = a.bieu_cam
    if a.mieng:
        NV['mat']['mieng'] = a.mieng
    ra = a.ra or os.path.join(ROOT, 'build', 'thu-hoathinh', 'but', f'{a.ma}.png')
    print('xong:', ve(NV, ra, a.scale, bong_den=a.bong_den))
    if a.so_cu:
        print('so sánh:', so_sanh(a.so_cu, ra, ra.replace('.png', '-so-cu.png')))
    if a.bieu_cam_bang:
        print('biểu cảm:', bang_bieu_cam(NV, ra.replace('.png', '-bieu-cam.png')))
