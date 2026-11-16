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
    'ngo-quyen':   dict(bg=('#5A3A10', '#C9A24A'), hat='khan', beard='ria', robe='#6A4A1E', trim='#C9A24A', age='trung'),
    'hoang-thao':  dict(bg=('#4A1410', '#A8382A'), hat='mao',  beard='none', robe='#7A1E18', trim='#E0B060', age='tre'),
    'luu-cung':    dict(bg=('#3A0E0A', '#8E2A20'), hat='mien', beard='dai', robe='#5A1410', trim='#E8C060', age='gia'),
    'quan-ta':     dict(bg=('#5A3A10', '#C9A24A'), hat='non',  beard='none', robe='#5A4630', trim='#A88A50', age='tre'),
    'duong-dinh-nghe': dict(bg=('#5A3A10', '#C9A24A'), hat='khan', beard='dai', robe='#4E3A1E', trim='#C9A24A', age='gia'),
    'kieu-cong-tien':  dict(bg=('#2E2A26', '#6A5E50'), hat='khan', beard='ria', robe='#3A342E', trim='#8A7A60', age='trung'),
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
         # mắt, mày, mũi, miệng
         '<path d="M36,40 q3,-2 6,0" stroke="#1E120A" stroke-width="1.1" fill="none"/><path d="M48,40 q3,-2 6,0" stroke="#1E120A" stroke-width="1.1" fill="none"/>',
         '<path d="M35,36 l7,-1.5" stroke="#1E120A" stroke-width="1.6"/><path d="M55,36 l-7,-1.5" stroke="#1E120A" stroke-width="1.6"/>',
         '<path d="M45,42 l-1.6,7 l3,0" stroke="#8A5A3A" stroke-width="0.8" fill="none"/>',
         '<path d="M41,54 q4,1.5 8,0" stroke="#7A3A2A" stroke-width="1" fill="none"/>']
    if c['beard'] == 'ria':
        o.append('<path d="M38,52 q7,-3 14,0" stroke="#1E120A" stroke-width="1.6" fill="none"/><path d="M43,57 l2,6 l2,-6" fill="#1E120A"/>')
    if c['beard'] == 'dai':
        o.append('<path d="M37,51 q8,-3 16,0" stroke="#2A2A2A" stroke-width="1.6" fill="none"/><path d="M38,56 Q45,78 52,56 Q45,60 38,56 Z" fill="#2A2420"/>')
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
    elif hat == 'non':     # nón lính
        o.append('<path d="M24,32 L45,16 L66,32 Z" fill="#7A5A30" stroke="#1E120A" stroke-width="1"/><line x1="45" y1="16" x2="45" y2="12" stroke="#1E120A" stroke-width="1.2"/>')
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

_uri = {}
def data_uri(ma):
    if ma not in _uri:
        _uri[ma] = 'data:image/png;base64,' + base64.b64encode(open(path(ma), 'rb').read()).decode()
    return _uri[ma]
