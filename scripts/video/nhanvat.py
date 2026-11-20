"""Chân dung nhân vật cho cờ (CHÂN DUNG MINH HỌA – không có chân dung thật thời này).

Ảnh nằm ở assets/nhanvat/<ma>.png (tỉ lệ ~ 9:10, mặt ở giữa). Nếu chưa có ảnh (chưa tạo bằng
Gemini/Flow) thì vẽ tạm chân dung vector style sơn mài và lưu vào assets/nhanvat/_vector/<ma>.png.
Ảnh thật luôn được ưu tiên, không bao giờ bị ghi đè.
"""
import base64, io, os
import cairosvg

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DIR = os.path.join(ROOT, 'assets', 'nhanvat')

# Mô tả vẽ tạm: màu nền, mũ, râu, áo, tuổi
NHANVAT = {
    'ngo-quyen':   dict(bg=('#5A3A10', '#C9A24A'), hat='tru',  beard='ria', robe='#6A4A1E', trim='#C9A24A', age='trung', face='dung', armor=True),
    'hoang-thao':  dict(bg=('#4A1410', '#A8382A'), hat='mao',  beard='ria', robe='#7A1E18', trim='#E0B060', age='tre', face='du', armor=True),
    'luu-cung':    dict(bg=('#3A0E0A', '#8E2A20'), hat='mien', beard='dai', robe='#5A1410', trim='#E8C060', age='gia', face='du'),
    'quan-ta':     dict(bg=('#5A3A10', '#C9A24A'), hat='non',  beard='none', robe='#5A4630', trim='#A88A50', age='tre', face='dung'),
    'duong-dinh-nghe': dict(bg=('#5A3A10', '#C9A24A'), hat='khan', beard='dai', robe='#4E3A1E', trim='#C9A24A', age='gia'),
    'khuc-thua-my':    dict(bg=('#5A3A10', '#C9A24A'), hat='khan', beard='ria', robe='#5A4630', trim='#C9A24A', age='trung', face='hien'),
    'tuong-nam-han':   dict(bg=('#4A1410', '#A8382A'), hat='tru',  beard='ria', robe='#7A1E18', trim='#E0B060', age='trung', face='du', armor=True),
    'tieu-ich':        dict(bg=('#4A1410', '#A8382A'), hat='mao',  beard='dai', robe='#5A1410', trim='#E8C060', age='gia', face='hien'),
    'su-gia':          dict(bg=('#2E2A26', '#6A5E50'), hat='khan', beard='none', robe='#3A342E', trim='#8A7A60', age='tre', face='hien'),
    'tran-hung-dao':   dict(bg=('#3A2A10', '#B8923A'), hat='khoi', beard='dai', robe='#2E3A4E', trim='#C9A24A', age='gia', face='dung', armor=True, armor_col='#3A4A5E'),
    'kieu-cong-tien':  dict(bg=('#2E2A26', '#6A5E50'), hat='khan', beard='ria', robe='#3A342E', trim='#8A7A60', age='trung', face='du'),
}

