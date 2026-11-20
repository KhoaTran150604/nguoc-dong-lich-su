"""Dựng THỬ một đoạn cảnh của tập (có giọng + âm hiệu ứng), để so phong cách mà không phải render cả tập.

    python3 scripts/video/thu_doan.py e2 docs/videos/E2-loi-doc.txt assets/e2/E2-GiaHuy s38-s45 [--final] [--anhsang[=chieu]]
-> build/<tập>/thu/<tập>-s38-s45-<goc|anhsang-ngay>.mp4
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dung as D  # noqa: E402


def main():
    import importlib, json
    import numpy as np
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    tap, loi, voice, rng = args[:4]
    sys.modules['dung'] = D
    D.EP = importlib.import_module('tap.' + tap)
    lo, hi = (int(x.strip('s')) for x in rng.split('-'))
    items = D.read_script(loi); meta = json.load(open(voice + '.json'))
    times, pauses, end = D.timeline(items, meta, getattr(D.EP, 'TAIL', 0.8))
    plan = [p for p in D.plan_scenes(items, times, pauses, end) if lo <= int(p[0][1:]) <= hi]
    t0, t1 = plan[0][1], plan[-1][2]
    as_name = D.ANH_SANG or getattr(D.EP, 'ANH_SANG', None)
    tag = f'anhsang-{as_name}' if as_name else 'goc'
    out_dir = os.path.join(D.ROOT, 'build', tap, 'thu', tag); os.makedirs(out_dir, exist_ok=True)
    jobs = [(c, a, b, os.path.join(out_dir, f'{c}-{D.W}p{D.FPS}.mp4')) for c, a, b in plan]
    todo = [j for j in jobs if not os.path.exists(j[3])]
    print(f'{len(plan)} cảnh {plan[0][0]}–{plan[-1][0]} · {t1-t0:.1f}s · {D.W}x{D.H} {D.FPS}fps · {tag} · render {len(todo)}', flush=True)
    import multiprocessing as mp, time
    st = time.time()
    with mp.get_context('fork').Pool(min(4, os.cpu_count())) as pool:
        for msg in pool.imap_unordered(D.render_scene, todo):
            print(' ', msg, f'({time.time()-st:.0f}s)', flush=True)
    lst = os.path.join(out_dir, 'list.txt'); open(lst, 'w').write(''.join(f"file '{j[3]}'\n" for j in jobs))
    hinh = os.path.join(out_dir, 'hinh.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', hinh], check=True)
    # âm thanh: trộn cả tập như dung.py rồi cắt đúng đoạn
    AT = D.AT
    v = AT.load_audio(voice + '.mp3'); segs, prev = [], 0
    for k, (pt, p, _) in enumerate(pauses):
        orig = pt - sum(pp for _, pp, _ in pauses[:k]); cut = int(orig * AT.SR)
        segs += [v[prev:cut], np.zeros(int(p * AT.SR))]; prev = cut
    segs.append(v[prev:]); vo = np.concatenate(segs)
    sfx = getattr(D.EP, 'SFX', lambda c, d: [])
    allplan = D.plan_scenes(items, times, pauses, end)
    events = [(a + t, nm, g, dd) for c, a, b in allplan for t, nm, g, dd in sfx(c, b - a) if t0 - 6 < a + t < t1]
    ok, bo = [], set()                     # máy thiếu scipy: bỏ âm hiệu ứng không tạo được, vẫn giữ giọng
    for ev in events:
        try: AT.get(ev[1], ev[3]); ok.append(ev)
        except ImportError: bo.add(ev[1])
    if bo: print('  (bỏ âm thiếu scipy:', ', '.join(sorted(bo)) + ')')
    events = ok
    mix = AT.mix(vo, events, end)[int(t0 * AT.SR):int(t1 * AT.SR)]
    wav = os.path.join(out_dir, 'tieng.wav'); AT.write_wav(mix, wav)
    name = os.path.join(D.ROOT, 'build', tap, 'thu', f'{tap}-{rng}-{tag}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', hinh, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', name], check=True)
    print('->', name, f'({time.time()-st:.0f}s)')


if __name__ == '__main__':
    main()
