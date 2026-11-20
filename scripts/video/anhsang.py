"""Lớp ÁNH SÁNG dùng chung cho mọi cảnh (nhóm 1: làm một lần, cảnh nào cũng đẹp lên).

Bộ máy dung.py vẽ mỗi khung thành 2 lớp: NỀN (bản đồ, ảnh) và LỚP PHỦ (thuyền, cờ, cọc, lính...).
Vì tách được 2 lớp nên tính được, không cần sửa từng hình vẽ:
  1. Bóng đổ   – lớp phủ đổ bóng mềm xuống nền, lệch theo hướng nắng
  2. Tô 3 tông – mép đón nắng sáng lên, mép khuất nắng tối đi (từ hình dạng của lớp phủ)
  3. Hướng nắng – nền sáng ấm phía nguồn sáng, tối dịu phía đối diện
  4. Chiều sâu – mép trên khung (xa) nhạt và mờ sương
  5. Bảng màu  – chỉnh màu toàn khung theo thời điểm (vùng tối ngả tím lạnh, vùng sáng ngả ấm), viền tối khung
  + vân giấy rất nhẹ cho cảm giác vẽ tay.
Bật trong dung.py bằng cờ --anhsang (hoặc ANH_SANG = 'ngay' trong tap/<mã>.py).
"""
import numpy as np
from PIL import Image, ImageFilter

# Bảng màu theo thời điểm. 'ngay' trung tính (mặc định) để không ám chỉ giờ giấc mà sử không chép.
PRESETS = {
    'ngay':  dict(sun=(255, 232, 188), shadow=(52, 40, 78), light_dir=(-0.62, -0.78), sun_k=0.30, dark_k=0.34,
                  haze=(238, 228, 210), haze_k=0.30, split_lo=(36, 44, 92), split_hi=(255, 222, 160), split_k=0.20,
                  contrast=1.12, sat=1.10, vignette=0.38),
    'chieu': dict(sun=(255, 206, 140), shadow=(60, 30, 70), light_dir=(-0.85, -0.52), sun_k=0.24, dark_k=0.26,
                  haze=(240, 196, 150), haze_k=0.26, split_lo=(70, 34, 86), split_hi=(255, 200, 130), split_k=0.20,
                  contrast=1.10, sat=1.08, vignette=0.32),
    'dem':   dict(sun=(196, 214, 255), shadow=(12, 16, 40), light_dir=(-0.4, -0.9), sun_k=0.10, dark_k=0.34,
                  haze=(90, 104, 140), haze_k=0.22, split_lo=(14, 22, 60), split_hi=(200, 214, 255), split_k=0.24,
                  contrast=1.06, sat=0.82, vignette=0.40),
}

_CACHE = {}


def _f(im):
    return np.asarray(im, dtype=np.float32) / 255.0


def _shift(a, dx, dy):
    """Dời mảng 2D (dx, dy) điểm ảnh, phần lộ ra = 0."""
    h, w = a.shape
    out = np.zeros_like(a)
    dx, dy = int(round(dx)), int(round(dy))
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


def _blur(a, r):
    if r <= 0:
        return a
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def _static(W, H, p, name):
    """Các lớp không đổi theo khung (gradient nắng, sương, viền tối, vân giấy) – tính một lần."""
    key = (W, H, name)
    if key in _CACHE:
        return _CACHE[key]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = xx / W - 0.5, yy / H - 0.5
    lx, ly = p['light_dir']
    # hướng nắng: +1 phía nguồn sáng, -1 phía đối diện
    g = (nx * lx + ny * ly) * 2.0
    g = np.clip(g, -1, 1)
    sun = np.clip(g, 0, 1)[..., None]
    dark = np.clip(-g, 0, 1)[..., None]
    # chiều sâu: mép trên = xa
    haze = (np.clip(1 - yy / (H * 0.55), 0, 1) ** 1.6)[..., None]
    # viền tối khung
    r = np.sqrt((nx * 1.15) ** 2 + ny ** 2)
    vig = (np.clip((r - 0.32) / 0.42, 0, 1) ** 1.5)[..., None]
    # vân giấy
    rng = np.random.default_rng(7)
    n = rng.random((H // 3 + 1, W // 3 + 1)).astype(np.float32)
    grain = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), dtype=np.float32) / 255.0
    fine = rng.random((H, W)).astype(np.float32)
    paper = (1 + (grain - 0.5) * 0.05 + (fine - 0.5) * 0.025)[..., None]
    _CACHE[key] = (sun, dark, haze, vig, paper)
    return _CACHE[key]


