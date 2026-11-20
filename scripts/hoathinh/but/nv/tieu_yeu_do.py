"""Tiểu yêu ĐỎ – biến thể đám đông của Tiểu yêu (nv/tieu_yeu.py): da cam đỏ, MỘT sừng giữa trán,
tóc đen, áo nâu đất, mặt mặc định quyết (lính hăng). Mọi thứ khác theo bản gốc."""
import copy

from nv.tieu_yeu import NV as _GOC

NV = copy.deepcopy(_GOC)
NV.update(ten='Tiểu yêu đỏ', ma='tieu-yeu-do')
NV['mau'].update(da='#E8806A', tai_trong='#C9634E', toc='#2B2530', ao='#8A6242', gau='#6E4C33',
                 dai='#E2B13C', no='#B5822A', vien_huy='#E2B13C', tua='#E2B13C')
NV['sung_yeu'] = [dict(goc=(0.16, -0.84), dinh=(0.22, -1.42), day=0.26, cong=0.04, gio=2)]
NV['toc']['gai'] = [(-162, 0.12, 12, -6), (-136, 0.20, 12, -4), (-112, 0.16, 12, 0), (-50, 0.18, 12, 8),
                    (-26, 0.12, 11, 10)]
NV['mat'].update(bieu_cam='quyet', mieng='mim', mau_may='#3A2420', mau_ma='#E98A80')
