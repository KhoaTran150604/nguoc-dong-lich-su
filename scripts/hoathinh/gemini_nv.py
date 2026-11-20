"""Gemini cho nhân vật chibi: VẼ MẪU → MÔ TẢ CHI TIẾT → CHẤM ĐIỂM bản vẽ code.

Quy trình (người dùng chốt 20/11/2026):
  1. mau   : Gemini vẽ ảnh mẫu từ prompt  → mau.png
             rồi Gemini mô tả chi tiết (vũ khí, màu HEX, trang phục, tóc/mũ, tỉ lệ) → spec.json
  2. (Claude vẽ lại bằng code theo mau.png + spec.json – scripts/hoathinh/chibi/<nv>.py)
  3. cham  : gửi ảnh mẫu + ảnh code cho Gemini chấm /100 → cham-<n>.json
             ≥ 80 là ĐẠT, chưa đạt thì sửa code theo góp ý rồi chấm lại.

Key: biến môi trường GEMINI_API_KEY (hoặc GOOGLE_API_KEY), hoặc dòng GEMINI_API_KEY=... trong file .env
ở gốc dự án (.env đã nằm trong .gitignore – không commit).

Chạy:
  python scripts/hoathinh/gemini_nv.py models
  python scripts/hoathinh/gemini_nv.py mau bat-gioi --prompt docs/nhan-vat/prompt/bat-gioi.txt
  python scripts/hoathinh/gemini_nv.py mota bat-gioi            # chỉ làm lại spec.json từ mau.png
  python scripts/hoathinh/gemini_nv.py cham bat-gioi build/thu-hoathinh/nhan-vat/bat-gioi.png
Ra: assets/nhan-vat/gemini/<nv>/
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets', 'nhan-vat', 'gemini')
API = 'https://generativelanguage.googleapis.com/v1beta'
MODEL_ANH = os.environ.get('GEMINI_MODEL_ANH', 'gemini-3.1-flash-image')
MODEL_CHU = os.environ.get('GEMINI_MODEL_CHU', 'gemini-3.5-flash')
NGUONG = 80


def lay_key():
    for k in ('GEMINI_API_KEY', 'GOOGLE_API_KEY'):
        if os.environ.get(k):
            return os.environ[k].strip()
    env = os.path.join(ROOT, '.env')
    if os.path.exists(env):
        for line in open(env, encoding='utf-8'):
            m = re.match(r'\s*(GEMINI_API_KEY|GOOGLE_API_KEY)\s*=\s*["\']?([^"\'\s]+)', line)
            if m:
                return m.group(2)
    # file key riêng của người dùng (ngoài repo): G:\My Drive\env\api_key.txt – lấy chuỗi key trong file
    for f in (os.environ.get('GEMINI_KEY_FILE', ''), r'G:\My Drive\env\api_key.txt',
              os.path.join(os.path.dirname(os.path.dirname(ROOT)), 'env', 'api_key.txt')):
        if f and os.path.exists(f):
            m = re.search(r'(AIza[0-9A-Za-z_-]{20,}|AQ\.[0-9A-Za-z_.-]{20,})', open(f, encoding='utf-8-sig').read())
            if m:
                return m.group(1)
    sys.exit('Chưa có key: đặt GEMINI_API_KEY trong biến môi trường hoặc file .env ở gốc dự án.')


def goi(model, parts, json_out=False, thu=3):
    body = {'contents': [{'role': 'user', 'parts': parts}]}
    if json_out:
        body['generationConfig'] = {'responseMimeType': 'application/json', 'temperature': 0.2}
    req = urllib.request.Request(f'{API}/models/{model}:generateContent',
                                 data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': lay_key()})
    for i in range(thu):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:600]
            if e.code in (429, 500, 503) and i < thu - 1:
                print(f'  Gemini {e.code}, thử lại sau {10 * (i + 1)}s…')
                time.sleep(10 * (i + 1))
                continue
            sys.exit(f'Gemini lỗi {e.code}: {msg}')


def anh_part(path):
    mime = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'
    return {'inline_data': {'mime_type': mime, 'data': base64.b64encode(open(path, 'rb').read()).decode()}}


def chu(resp):
    return ''.join(p.get('text', '') for c in resp.get('candidates', []) for p in c['content'].get('parts', []))


def doc_json(resp):
    t = chu(resp).strip()
    t = re.sub(r'^```(json)?|```$', '', t, flags=re.M).strip()
    return json.loads(t)


MOTA = """You are a character-design analyst. Describe the attached chibi mascot image so a programmer can
redraw it EXACTLY with code (flat vector shapes). Return JSON only, with these keys:
{
 "proportions": {"head_width_vs_body_width": float, "head_height_vs_total_height": float,
                  "head_shape": str, "body_shape": str, "view_angle": str, "notes": str},
 "outline": {"color_hex": str, "thickness_vs_head_width": float},
 "background_hex": str,
 "face": {"skin_hex": str, "skin_shadow_hex": str, "eyes": str, "brows": str, "cheeks_hex": str,
          "snout_or_nose": str, "snout_hex": str, "nostrils_hex": str, "mouth": str, "ears": str},
 "hair_and_headwear": {"description": str, "colors_hex": [str], "emblem": str, "band": str},
 "outfit": [{"part": str, "description": str, "color_hex": str}],
 "weapon": {"name": str, "parts": [{"part": str, "shape": str, "color_hex": str}],
            "length_vs_character_height": float, "angle_deg_from_vertical": float,
            "position": str, "held_how": str},
 "hands_and_limbs": str,
 "distinctive_details": [str],
 "positions_percent": {"head_center": [x, y], "body_center": [x, y], "hand": [x, y],
                       "weapon_top": [x, y], "weapon_bottom": [x, y]}
}
Colors as exact hex sampled from the image. Positions are % of image width/height."""

CHAM = """You are a strict art director judging a CODE-DRAWN redraw (image 2) against the REFERENCE mascot
(image 1). IMPORTANT: image 2 intentionally uses the channel's STANDARD CHIBI FRAME shared by all characters
(head size, head/body ratio, body block shape, body offset, floating-hand position, outline thickness, canvas
size). Do NOT penalize those. The reference is used ONLY for colors and character details. Judge: face &
expression, colors, outfit, headwear/hair, weapon, and overall cuteness/appeal. Ignore tiny pixel
differences; be strict on any detail a viewer would notice as missing or wrong. Spec of the reference (for colors/details): {spec}

