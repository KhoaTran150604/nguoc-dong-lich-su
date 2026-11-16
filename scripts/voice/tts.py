"""Tạo giọng đọc cho video bằng ZeroTTS (chạy local, miễn phí, không giới hạn).

Đầu vào: file .txt, MỖI DÒNG = MỘT CÂU PHỤ ĐỀ. Dòng trống = hết đoạn (nghỉ dài hơn).
Đầu ra:  <out>.mp3 (giọng đọc) + <out>.json (mốc thời gian từng câu → dùng cho phụ đề/cảnh).

Ví dụ:
  python scripts/voice/tts.py docs/shorts/01-loi-doc.txt -o assets/short1/voice-HuuDuc
  python scripts/voice/tts.py loi.txt -o out --voice huuduc --cfg 2 --speed 0.95 --seed 7

Giọng mặc định "huuduc" (Hữu Đức: nam, lớn tuổi, kể chuyện, trầm, điềm đạm) – gần
"Anh Khôi nâng cao" của Vbee nhất trong 8 giọng có sẵn.
Cài: pip install zerotts ; nếu tải weights lỗi "CAS/xet" thì đặt HF_HUB_DISABLE_XET=1.
"""
import argparse, json, os, re, subprocess, sys, tempfile

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # proxy chặn backend Xet của HuggingFace
import numpy as np


def trim(a, sr, thr_db=-45, pad=0.04):
    """Cắt khoảng lặng đầu/cuối, chừa lại `pad` giây cho tự nhiên."""
    if a.size == 0:
        return a
    thr = 10 ** (thr_db / 20) * max(np.abs(a).max(), 1e-9)
    win = int(sr * 0.01)
    env = np.convolve(np.abs(a), np.ones(win) / win, mode="same")
    idx = np.where(env > thr)[0]
    if idx.size == 0:
        return a
    s = max(idx[0] - int(pad * sr), 0)
    e = min(idx[-1] + int(pad * sr), a.size)
    return a[s:e]


def fold_bac(w):
    """Giọng Bắc đọc tr=ch, d=gi=r, s=x → không tính là lỗi khi so chữ."""
    w = re.sub(r"^tr", "ch", w)
    w = re.sub(r"^(gi|r)", "d", w)
    return re.sub(r"^s", "x", w)


def syllables(text, normalize):
    t = normalize(text).lower()
    return [fold_bac(w) for w in re.sub(r"[^\w\s]", " ", t).split()]


def make_checker(normalize):
    """Whisper nghe lại từng câu → điểm giống (0–1) so với chữ gốc, theo âm tiết có dấu."""
    from difflib import SequenceMatcher
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    asr = WhisperModel("medium", device="cpu", compute_type="int8")

    def check(audio, sr, expected):
        pad = np.zeros(8000, np.float32)  # đệm 0,5s: Whisper nghe câu cụt đầu rất kém
        a16 = np.concatenate([pad, resample_poly(audio, 16000, sr).astype(np.float32), pad])
        heard = " ".join(s.text for s in asr.transcribe(a16, language="vi", beam_size=5)[0])
        exp, got = syllables(expected, normalize), syllables(heard, normalize)
        return SequenceMatcher(None, exp, got).ratio(), heard.strip()
    return check