def _vector_svg(c, w=270, h=300):
    b0, b1 = c['bg']; skin = '#E2B98C' if c['age'] != 'gia' else '#D8AE82'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 90 100">',
         f'<defs><radialGradient id="g" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="{b1}"/><stop offset="1" stop-color="{b0}"/></radialGradient></defs>',
         '<rect width="90" height="100" fill="url(#g)"/>',
         # vân sơn mài: vòng tròn đồng mờ
         f'<circle cx="45" cy="40" r="34" fill="none" stroke="#F3D27A" stroke-width="0.6" opacity="0.35"/>',
         # áo
         f'<path d="M8,100 Q12,74 30,68 L45,76 L60,68 Q78,74 82,100 Z" fill="{c["robe"]}" stroke="#1E120A" stroke-width="1"/>',
         f'<path d="M30,68 L45,90 L60,68" fill="none" stroke="{c["trim"]}" stroke-width="2.4"/>',
         # cổ + mặt
         f'<rect x="39" y="56" width="12" height="14" fill="{skin}"/>',
         f'<ellipse cx="45" cy="44" rx="15" ry="18" fill="{skin}" stroke="#5A3A20" stroke-width="0.8"/>',
         f'<ellipse cx="30" cy="45" rx="2.4" ry="4" fill="{skin}"/><ellipse cx="60" cy="45" rx="2.4" ry="4" fill="{skin}"/>',
         '<path d="M45,42 l-1.6,7 l3,0" stroke="#8A5A3A" stroke-width="0.8" fill="none"/>']
    face = c.get('face', 'hien')
    if face == 'hien':
        o += ['<path d="M36,40 q3,-2 6,0" stroke="#1E120A" stroke-width="1.1" fill="none"/><path d="M48,40 q3,-2 6,0" stroke="#1E120A" stroke-width="1.1" fill="none"/>',
              '<path d="M35,36 l7,-1.5" stroke="#1E120A" stroke-width="1.6"/><path d="M55,36 l-7,-1.5" stroke="#1E120A" stroke-width="1.6"/>',
              '<path d="M41,54 q4,1.5 8,0" stroke="#7A3A2A" stroke-width="1" fill="none"/>']
    else:
        fierce = face == 'du'
        # mắt: lòng trắng + con ngươi, mí trên kẻ đậm và xếch
        for ex, sgn in ((39, -1), (51, 1)):
            o.append(f'<path d="M{ex-4},41 Q{ex},{38.6 if fierce else 38.2} {ex+4},41 Q{ex},42.6 {ex-4},41 Z" fill="#F2E6CC" stroke="#1E120A" stroke-width="0.9"/>')
            o.append(f'<circle cx="{ex + (0.6 if fierce else 0)*sgn*-1:.1f}" cy="40.9" r="1.3" fill="#1E120A"/>')
            o.append(f'<path d="M{ex-4.4},{40.6 if fierce else 40.2} L{ex+4.4},{39.4 if sgn>0 else 41.6}" stroke="#1E120A" stroke-width="1.1" transform="scale(1 1)"/>' if False else '')
        if fierce:   # nghiêm, lạnh: mày hơi chau, miệng hơi trễ – không quá dữ
            o += ['<path d="M34,35.6 Q38.5,36 43,38.2 L42.8,39.2 Q38.5,37.4 34,37.2 Z" fill="#1E120A"/><path d="M56,35.6 Q51.5,36 47,38.2 L47.2,39.2 Q51.5,37.4 56,37.2 Z" fill="#1E120A"/>',
                  '<path d="M41,55 q4,-1.2 8,0" stroke="#5A1A12" stroke-width="1.1" fill="none"/>']
        else:        # điềm tĩnh, tự tin: mày rậm vừa, hơi xếch; miệng thẳng, khoé hơi nhếch
            o += ['<path d="M34,36.6 Q38.5,35.6 43,37 L43,38.2 Q38.5,37 34,38 Z" fill="#1E120A"/><path d="M56,36.6 Q51.5,35.6 47,37 L47,38.2 Q51.5,37 56,38 Z" fill="#1E120A"/>',
                  '<path d="M41,54.2 q4,0.9 8,0" stroke="#5A1A12" stroke-width="1.1" fill="none"/>']
    if c['beard'] == 'ria':
        o.append('<path d="M38,52 q7,-3 14,0" stroke="#1E120A" stroke-width="1.6" fill="none"/><path d="M43,57 l2,6 l2,-6" fill="#1E120A"/>')
    if c['beard'] == 'dai':
        bc = '#6A6460' if c['age'] == 'gia' else '#2A2420'
        o.append(f'<path d="M37,51 q8,-3 16,0" stroke="{bc}" stroke-width="1.6" fill="none"/><path d="M38,56 Q45,78 52,56 Q45,60 38,56 Z" fill="{bc}"/>')
    if c['age'] == 'gia':
        o.append('<path d="M37,32 q8,-1 16,0" stroke="#8A5A3A" stroke-width="0.5" fill="none"/>')
    hat = c['hat']
    if hat == 'khan':      # khăn vấn / khăn chít
        o.append(f'<path d="M29,38 Q30,18 45,17 Q60,18 61,38 Q56,28 45,28 Q34,28 29,38 Z" fill="#2A1A10"/><path d="M31,30 Q45,22 59,30" stroke="{c["trim"]}" stroke-width="1.2" fill="none"/>')
    elif hat == 'mao':     # mũ quan có cánh (minh họa)
        o.append(f'<path d="M30,34 Q31,16 45,14 Q59,16 60,34 Z" fill="#1E120A"/><rect x="18" y="27" width="12" height="3" fill="#1E120A"/><rect x="60" y="27" width="12" height="3" fill="#1E120A"/><circle cx="45" cy="20" r="2" fill="{c["trim"]}"/>')
    elif hat == 'mien':    # mũ vua có tua (minh họa)
        o.append(f'<path d="M30,33 Q31,18 45,16 Q59,18 60,33 Z" fill="#1E120A"/><rect x="26" y="12" width="38" height="4" fill="{c["trim"]}" stroke="#1E120A" stroke-width="0.6"/>')
        o.append(''.join(f'<line x1="{x}" y1="16" x2="{x}" y2="25" stroke="{c["trim"]}" stroke-width="0.8"/>' for x in (30, 35, 55, 60)))
    elif hat == 'tru':     # mũ trụ của tướng: chóp nhọn, chùm tua đỏ, vành che tai (minh họa)
        o.append(f'<path d="M27,40 Q27,16 45,13 Q63,16 63,40 L58,40 Q57,25 45,24 Q33,25 32,40 Z" fill="#8A6A2A" stroke="#1E120A" stroke-width="1"/>')
        o.append(f'<path d="M30,26 Q45,18 60,26" stroke="{c["trim"]}" stroke-width="1.6" fill="none"/><path d="M33,32 Q45,26 57,32" stroke="#F3D27A" stroke-width="0.8" fill="none"/>')
        o.append(f'<path d="M42,14 L45,4 L48,14 Z" fill="{c["trim"]}" stroke="#1E120A" stroke-width="0.6"/><path d="M45,6 Q39,0 37,6 Q41,3 45,8 Q49,3 53,6 Q51,0 45,6 Z" fill="#B3261E"/>')
        o.append('<circle cx="45" cy="21" r="2.2" fill="#B3261E" stroke="#F3D27A" stroke-width="0.6"/>')
        o.append(f'<path d="M27,40 L25,52 L31,50 L32,40 Z M63,40 L65,52 L59,50 L58,40 Z" fill="#7A5A24" stroke="#1E120A" stroke-width="0.8"/>')
    elif hat == 'khoi':    # mũ khôi tròn có cánh phượng hai bên (minh họa), khác mũ trụ của Ngô Quyền
        o.append(f'<path d="M28,38 Q28,17 45,15 Q62,17 62,38 Q56,30 45,30 Q34,30 28,38 Z" fill="#3A3A40" stroke="#1E120A" stroke-width="1"/>')
        o.append(f'<path d="M31,31 Q45,23 59,31" stroke="{c["trim"]}" stroke-width="1.8" fill="none"/>')
        o.append(f'<path d="M29,30 Q18,22 16,12 Q24,18 30,24 Z M61,30 Q72,22 74,12 Q66,18 60,24 Z" fill="{c["trim"]}" stroke="#1E120A" stroke-width="0.7"/>')
        o.append(f'<rect x="42" y="9" width="6" height="7" rx="1" fill="{c["trim"]}" stroke="#1E120A" stroke-width="0.6"/><circle cx="45" cy="22" r="2.4" fill="#F3D27A" stroke="#1E120A" stroke-width="0.5"/>')
    elif hat == 'non':     # nón lính
        o.append('<path d="M24,32 L45,16 L66,32 Z" fill="#7A5A30" stroke="#1E120A" stroke-width="1"/><line x1="45" y1="16" x2="45" y2="12" stroke="#1E120A" stroke-width="1.2"/>')
    if c.get('armor'):     # giáp vai + giáp ngực vảy
        o.append(f'<path d="M10,100 Q10,78 26,70 Q33,74 34,82 Q22,84 16,100 Z M80,100 Q80,78 64,70 Q57,74 56,82 Q68,84 74,100 Z" fill="{c.get("armor_col", "#7A5A24")}" stroke="#1E120A" stroke-width="0.9"/>')
        o.append(''.join(f'<path d="M{x},{y} q3,3 6,0" stroke="#F3D27A" stroke-width="0.6" fill="none"/>' for y in (86, 91, 96) for x in range(34, 56, 6)))
    o.append('</svg>')
    return ''.join(o)

