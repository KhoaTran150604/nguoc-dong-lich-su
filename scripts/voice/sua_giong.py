"""Sửa giọng đọc TẠI CHỖ, không tạo lại cả bài: bỏ câu, hoặc thay câu bằng bản đọc mới.

    python3 scripts/voice/sua_giong.py <giọng_cũ> <giọng_mới> [--bo 10,57] [--thay 102=<giọng_1_câu>]
<giọng_*> là đường dẫn KHÔNG đuôi tới cặp .mp3 + .json do tts.py tạo. Số câu tính từ 1 như trong .json.
Ví dụ thay câu 102 bằng một câu vừa đọc riêng:
    python3 scripts/voice/tts.py cau.txt -o build/cau --check
    python3 scripts/voice/sua_giong.py assets/e2/E2-GiaHuy assets/e2/E2-GiaHuy-v2 --bo 10 --thay 102=build/cau
Nhớ sửa file lời đọc (.txt) cho khớp: số câu trong .json mới phải bằng số câu trong .txt.
"""
import argparse, json, subprocess
import numpy as np

SR = 44100
def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def main():
    p = argparse.ArgumentParser(); p.add_argument('cu'); p.add_argument('moi')
    p.add_argument('--bo', default=''); p.add_argument('--thay', action='append', default=[])
    a = p.parse_args()
    meta = json.load(open(a.cu + '.json')); v = load(a.cu + '.mp3'); L = meta['lines']
    bo = {int(x) for x in a.bo.split(',') if x}
    thay = {}
    for t in a.thay:
        i, base = t.split('='); m2 = json.load(open(base + '.json')); x = m2['lines'][0]; au = load(base + '.mp3')
        thay[int(i)] = (au[int(x['start'] * SR): int(x['end'] * SR)], x['text'])
    pieces = [v[: int(L[0]['start'] * SR)]]; t = L[0]['start']; out = []
    for k, ln in enumerate(L):
        i = ln['i']; s0, e0 = int(ln['start'] * SR), int(ln['end'] * SR)
        nxt = int(L[k + 1]['start'] * SR) if k + 1 < len(L) else len(v)
        if i in bo: continue
        body, text = (thay[i] if i in thay else (v[s0:e0], ln['text']))
        gap = v[e0:nxt]
        out.append({**{kk: vv for kk, vv in ln.items() if kk not in ('score', 'heard')}, 'i': len(out) + 1, 'text': text,
                    'start': round(t, 3), 'end': round(t + len(body) / SR, 3)})
        pieces += [body, gap]; t += (len(body) + len(gap)) / SR
    y = np.concatenate(pieces).astype(np.float32)
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '192k', a.moi + '.mp3'], stdin=subprocess.PIPE)
    pr.stdin.write(y.tobytes()); pr.stdin.close(); pr.wait()
    meta2 = {**meta, 'duration': round(len(y) / SR, 3), 'lines': out, 'sua_tu': a.cu, 'bo': sorted(bo), 'thay': sorted(thay)}
    json.dump(meta2, open(a.moi + '.json', 'w'), ensure_ascii=False, indent=1)
    print(f'Xong: {a.moi}.mp3 ({len(y)/SR:.1f}s, {len(out)} câu; bỏ {sorted(bo)}, thay {sorted(thay)})')

if __name__ == '__main__':
    main()
