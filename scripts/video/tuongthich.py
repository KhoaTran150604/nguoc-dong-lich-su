"""Cho bộ dựng chạy được trên máy KHÔNG có thư viện cairo / ffmpeg hệ thống (vd Mac không có Homebrew).

Import module này TRƯỚC mọi thứ dùng cairosvg/ffmpeg (dung.py đã làm sẵn):
  - cairosvg không nạp được  -> thay bằng bản giả dùng resvg-py   (pip install --user resvg-py)
  - không có lệnh ffmpeg     -> dùng ffmpeg đóng gói của imageio-ffmpeg (pip install --user imageio-ffmpeg)
Máy đã có cairo + ffmpeg thật thì module này không làm gì.
"""
import os
import re
import shutil
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))


def _ffmpeg():
    if shutil.which('ffmpeg'):
        return
    try:
        import imageio_ffmpeg
    except ImportError:
        return
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    bindir = os.path.join(os.path.expanduser('~'), '.cache', 'nguoc-dong-bin')
    os.makedirs(bindir, exist_ok=True)
    link = os.path.join(bindir, 'ffmpeg')
    if not os.path.exists(link):
        os.symlink(exe, link)
    os.environ['PATH'] = bindir + os.pathsep + os.environ.get('PATH', '')


# Tên font "đầy đủ" mà cairo/fontconfig hiểu, resvg cần tách thành họ + độ đậm
_FONT_FIX = [(r'font-family="Be Vietnam Pro (SemiBold|Medium|Bold)"',
              lambda m: 'font-family="Be Vietnam Pro" font-weight="%d"' % {'Medium': 500, 'SemiBold': 600, 'Bold': 700}[m.group(1)])]


def _cairosvg():
    try:
        import cairosvg  # noqa: F401
        return
    except (OSError, ImportError):
        for k in [k for k in sys.modules if k == 'cairosvg' or k.startswith('cairosvg.') or k.startswith('cairocffi')]:
            del sys.modules[k]
    import resvg_py
    font_dirs = [os.path.join(ROOT, 'fonts'), os.path.expanduser('~/Library/Fonts')]
    font_dirs = [d for d in font_dirs if os.path.isdir(d)]

    def svg2png(bytestring=None, write_to=None, **_):
        s = bytestring.decode('utf-8') if isinstance(bytestring, bytes) else bytestring
        for pat, rep in _FONT_FIX:
            s = re.sub(pat, rep, s)
        png = resvg_py.svg_to_bytes(svg_string=s, font_dirs=font_dirs)
        png = bytes(png)
        if write_to:
            with open(write_to, 'wb') as f:
                f.write(png)
            return None
        return png

    mod = types.ModuleType('cairosvg')
    mod.svg2png = svg2png
    mod.__file__ = __file__
    sys.modules['cairosvg'] = mod


_ffmpeg()
_cairosvg()