def path(ma):
    """Đường dẫn ảnh chân dung: ưu tiên ảnh thật, không có thì vẽ vector tạm."""
    real = os.path.join(DIR, f'{ma}.png')
    if os.path.exists(real): return real
    vec = os.path.join(DIR, '_vector', f'{ma}.png')
    if not os.path.exists(vec):
        os.makedirs(os.path.dirname(vec), exist_ok=True)
        cairosvg.svg2png(bytestring=_vector_svg(NHANVAT[ma]).encode(), write_to=vec)
    return vec

TEN = {'ngo-quyen': 'NGÔ QUYỀN', 'hoang-thao': 'HOẰNG THÁO', 'luu-cung': 'LƯU CUNG', 'quan-ta': 'QUÂN TA',
       'duong-dinh-nghe': 'DƯƠNG ĐÌNH NGHỆ', 'kieu-cong-tien': 'KIỀU CÔNG TIỄN', 'khuc-thua-my': 'KHÚC THỪA MỸ',
       'tuong-nam-han': 'TƯỚNG NAM HÁN', 'tieu-ich': 'TIÊU ÍCH', 'su-gia': 'SỨ GIẢ', 'tran-hung-dao': 'TRẦN HƯNG ĐẠO'}
for _k, _v in TEN.items():
    if _k in NHANVAT: NHANVAT[_k].setdefault('ten', _v)

_uri = {}
def data_uri(ma):
    if ma not in _uri:
        _uri[ma] = 'data:image/png;base64,' + base64.b64encode(open(path(ma), 'rb').read()).decode()
    return _uri[ma]