def read_lines(path):
    """Trả về list (câu, hết_đoạn?)."""
    raw = open(path, encoding="utf-8").read().splitlines()
    items = []
    for i, line in enumerate(raw):
        t = line.strip()
        if not t or t.startswith("#"):
            if items:
                items[-1] = (items[-1][0], True)
            continue
        items.append((t, False))
    return items


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("text", help="file .txt, mỗi dòng một câu")
    p.add_argument("-o", "--out", required=True, help="đường dẫn đầu ra, không đuôi")
    p.add_argument("--voice", default="huuduc")
    p.add_argument("--cfg", type=float, default=2.0, help="1.0–3.0; cao = bám giọng chặt hơn (chậm gấp đôi)")
    p.add_argument("--speed", type=float, default=1.0, help="<1 chậm lại (vd 0.93), giữ cao độ")
    p.add_argument("--gap", type=float, default=0.25, help="nghỉ giữa các câu trong một đoạn (giây)")
    p.add_argument("--para-gap", type=float, default=0.6, help="nghỉ giữa các đoạn (giây)")
    p.add_argument("--lead", type=float, default=0.3, help="lặng ở đầu file (giây)")
    p.add_argument("--seed", type=int, default=7, help="cùng seed + cùng câu = cùng kết quả")
    p.add_argument("--retake", default="", help="đọc lại các câu số (1-based), vd '3,5' – đổi seed riêng câu đó")
    p.add_argument("--check", action="store_true",
                   help="Whisper nghe lại từng câu, sai thì tự đọc lại (cần: pip install faster-whisper)")
    p.add_argument("--tries", type=int, default=4, help="số lần đọc tối đa mỗi câu khi --check")
    p.add_argument("--pass-score", type=float, default=0.95, help="ngưỡng đạt khi --check")
    p.add_argument("--model", default="zeroweight-ai/ZeroTTS")
    a = p.parse_args()

    from zerotts import ZeroTTS, normalize_vi_text
    from zerotts.chunking import normalize_punctuation, clean_segment_punctuation

    items = read_lines(a.text)
    if not items:
        sys.exit("File không có câu nào.")
    retake = {int(x) for x in a.retake.split(",") if x.strip()}

    tts = ZeroTTS.from_pretrained(a.model)
    sr = tts.sample_rate
    check = make_checker(normalize_vi_text) if a.check else None
    report = []
    pieces, timeline, t = [np.zeros(int(a.lead * sr), np.float32)], [], a.lead

    for i, (line, end_para) in enumerate(items, 1):
        # "…" → "," để model ngắt nhẹ; chuẩn hoá số/ngày thành chữ ("938" → "chín trăm ba mươi tám")
        spoken = clean_segment_punctuation(normalize_punctuation(normalize_vi_text(line.replace("…", ","))))
        spoken = re.sub(r"^[,\s]+", "", spoken)
        best = None
        for k in range(a.tries if check else 1):
            np.random.seed(a.seed + i + 100 * k + (1000 if i in retake else 0))
            audio = tts.synthesize(spoken, voice=a.voice, cfg_scale=a.cfg).reshape(-1).astype(np.float32)
            audio = trim(audio, sr)
            score, heard = check(audio, sr, line) if check else (1.0, "")
            if best is None or score > best[0]:
                best = (score, heard, audio, k + 1)
            if score >= a.pass_score:
                break
        score, heard, audio, ntry = best
        if check:
            flag = "OK " if score >= a.pass_score else "XEM"
            print(f"      {flag} {score:.2f} (lần {ntry}) nghe: {heard}", flush=True)
            report.append({"i": i, "score": round(score, 3), "heard": heard, "tries": ntry})
        dur = audio.size / sr / a.speed
        timeline.append({"i": i, "text": line, "start": round(t, 3), "end": round(t + dur, 3),
                         **({"score": round(score, 3), "heard": heard} if check else {})})
        gap = a.para_gap if end_para else a.gap
        pieces += [audio, np.zeros(int(gap * sr * a.speed), np.float32)]
        t += dur + gap
        print(f"[{i}/{len(items)}] {dur:5.2f}s  {line}", flush=True)

    wav = np.concatenate(pieces)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.wav")
        tts.save_audio(wav, raw)
        af = (f"atempo={a.speed}," if a.speed != 1.0 else "") + "loudnorm=I=-16:TP=-1.5:LRA=11"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af,
                        "-ar", "44100", "-ac", "1", "-b:a", "192k", a.out + ".mp3"], check=True)

    meta = {"voice": a.voice, "cfg": a.cfg, "speed": a.speed, "seed": a.seed,
            "duration": round(t, 3), "lines": timeline}
    json.dump(meta, open(a.out + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Xong: {a.out}.mp3 ({t:.1f}s) + {a.out}.json")
    bad = [r for r in report if r["score"] < a.pass_score]
    if bad:
        print("Cần nghe lại các câu:", ", ".join(str(r["i"]) for r in bad),
              "→ thử --retake hoặc đổi --seed (Whisper cũng có thể nghe nhầm tên riêng).")


if __name__ == "__main__":
    main()