Return JSON only:
{
 "score": int 0-100,
 "breakdown": {"face_expression": int /25, "colors": int /20, "outfit": int /20,
               "headwear_hair": int /15, "weapon": int /15, "appeal": int /5},
 "matches": [str],
 "fixes": [{"priority": int 1-3, "area": str, "problem": str, "how_to_fix": str}],
 "verdict": "PASS if score>=80 else FAIL"
}
Write "problem" and "how_to_fix" in Vietnamese, concrete enough for a programmer (sizes relative to head
width, positions, hex colors)."""


def lenh_models(_):
    req = urllib.request.Request(f'{API}/models?pageSize=200', headers={'x-goog-api-key': lay_key()})
    with urllib.request.urlopen(req, timeout=60) as r:
        for m in json.load(r)['models']:
            print(m['name'], '|', ','.join(m.get('supportedGenerationMethods', [])))


def lenh_mota(a):
    d = os.path.join(OUT, a.nv)
    mau = os.path.join(d, 'mau.png')
    print(f'Gemini ({MODEL_CHU}) mô tả chi tiết…')
    spec = doc_json(goi(MODEL_CHU, [anh_part(mau), {'text': MOTA}], json_out=True))
    json.dump(spec, open(os.path.join(d, 'spec.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('→', os.path.join(d, 'spec.json'))


def lenh_mau(a):
    d = os.path.join(OUT, a.nv)
    os.makedirs(d, exist_ok=True)
    prompt = open(a.prompt, encoding='utf-8').read()
    print(f'Gemini ({MODEL_ANH}) vẽ mẫu…')
    resp = goi(MODEL_ANH, [{'text': prompt}])
    n = 0
    for c in resp.get('candidates', []):
        for p in c['content'].get('parts', []):
            data = p.get('inline_data') or p.get('inlineData')
            if data:
                n += 1
                ten = 'mau.png' if n == 1 else f'mau-{n}.png'
                open(os.path.join(d, ten), 'wb').write(base64.b64decode(data['data']))
                print('→', os.path.join(d, ten))
    if not n:
        sys.exit('Gemini không trả ảnh: ' + json.dumps(resp)[:800])
    lenh_mota(a)


def lenh_cham(a):
    d = os.path.join(OUT, a.nv)
    spec = open(os.path.join(d, 'spec.json'), encoding='utf-8').read()
    print(f'Gemini ({MODEL_CHU}) chấm {a.n} lần, lấy trung bình…')
    ds = []
    for _ in range(a.n):
        ds.append(doc_json(goi(MODEL_CHU, [{'text': 'Image 1 = REFERENCE:'}, anh_part(os.path.join(d, 'mau.png')),
                                           {'text': 'Image 2 = CODE-DRAWN redraw:'}, anh_part(a.anh),
                                           {'text': CHAM.replace('{spec}', spec)}], json_out=True)))
    kq = dict(ds[-1])
    kq['cac_lan'] = [x['score'] for x in ds]
    kq['score'] = round(sum(kq['cac_lan']) / len(ds))
    kq['fixes'] = [f for x in ds for f in x.get('fixes', [])]
    print('  điểm từng lần:', kq['cac_lan'])
    lan = len([f for f in os.listdir(d) if f.startswith('cham-')]) + 1
    kq['anh'] = os.path.relpath(a.anh, ROOT)
    json.dump(kq, open(os.path.join(d, f'cham-{lan}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"Lần {lan}: {kq['score']}/100 → {'ĐẠT' if kq['score'] >= NGUONG else 'CHƯA ĐẠT'}")
    print(json.dumps(kq.get('breakdown'), ensure_ascii=False))
    for f in sorted(kq.get('fixes', []), key=lambda x: x.get('priority', 9)):
        print(f"  [{f.get('priority')}] {f.get('area')}: {f.get('problem')} → {f.get('how_to_fix')}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='lenh', required=True)
    sp.add_parser('models')
    p = sp.add_parser('mau'); p.add_argument('nv'); p.add_argument('--prompt', required=True)
    p = sp.add_parser('mota'); p.add_argument('nv')
    p = sp.add_parser('cham'); p.add_argument('nv'); p.add_argument('anh'); p.add_argument('-n', type=int, default=3)
    a = ap.parse_args()
    {'models': lenh_models, 'mau': lenh_mau, 'mota': lenh_mota, 'cham': lenh_cham}[a.lenh](a)
