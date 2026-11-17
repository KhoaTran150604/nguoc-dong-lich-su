"""ĐỒNG BỘ cloud ↔ máy nhà – chạy mỗi lần ngồi vào máy (không tốn token nếu tự chạy).

    python3 scripts/dong_bo.py            # pull main + dựng lại video đã duyệt mà máy chưa có
    python3 scripts/dong_bo.py --chi-xem  # chỉ báo cáo, không dựng

Nguyên tắc: git là nguồn sự thật cho code/kịch bản/giọng/CLAUDE.md; video KHÔNG đi qua git mà được
dựng lại từ code (kết quả giống bản trên cloud). Danh sách video cần có: docs/videos/thanh-pham.json.
"""
import hashlib, json, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
CHI_XEM = '--chi-xem' in sys.argv

def git(*a, check=True):
    r = subprocess.run(['git', *a], capture_output=True, text=True)
    if check and r.returncode: print('  git', ' '.join(a), '→', r.stderr.strip()); sys.exit(1)
    return r.stdout.strip()

def bar(i, n, t0, ten):
    u = i / max(1, n); w = int(u * 20); da = (time.time() - t0) / 60
    con = da / u - da if u else 0
    print(f'\rĐồng bộ {"█"*w}{"░"*(20-w)} {u*100:3.0f}%  ({i}/{n})  đã {da:.1f} phút · còn ~{con:.1f} phút  [{ten}]   ', end='', flush=True)

print('① Lấy bản mới nhất từ GitHub (nhánh main)…')
if git('status', '--porcelain'):
    print('  ⚠️  Máy đang có thay đổi chưa commit:'); print('  ' + git('status', '--short').replace('\n', '\n  '))
    print('  → Commit + push (hoặc bỏ) rồi chạy lại, để không đè mất việc.'); sys.exit(1)
git('fetch', '--quiet', 'origin')
if git('rev-parse', '--abbrev-ref', 'HEAD') != 'main': git('checkout', '--quiet', 'main')
git('pull', '--quiet', '--ff-only', 'origin', 'main')
print('  ✅ main @', git('log', '-1', '--format=%h %s'))
cho = [b.strip() for b in git('branch', '-r', '--no-merged', 'origin/main').split('\n') if b.strip().startswith('origin/claude/')]
if cho:
    print(f'  ⚠️  {len(cho)} nhánh cloud CHƯA gộp vào main (việc làm trên cloud chưa về máy):')
    for b in cho: print('     -', b, '·', git('log', '-1', '--format=%cr: %s', b))
    print('  → Mở PR của nhánh đó trên GitHub và bấm Merge, rồi chạy lại.')

print('② Kiểm tra video đã duyệt…')
ds = json.load(open('docs/videos/thanh-pham.json', encoding='utf-8'))
def dau_van(files):          # dấu vân của công thức dựng: đổi code/lời/giọng → dựng lại
    h = hashlib.sha1()
    for f in files:
        if os.path.exists(f): h.update(open(f, 'rb').read())
    return h.hexdigest()[:12]
can = []
for sp in ds.get('short', []):
    tap, n = sp['tap'], sp['phan']
    out = f'build/short/{tap}-p{n}/SHORT-{tap.upper()}-P{n}.mp4'; stamp = out + '.dauvan'
    dv = dau_van(['scripts/video/short.py', 'scripts/video/thumb.py', 'scripts/video/thumb_video.py', f'scripts/video/tap/{tap}.py'] + sp.get('phu_thuoc', []))
    ok = os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == dv
    print(f'  {"✅ có sẵn" if ok else "⏳ cần dựng"}  Short {tap.upper()} phần {n}  ({sp.get("ghi_chu", "")})')
    if not ok: can.append((tap, n, out, stamp, dv))
for v in ds.get('dai', []):
    print(f'  {"✅ có sẵn" if os.path.exists(v["file"]) else "❌ THIẾU"}  Video dài {v["tap"].upper()}: {v["file"]}')

if not can: print('\n✅ XONG – máy đã khớp với cloud, sẵn sàng đăng.'); sys.exit(0)
if CHI_XEM: print(f'\n(--chi-xem) Còn {len(can)} video cần dựng.'); sys.exit(0)
print(f'③ Dựng {len(can)} video (máy tự chạy, ~4 phút/Short)…')
t0 = time.time()
for i, (tap, n, out, stamp, dv) in enumerate(can):
    bar(i, len(can), t0, f'{tap.upper()} P{n}')
    r = subprocess.run([sys.executable, 'scripts/video/short.py', tap, str(n)], capture_output=True, text=True)
    if r.returncode: print(f'\n  ❌ Lỗi khi dựng {tap} P{n}:\n' + r.stderr[-1500:]); sys.exit(1)
    open(stamp, 'w').write(dv)
bar(len(can), len(can), t0, 'xong'); print()
print('\n✅ XONG – video nằm ở build/short/<tập>-p<n>/ . Sẵn sàng đăng bằng skill dang-youtube.')
