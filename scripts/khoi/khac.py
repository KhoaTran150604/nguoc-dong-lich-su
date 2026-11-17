"""Bộ lọc 'bản khắc cổ' – phong cách thumbnail đã chốt (15/11/2026).
Biến ảnh chân dung AI thành nét mực gạch chéo trên giấy dó, bớt vẻ 'ảnh AI'.
python3 scripts/khoi/khac.py <ảnh vào> <ảnh ra>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

def paper(w, h, base=(226, 206, 166), seed=3):
    rng = np.random.default_rng(seed)
    n = rng.random((h // 6 + 1, w // 6 + 1))
    t = Image.fromarray((n * 255).astype('uint8')).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    a = np.asarray(t) / 255.
    return Image.fromarray(np.clip(np.array(base)[None, None, :] + (a[..., None] - 0.5) * 40, 0, 255).astype('uint8'))

def woodcut(p, ink=(34, 22, 14)):
    g = ImageOps.autocontrast(p.convert('L')).filter(ImageFilter.SMOOTH_MORE)
    a = np.asarray(g) / 255.; h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]
    hatch = np.sin((xx + yy) * 0.55) * 0.5 + 0.5          # nét gạch chéo
    m = (a < 0.28) | ((a < 0.62) & (hatch > a * 1.35)) | (np.asarray(g.filter(ImageFilter.FIND_EDGES)) > 38)
    out = np.where(m[..., None], np.array(ink), np.asarray(paper(w, h)).astype(float))
    return Image.fromarray(out.astype('uint8'))

if __name__ == '__main__':
    woodcut(Image.open(sys.argv[1]).convert('RGB')).save(sys.argv[2]); print('OK', sys.argv[2])
