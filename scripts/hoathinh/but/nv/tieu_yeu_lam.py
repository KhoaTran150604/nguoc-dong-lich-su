"""Tiểu yêu LAM – biến thể đám đông của Tiểu yêu (nv/tieu_yeu.py): da xanh lam, tóc cam,
áo đỏ nâu, sừng ngắn hơn, mặt mặc định ngạc nhiên (lính ngơ ngác). Mọi thứ khác theo bản gốc."""
import copy

from nv.tieu_yeu import NV as _GOC

NV = copy.deepcopy(_GOC)
NV.update(ten='Tiểu yêu lam', ma='tieu-yeu-lam')
NV['mau'].update(da='#9CC3E6', tai_trong='#7AA3CC', toc='#C9662E', ao='#A8473B', gau='#863830',
                 dai='#4D5F94', no='#3D4C78', vien_huy='#4D5F94', tua='#4D5F94')
NV['sung_yeu'] = [dict(goc=(-0.36, -0.82), dinh=(-0.52, -1.20), day=0.22, cong=-0.04, gio=1),
                  dict(goc=(0.56, -0.72), dinh=(0.80, -1.06), day=0.18, cong=0.04, gio=1)]
NV['mat'].update(bieu_cam='ngac', mieng='o', mau_may='#5A2E18', mau_ma='#F0A8A0')