def _khoi(B, O, p, U, manh=1.0):
    """Ghép lớp O (RGBA float) lên nền B (RGB float) có bóng đổ + tô 3 tông. Trả RGB float."""
    a = O[..., 3]
    if a.max() <= 0.01:
        return B
    lx, ly = p['light_dir']
    SUN = np.array(p['sun'], np.float32) / 255
    SHD = np.array(p['shadow'], np.float32) / 255
    # 1. bóng đổ: lệch ngược hướng nắng, mềm, ngả tím
    d = 9 * U
    sh = _blur(_shift(a, -lx * d, -ly * d), 4.5 * U) * 0.62 * manh
    sh = sh * (1 - a * 0.85)                      # không tự đổ bóng lên chính nó
    B = B * (1 - sh[..., None]) + (B * SHD * 1.5) * sh[..., None]
    # 2. tô 3 tông: mép đón nắng sáng ấm / phần khuất nắng tối lạnh
    r = max(1.5, 2.6 * U)
    rim = np.clip(a - _shift(a, -lx * r, -ly * r), 0, 1)
    rim = _blur(rim, 0.7 * U) * a
    edge = np.clip(a - _shift(a, lx * r, ly * r), 0, 1)
    body = np.clip(a - _blur(_shift(a, lx * 7 * U, ly * 7 * U), 2.5 * U), 0, 1)
    body = _blur(body, 2 * U)
    shade = np.clip(edge * 0.9 + body * 0.75, 0, 1) * a
    C = O[..., :3]
    kr, ks = 0.7 * manh, 0.5 * manh
    C = C * (1 - kr * rim[..., None]) + np.minimum(1, C * 0.55 + SUN * 0.8) * (kr * rim[..., None])
    C = C * (1 - ks * shade[..., None]) + (C * SHD * 2.0) * (ks * shade[..., None])
    A = a[..., None]
    return B * (1 - A) + C * A


def noi_khoi(base, lop, name='ngay', U=1.0, manh=1.0):
    """Cho nền bản đồ: ghép lớp vật (đồi, cây, đảo) lên mặt đất, có bóng + 3 tông. Trả RGBA."""
    F = _khoi(_f(base.convert('RGB')), _f(lop), PRESETS[name], U, manh)
    return Image.fromarray(np.clip(F * 255 + 0.5, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


def ap_dung(bg, ov, name='ngay', U=1.0):
    """bg, ov: ảnh RGBA cùng cỡ (nền, lớp phủ). Trả ảnh RGB đã có ánh sáng."""
    p = PRESETS[name]
    W, H = bg.size
    sun, dark, haze, vig, paper = _static(W, H, p, name)
    SUN = np.array(p['sun'], np.float32) / 255
    SHD = np.array(p['shadow'], np.float32) / 255

    B = _f(bg.convert('RGB'))
    # nền: nắng ấm phía nguồn sáng, tối dịu phía kia, sương phía xa
    B = B * (1 - p['sun_k'] * sun) + np.minimum(1, B * SUN * 1.25) * (p['sun_k'] * sun)
    B = B * (1 - p['dark_k'] * dark) + (B * SHD * 2.2) * (p['dark_k'] * dark)
    B = B * (1 - p['haze_k'] * haze) + (np.array(p['haze'], np.float32) / 255) * (p['haze_k'] * haze)
    F = _khoi(B, _f(ov), p, U)
    # 5. bảng màu toàn khung: tách tông (tối ngả lạnh, sáng ngả ấm), tương phản, độ bão hòa
    lum = (F[..., 0] * 0.299 + F[..., 1] * 0.587 + F[..., 2] * 0.114)[..., None]
    lo = np.array(p['split_lo'], np.float32) / 255
    hi = np.array(p['split_hi'], np.float32) / 255
    k = p['split_k']
    F = F + (lo - 0.5) * k * (1 - lum) * 0.9 + (hi - 0.5) * k * lum * 0.7
    F = (F - 0.5) * p['contrast'] + 0.5
    lum = (F[..., 0] * 0.299 + F[..., 1] * 0.587 + F[..., 2] * 0.114)[..., None]
    F = lum + (F - lum) * p['sat']
    F = F * (1 - p['vignette'] * vig) + (F * SHD * 1.4) * (p['vignette'] * vig)
    F = F * paper
    return Image.fromarray(np.clip(F * 255 + 0.5, 0, 255).astype(np.uint8), 'RGB')
