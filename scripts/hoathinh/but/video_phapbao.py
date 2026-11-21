# -*- coding: utf-8 -*-
"""VIDEO DÀI 'Top 15 Pháp Bảo Tây Du' — PIPELINE FULL (dựng theo CỤM 5 phút).

Chuẩn (người dùng chốt 21/11/2026):
  • CHỈ fade khi ĐỔI cảnh (dissolve, không đen). Cùng 1 cảnh nhiều câu → khung chạy LIỀN MẠCH,
    nhân vật chỉ NHỊP NHẸ (thở/nhún). (Sửa lỗi cũ: fade-to-black đầu+cuối mỗi câu → chớp đen.)
  • Mỗi món có INFO (ải/kiếp nạn + boss/yêu quái) + HIỆU ỨNG (demo_* từ storyboard).
  • Nhân vật quan trọng vẽ chi tiết (Bộ Bút) — hiện tạm silhouette, thay dần khi vẽ xong.

Tái dùng:
  short01.py  → sprite()/silhouette(), giọng ZeroTTS (VOICE), SFX, mouths_for()
  storyboard_phapbao.py → nền 16:9, memory_card, score_badge, title_card, pop_text, demo_* (hiệu ứng)

Chạy (theo cụm — render + mux ra 1 file / cụm):
    PYTHONUTF8=1 HF_HUB_DISABLE_XET=1 python scripts/hoathinh/but/video_phapbao.py --part 1
    ...--part 2   |  ...--part 3   |  ...--part all
    ...--part 1 --audio   (chỉ dựng lại tiếng, dùng khung đã render)
    ...--concat           (ghép 3 cụm thành phapbao-full.mp4)
Ra: du-an/tay-du-ky/output/long/phapbao-p<N>.mp4  (+ phapbao-full.mp4)
"""
import os
import sys
import glob
import hashlib
import subprocess
import math

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import numpy as np
import scipy.signal as sps
import soundfile as sf
from PIL import Image, ImageDraw

import short01 as SH            # sprite, silhouette, VOICE, SFX, mouths_for, put/tone/whoosh/thud/clash
import storyboard_phapbao as SB  # nền 16:9, memory_card, score_badge, title_card, pop_text, demo_*

W, H = SB.W, SB.H               # 1920 x 1080
FPS = SH.FPS                    # 24
SR = SH.SR                      # 44100
GAP = 0.34                      # khoảng lặng cuối mỗi câu (giây)
GY = int(H * 0.965)             # mặt đất (mép chân nhân vật)

OUTDIR = os.path.join(ROOT, 'du-an', 'tay-du-ky', 'output', 'long')

# giọng theo MÃ nhân vật
VOICE_MA = {'ngo-khong': 'giahuy', 'bat-gioi': 'quangminh',
            'sa-tang': 'huuduc', 'duong-tang': 'tiendat'}

# ───────────────────────── KỊCH BẢN FULL (theo v2) ─────────────────────────
# mỗi SCENE = 1 "khung cảnh" (đổi scene mới dissolve). chars: (ma, bc, xf, h, flip)
#   speaker lấy mouth theo giọng; các nhân vật còn lại nhịp nhẹ.
# info: (ải/kiếp nạn, boss/yêu quái)  ·  fx: key demo trong SB.DEMOS (hiệu ứng sau thoại)
HOOK = [('sa-tang', 'hien', 0.12, 330, False), ('bach-long-ma', 'hien', 0.29, 300, False),
        ('duong-tang', 'hien', 0.46, 340, False), ('bat-gioi', 'quyet', 0.65, 330, True),
        ('ngo-khong', 'quyet', 0.84, 350, False)]

SCENES = [
 # ---------------- CỤM 1 (0–~5:00) ----------------
 {'id': 's01', 'part': 1, 'bg': ('quan_tra', 'xe'), 'chars': HOOK,
  'title': 'ĐẠI CHIẾN PHÁP BẢO',
  'lines': [
    ('ngo-khong', 'Khắp Tam Giới, pháp bảo mạnh nhất, khỏi bàn! Gậy Như Ý của lão Tôn, một gậy sập cả Thiên Cung!'),
    ('bat-gioi', 'Xì! Mạnh gì mà bị hút vào hồ lô, úp trong chuông, trói bằng dây. Có món chỉ cần gọi tên là đại sư huynh bay tọt vào trong!'),
    ('sa-tang', 'Thôi, cãi suông tới sáng. Ta xếp hạng đàng hoàng: mười lăm pháp bảo đỉnh nhất Tây Du, chấm điểm sức mạnh.'),
    ('ngo-khong', 'Xếp thì xếp! Gậy lão Tôn số một, khỏi cãi!'),
    ('sa-tang', 'Đại sư huynh, e là hôm nay gậy của ngươi không đứng số một đâu.'),
    ('ngo-khong', 'Hả?! Món nào dám trên gậy lão Tôn?!'),
    ('duong-tang', 'Xem hết rồi biết. Nhớ, thứ mạnh nhất chưa chắc là thứ lợi hại nhất.'),
  ]},
 {'id': 's_title', 'part': 1, 'bg': ('quan_tra', 'xe'), 'chars': [],
  'big': 'TOP 15 PHÁP BẢO', 'small': 'Pháp bảo nào MẠNH NHẤT Tây Du Ký?', 'dur': 1.8},

 {'id': 's02', 'part': 1, 'bg': ('song',),
  'chars': [('sa-tang', 'hien', 0.14, 500, False), ('bat-gioi', 'vui', 0.32, 500, True)],
  'cards2': [('bao_truong', '5.0', 0.60), ('dinh_ba', '6.0', 0.85)], 'fx': 'khoidong',
  'title': 'KHỞI ĐỘNG — Vũ khí thầy trò',
  'info': ('Lưu Sa Hà · trước khi theo thầy', 'Sa Tăng · Bát Giới'),
  'lines': [
    ('sa-tang', 'Khởi động bằng đồ nhà mình. Hàng Yêu Bảo Trượng của ta, Lỗ Ban đẽo từ cây sa-la trên cung trăng, nặng năm nghìn không trăm bốn tám cân.'),
    ('bat-gioi', 'Nặng ngang bừa của ta! Cửu Xỉ Đinh Ba, chính tay Thái Thượng Lão Quân rèn, một bừa chín lỗ máu!'),
    ('ngo-khong', 'Chín lỗ, trên vỏ bí nhà ngươi thì có.'),
    ('sa-tang', 'Thành thật: ta năm điểm, bừa nhỉnh hơn nhờ gốc Lão Quân, sáu. Qua nhanh kẻo mất lòng!'),
  ]},

 {'id': 's03', 'part': 1, 'bg': ('troi',),
  'chars': [('ngo-khong', 'vui', 0.24, 560, False), ('sa-tang', 'hien', 0.50, 460, False)],
  'card': 'gay_nhu_y', 'cardx': 0.80, 'diem': '9.0', 'fanfare': True, 'fx': 's03',
  'title': 'GẬY NHƯ Ý — 13.500 cân',
  'info': ('Đông Hải Long Cung · Đại náo Thiên Cung', 'Ngộ Không'),
  'lines': [
    ('ngo-khong', 'Giờ mới tới hàng thật! Định Hải Thần Châm trấn đáy Đông Hải, một vạn ba nghìn năm trăm cân. To thì chọc thủng trời, nhỏ thì giấu trong tai!'),
    ('bat-gioi', 'Cái này ta công nhận. Đại náo Thiên Cung, mười vạn thiên binh giữ không nổi.'),
    ('sa-tang', 'Công năng, thực chiến, đẳng cấp đều đỉnh. Nhưng trục khắc chế của gậy thì yếu. Cả video này toàn món trói, úp, hút, thổi được nó. Nên chín, không phải mười.'),
    ('ngo-khong', 'Khắc chế yếu? Lão Tôn mà...'),
    ('sa-tang', 'Cứ xem hết đi rồi cãi.'),
  ]},

 {'id': 's04', 'part': 1, 'bg': ('quan_tra', 'xe'),
  'chars': [('duong-tang', 'quyet', 0.22, 520, False), ('ngo-khong', 'buon', 0.46, 470, True)],
  'card': 'vong_kim_co', 'cardx': 0.80, 'diem': '7.5', 'fx': 's04',
  'title': 'VÒNG KIM CÔ — 7.5',
  'info': ('Quan Âm ban · siết đầu Ngộ Không', 'Quan Âm Bồ Tát / Đường Tăng'),
  'lines': [
    ('duong-tang', 'Món tiếp theo ở ngay trên đầu đồ đệ lớn của ta.'),
    ('ngo-khong', 'Sư phụ! Đừng niệm! Con...'),
    ('bat-gioi', 'Cả Thiên đình mười vạn thiên binh không nhốt nổi đại sư huynh. Vậy mà sư phụ chỉ cần lẩm bẩm ba câu, là ổng lăn ra ôm đầu! Đây, pháp bảo mạnh nhất Tây Du nè!'),
    ('sa-tang', 'Sát thương bằng không, mà trị đúng kẻ mạnh nhất đoàn. Quản lý còn ghê hơn đánh. Bảy rưỡi.'),
    ('duong-tang', 'Vũ khí lợi hại nhất, đôi khi không phải để giết, mà để giữ người lại.'),
  ]},

 {'id': 's05', 'part': 1, 'bg': ('troi',),
  'chars': [('sa-tang', 'hien', 0.15, 540, False)],
  'card': 'tinh_binh', 'cardx': 0.80, 'diem': '8.0', 'fx': 's05',
  'title': 'TỊNH BÌNH DƯƠNG LIỄU — 8.0',
  'owner_sil': ('bach-cot-tinh', (150, 210, 205)), 'owner_x': 0.42, 'owner_h': 500,
  'info': ('Nam Hải · cứu cây nhân sâm, thu Hồng Hài Nhi', 'Quan Âm Bồ Tát'),
  'lines': [
    ('sa-tang', 'Tịnh Bình Dương Liễu. Một giọt cam lồ, cải tử hoàn sinh. Cây nhân sâm ngàn năm bị đánh đổ cũng sống lại.'),
    ('ngo-khong', 'Chưa hết. Lúc thu Hồng Hài Nhi, Bồ Tát đổ cả một biển nước vào trong bình, nghiêng tay là tràn ra biển lớn. Nhỏ mà chứa cả đại dương!'),
    ('bat-gioi', 'Vừa cứu người vừa nhốt yêu, ghê thật.'),
    ('sa-tang', 'Giá mà nó đánh khoẻ như cứu thì chín điểm. Thiên về hỗ trợ nên ta để tám, vẫn là hàng khủng.'),
  ]},

 # ---------------- CỤM 2 (~5:00–10:00) ----------------
 {'id': 's06', 'part': 2, 'bg': ('hang', (58, 46, 20)),
  'chars': [('ngo-khong', 'buon', 0.26, 540, False)],
  'card': 'kim_nhieu', 'cardx': 0.78, 'diem': '8.5', 'fanfare': True, 'fx': 's06',
  'title': 'KIM NHIÊU — 8.5', 'owner_sil': ('duong-tang', (210, 180, 60)),
  'info': ('Tiểu Lôi Âm Tự · giả Phật', 'Hoàng Mi Lão Phật'),
  'lines': [
    ('ngo-khong', 'Món này ta không muốn nhắc. Kim Nhiêu của Hoàng Mi. Nó úp ta kín mít, biến to biến nhỏ gì cũng dính chặt, gậy chọc không thủng.'),
    ('bat-gioi', 'Phải mời hăm tám vị tinh tú xuống, rồi Kháng Kim Long lấy sừng chọc thủng mới lôi được đại sư huynh ra. Nằm trong đó tối lắm hả, ha ha...'),
    ('ngo-khong', 'Im! Đồ gì chạm vào là dính, kể cả binh khí thần tiên.'),
    ('sa-tang', 'Giam cầm tuyệt đối, khắc cả thần Phật. Tám rưỡi, Thần khí.'),
  ]},

 {'id': 's07', 'part': 2, 'bg': ('troi',),
  'chars': [('sa-tang', 'hien', 0.22, 500, False), ('ngo-khong', 'quyet', 0.46, 470, True)],
  'card': 'chieu_yeu_kinh', 'cardx': 0.80, 'diem': '6.5', 'fx': 's07',
  'title': 'GƯƠNG 6.5  vs  THÁP 6.0', 'owner_sil': ('bach-cot-tinh', (200, 205, 210)),
  'info': ('Thật giả Mỹ Hầu Vương · trị Na Tra', 'Thác Tháp Lý Thiên Vương'),
  'lines': [
    ('sa-tang', 'Hai món cùng một chủ, Thác Tháp Lý Thiên Vương. Cho chúng đấu nhau cho vui. Gương trước: Chiếu Yêu Kính, chiếu cái, mọi yêu ma lộ nguyên hình.'),
    ('ngo-khong', 'Hữu dụng đấy, nhưng hồi Lục Nhĩ Mỹ Hầu giả lão Tôn, cái gương soi ra hai con y hệt, bó tay luôn!'),
    ('bat-gioi', 'Gương cũng có lúc lác! Còn cái tháp? Giơ lên là thu người vào trong, chính nó khống chế được Na Tra tam thái tử.'),
    ('sa-tang', 'Gương làm do thám số một, đánh đấm số không, sáu rưỡi. Tháp khống chế gọn nhưng công năng hẹp, sáu. Huề, qua món máu hơn!'),
  ]},

 {'id': 's09', 'part': 2, 'bg': ('nui',),
  'chars': [('ngo-khong', 'buon', 0.24, 520, False), ('bat-gioi', 'vui', 0.48, 500, True)],
  'card': 'hoang_kim_thang', 'cardx': 0.80, 'diem': '7.0', 'fx': 's09',
  'title': 'HOẢNG KIM THẰNG — 7.0',
  'info': ('Bình Đính Sơn · Liên Hoa Động', 'Kim Giác Đại Vương'),
  'lines': [
    ('ngo-khong', 'Hoảng Kim Thằng của đám Bình Đính Sơn. Trói được cả thần tiên. Ta bị quấn, càng giãy càng chặt.'),
    ('bat-gioi', 'Ghi sổ! Bị trói, một lần nữa nhé. Hôm nay bảng điểm cũng là bảng những lần Tôn Ngộ Không lãnh đủ ha?'),
    ('ngo-khong', 'Trư Bát Giới! Còn ngươi? Bị Hồng Hài Nhi tóm bỏ bao, bị yêu quái đòi hấp chín cả lò, ta quên à?!'),
    ('bat-gioi', 'Ờ thì, ta gạch dòng đó đi vậy.'),
    ('sa-tang', 'Ác ở chỗ: kẻ cầm dây biết khẩu quyết thì cởi, kẻ bị trói không biết thì chịu chết. Bảy điểm.'),
  ]},

 {'id': 's10', 'part': 2, 'bg': ('hang', (52, 36, 58)),
  'chars': [('bat-gioi', 'vui', 0.24, 500, False), ('ngo-khong', 'buon', 0.48, 470, True)],
  'card': 'ho_lo', 'cardx': 0.80, 'diem': '8.5', 'fanfare': True, 'fx': 's10',
  'title': 'HỒ LÔ TỬ KIM — 8.5', 'owner_sil': ('tieu-yeu', (150, 90, 160)),
  'info': ('Bình Đính Sơn · Liên Hoa Động', 'Kim Giác · Ngân Giác'),
  'lines': [
    ('bat-gioi', 'Đây! Món ta nhắc từ đầu! Gọi đúng tên, ngươi dạ một tiếng là bị hút tọt vào, một lát hoá nước! Gậy một vạn ba nghìn rưỡi cân để làm gì?!'),
    ('ngo-khong', 'Thì ta tráo một cái hồ lô giả, rồi xưng tên đảo Giả Hành Tôn lừa nó mới thoát! Đấu trí chứ bộ, đâu phải đấu sức!'),
    ('sa-tang', 'Đây mới là khắc tinh của cao thủ: không cần mạnh hơn ngươi, chỉ cần ngươi lỡ miệng đáp lời. Cặp này suýt kết liễu đại ca. Tám rưỡi, Thần khí.'),
    ('duong-tang', 'Thấy chưa, món trị kẻ mạnh nhất lại là món nhẹ nhàng nhất.'),
  ]},

 {'id': 's11', 'part': 2, 'bg': ('lua',),
  'chars': [('sa-tang', 'hien', 0.24, 520, False), ('ngo-khong', 'ngac', 0.48, 470, True)],
  'card': 'quat_ba_tieu', 'cardx': 0.80, 'diem': '8.0', 'fx': 's11', 'owner_sil': ('nu-vuong', (230, 120, 70)),
  'title': 'QUẠT BA TIÊU — 8.0',
  'info': ('Hoả Diệm Sơn · vợ Ngưu Ma Vương', 'Thiết Phiến Công Chúa'),
  'lines': [
    ('sa-tang', 'Quạt Ba Tiêu, báu vật trời đất. Một phẩy dập tắt tám trăm dặm lửa Hoả Diệm Sơn. Phẩy vào người thì...'),
    ('ngo-khong', 'Bay tám vạn bốn nghìn dặm, tới tận Tiểu Tu Di Sơn! Ta phải nuốt Định Phong Đan mới đứng yên nổi mà mượn quạt.'),
    ('bat-gioi', 'Lại bị thổi bay, chấm thêm một dòng!'),
    ('sa-tang', 'Uy lực đổi cả thời tiết, tầm thiên tai. Tám điểm, mạnh hơn nhờ quy mô.'),
  ]},

 # ---------------- CỤM 3 (~10:00–kết) ----------------
 {'id': 's12', 'part': 3, 'bg': ('lua',),
  'chars': [('ngo-khong', 'buon', 0.28, 540, False)],
  'card': 'tam_muoi', 'cardx': 0.78, 'diem': '7.5', 'fx': 's12', 'owner_sil': ('tieu-yeu-do', (240, 70, 50)),
  'title': 'TAM MUỘI CHÂN HOẢ — 7.5',
  'info': ('Hoả Vân Động · con Ngưu Ma Vương', 'Hồng Hài Nhi'),
  'lines': [
    ('ngo-khong', 'Thằng nhóc Hồng Hài Nhi. Tam Muội Chân Hoả, nước dội không tắt, càng dội càng bùng. Ta xông vào cứu sư phụ suýt toi mạng, phải đi cầu Bồ Tát.'),
    ('bat-gioi', 'Một đứa con nít mà hành đại sư huynh tới mức phải đi cầu viện! Lửa đó ghê thật, hay tại đại ca già rồi ha?'),
    ('ngo-khong', 'Ngươi...!'),
    ('sa-tang', 'Sát thương khủng, nhưng cuối cùng bị Bồ Tát khắc gọn. Bảy rưỡi.'),
  ]},

 {'id': 's13', 'part': 3, 'bg': ('quan_tra', 'trua'),
  'chars': [('duong-tang', 'hien', 0.22, 520, False), ('bat-gioi', 'vui', 0.48, 500, True)],
  'card': 'nhan_sam', 'cardx': 0.80, 'diem': '7.0', 'fx': 's13',
  'title': 'NHÂN SÂM QUẢ — 7.0',
  'info': ('Ngũ Trang Quán · đổ cây nhân sâm', 'Trấn Nguyên Đại Tiên'),
  'lines': [
    ('duong-tang', 'Có thứ không chém giết ai, nhưng cả Tam Giới thèm: Nhân Sâm Quả của Trấn Nguyên Đại Tiên, bậc Địa Tiên chi tổ.'),
    ('bat-gioi', 'Ngửi thôi đã sống ba trăm sáu mươi tuổi! Ăn một quả, bốn vạn bảy nghìn năm! Mà con nuốt chửng không kịp nếm, tiếc đứt ruột tới giờ!'),
    ('sa-tang', 'Món này không đánh ai, chỉ khiến nhị sư huynh chảy nước miếng. Mà cỡ đó cũng đáng bảy điểm.'),
  ]},

 {'id': 's14', 'part': 3, 'bg': ('lua', 'khoi'),
  'chars': [('duong-tang', 'hien', 0.22, 520, False), ('bat-gioi', 'vui', 0.48, 500, True)],
  'card': 'ca_sa', 'cardx': 0.80, 'diem': '4.0', 'fx': 's14',
  'title': 'CẨM LAN CÀ SA — 4.0 (thấp nhất)',
  'info': ('Quán Âm Thiền Viện · cướp cà sa', 'Hắc Hùng Tinh (Hắc Phong Sơn)'),
  'lines': [
    ('duong-tang', 'Chiếc cà sa này nước lửa không xâm, tránh tai ương...'),
    ('bat-gioi', 'Nhưng nó gây tai ương thì nhiều hơn! Sư phụ đem khoe, ông sư già tham đốt cả thiền viện để cướp. Suýt toi cả đoàn!'),
    ('ngo-khong', 'Bốn điểm! Cái áo khoe một phát cháy luôn cả chùa, đồ mạnh kiểu phá hoại nội bộ ha!'),
    ('sa-tang', 'Hộ thân thì có, sức mạnh thì bốn. Thấp nhất bảng. Nghỉ xả hơi tí, rồi tới món khiến lão Tôn á khẩu.'),
  ]},

 {'id': 's15', 'part': 3, 'bg': ('hang', (40, 46, 58)),
  'chars': [('ngo-khong', 'buon', 0.26, 540, False)],
  'card': 'kim_cang_trac', 'cardx': 0.78, 'diem': '9.5', 'fanfare': True, 'fx': 's15',
  'title': 'CÚ LẬT: KIM CANG TRÁC — 9.5 (SỐ 1)', 'owner_sil': ('bach-long-ma', (110, 150, 200)),
  'info': ('Kim Đâu Sơn · Kim Đâu Động · trâu xanh Lão Quân', 'Độc Giác Tỷ Đại Vương'),
  'lines': [
    ('ngo-khong', 'Còn một món. Món khiến lão Tôn á khẩu. Kim Cang Trác của Độc Giác Tỷ Đại Vương. Nó hút bay gậy Như Ý của ta ngay giữa trận, ta trơ tay!'),
    ('bat-gioi', 'Hút cả gậy một vạn ba nghìn rưỡi cân?? Vậy nó trên cả gậy đại sư huynh à?!'),
    ('sa-tang', 'Không chỉ gậy, nó hút luôn binh khí thiên tướng, hoả khí Hoả Đức Tinh Quân, cả nước của Thuỷ Bá, không chừa thứ gì. Cả nhà trời bó tay, phải mời Thái Thượng Lão Quân tới. Hoá ra con yêu là con trâu xanh ngài cưỡi. Khắc chế gần như tuyệt đối, chín rưỡi, cao nhất bảng!'),
    ('ngo-khong', 'Khoan. Cái vòng đó, chính nó ném trúng đầu lão Tôn lúc đại náo Thiên Cung, làm ta ngã mới bị bắt. Thì ra kẻ hạ ta năm xưa, là một cái vòng của con trâu. Lão Tôn không phục, nhưng phải phục.'),
  ]},

 {'id': 's16', 'part': 3, 'bg': ('quan_tra', 'chieu'),
  'chars': [('sa-tang', 'hien', 0.12, 320, False), ('bach-long-ma', 'hien', 0.29, 290, False),
            ('duong-tang', 'hien', 0.46, 330, False), ('bat-gioi', 'vui', 0.65, 320, True),
            ('ngo-khong', 'quyet', 0.84, 340, False)],
  'big': 'SỐ 1 LÀ MÓN NÀO?', 'small': 'Kim Cang Trác · Gậy Như Ý · hay Hồ Lô? Gõ phe của bạn',
  'lines': [
    ('sa-tang', 'Kết quả. Số một: Kim Cang Trác, chín rưỡi, cái vòng hút sạch thiên hạ. Số hai: Gậy Như Ý, chín. Số liệu là số liệu, ta không thiên vị ai.'),
    ('ngo-khong', 'Hừ! Cái vòng đó phải nhờ Lão Quân ra mặt mới đòi lại được. Còn gậy lão Tôn, tự tay đại náo Thiên Cung!'),
    ('bat-gioi', 'Để nhị sư huynh tổng kết! Cả bảng hôm nay, đại sư huynh bị: niệm chú ôm đầu, úp chuông Kim Nhiêu, hút hồ lô, trói dây vàng, thổi bay tám vạn tư dặm, thiêu ho khói, và hút mất gậy! Bảy lần! Lịch sử nên gọi đây là Top mười lăm lần Tôn Ngộ Không lãnh đủ!'),
    ('ngo-khong', 'Trư Bát Giới! Ta xé cuốn sổ đó...'),
    ('duong-tang', 'Thôi nào. Pháp bảo cũng như con người, mạnh hay yếu không nằm ở to với nặng, mà ở chỗ có gặp đúng khắc tinh hay không. Thứ hợp cảnh mới là thứ mạnh nhất.'),
    ('sa-tang', 'Còn bạn? Theo bạn số một thật sự là Kim Cang Trác, hay Gậy Như Ý, hay hồ lô gọi tên mới bá nhất? Gõ phe của bạn ở dưới.'),
  ]},
]


# ───────────────────────── GIỌNG ─────────────────────────
def scene_lines(scenes):
    out = []
    for sc in scenes:
        for ma, text in sc.get('lines', []):
            out.append((ma, text))
    return out


def gen_voices(scenes, work):
    lines = scene_lines(scenes)
    cache = os.path.join(work, 'voices.npz')
    sig = hashlib.md5('|'.join(t for _, t in lines).encode('utf-8')).hexdigest()
    if os.path.exists(cache):
        try:
            z = np.load(cache, allow_pickle=True)
            if z['sig'].item() == sig:
                outs = [z['a%d' % i].astype(np.float32) for i in range(len(lines))]
                print('  (dùng cache %d câu)' % len(outs), flush=True)
                return outs
        except Exception as e:
            print('  (cache giọng hỏng, tạo lại:', e, ')', flush=True)
    from zerotts import ZeroTTS, normalize_vi_text
    tts = ZeroTTS.from_pretrained('zeroweight-ai/ZeroTTS')
    sr = tts.sample_rate
    outs = []
    for i, (ma, text) in enumerate(lines):
        best = None
        for k in range(2):
            np.random.seed(11 + k)
            a = tts.synthesize(normalize_vi_text(text), voice=VOICE_MA[ma], cfg_scale=1.0).reshape(-1).astype(np.float32)
            idx = np.where(np.abs(a) > 0.012)[0]
            if idx.size:
                a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
            if best is None or a.size > best.size:
                best = a
        a44 = sps.resample_poly(best, SR, sr).astype(np.float32)
        outs.append(a44)
        print('  câu %d/%d [%s] %.2fs' % (i + 1, len(lines), ma, a44.size / SR), flush=True)
    try:
        np.savez(cache, sig=sig, **{'a%d' % i: a for i, a in enumerate(outs)})
    except Exception as e:
        print('  (không lưu cache giọng:', e, ')', flush=True)
    return outs


# ───────────────────────── DỰNG KHUNG ─────────────────────────
def info_panel(bg, info):
    if not info:
        return
    ai, boss = info
    rows = [('Ải / kiếp nạn:', ai), ('Yêu quái:', boss)]
    d = ImageDraw.Draw(bg, 'RGBA')
    fl = SB.font(34); fv = SB.font(38)
    wmax = 0
    for lab, val in rows:
        wmax = max(wmax, d.textlength(lab + '  ', font=fl) + d.textlength(val, font=fv))
    x0, y0 = 48, 150
    pad, lh = 24, 58
    x1, y1 = x0 + int(wmax) + pad * 2, y0 + lh * len(rows) + pad
    d.rounded_rectangle([x0 + 6, y0 + 7, x1 + 6, y1 + 7], 18, fill=(0, 0, 0, 90))   # đổ bóng
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(24, 18, 30, 224), outline=(240, 208, 120, 245), width=4)
    for i, (lab, val) in enumerate(rows):
        yy = y0 + pad // 2 + i * lh
        d.text((x0 + pad, yy + 3), lab, font=fl, fill=(240, 208, 120))
        d.text((x0 + pad + d.textlength(lab + '  ', font=fl), yy), val, font=fv, fill=(255, 246, 226))


def draw_owner(bg, sc):
    """Chủ sở hữu (thần/Phật) = silhouette tối + VIỀN VÀNG dạng stroke (nổi trên MỌI nền) + hào quang vàng
    + vầng hào quang trên đầu. Đứng tách riêng, không đè nhân vật. (Boss đụng độ thay bằng sprite chi tiết sau.)"""
    if not sc.get('owner_sil'):
        return
    ma, col = sc['owner_sil']
    cx = int(W * sc.get('owner_x', 0.44))
    hh = sc.get('owner_h', 470)
    GOLD = (255, 222, 120)
    spr = SH.sprite(ma, 'quyet', 'mim', h=hh)
    hy = GY - int(hh * 0.80)   # đầu
    # hào quang toả (tint theo chủ + lõi vàng ấm) — đủ đậm để nổi trên nền sáng
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
    for r, al in [(190, 46), (140, 72), (95, 110)]:
        dg.ellipse([cx - r, hy - r, cx + r, hy + r], fill=col + (al,))
    for r, al in [(120, 40), (70, 70)]:
        dg.ellipse([cx - r, hy - r, cx + r, hy + r], fill=GOLD + (al,))
    bg.alpha_composite(glow)
    # VIỀN VÀNG = stroke: dán silhouette vàng lệch 8 hướng rồi dán silhouette tối lên trên
    rim = SH.silhouette(spr, col=GOLD)
    for ox, oy in [(-6, 0), (6, 0), (0, -6), (0, 6), (-5, -5), (5, -5), (-5, 5), (5, 5)]:
        SB.paste_mid(bg, rim, cx + ox, GY + oy)
    sil = SH.silhouette(spr, col=(34, 30, 42))
    SB.paste_mid(bg, sil, cx, GY)
    # vầng hào quang trên đầu (viền tối mỏng để nổi trên nền sáng + vòng vàng)
    d = ImageDraw.Draw(bg, 'RGBA')
    d.ellipse([cx - 70, hy - 92, cx + 70, hy - 22], outline=(40, 30, 10, 200), width=12)
    d.ellipse([cx - 70, hy - 92, cx + 70, hy - 22], outline=GOLD + (255,), width=7)
    # điểm ngọc sáng lấp lánh
    for sx, sy in [(-40, -70), (46, -40), (-10, -96)]:
        d.ellipse([cx + sx - 7, hy + sy - 7, cx + sx + 7, hy + sy + 7], fill=(255, 255, 240, 235))


def build_base(sc):
    """Nền + chủ sở hữu + thẻ ký ức + badge + info + tiêu đề (TĨNH, không nhân vật chính)."""
    bg = SB.make_bg(sc['bg'])
    draw_owner(bg, sc)
    # thẻ ký ức (item) + badge — hỗ trợ 1 hoặc 2 thẻ
    if sc.get('cards2'):
        for ma, diem, cxf in sc['cards2']:
            cx = int(W * cxf)
            SB.memory_card(bg, ma, cx, int(H * 0.44), 330)
            SB.score_badge(bg, cx, int(H * 0.75), diem)
    elif sc.get('card'):
        cx = int(W * sc.get('cardx', 0.80))
        SB.memory_card(bg, sc['card'], cx, int(H * 0.44), sc.get('cardsz', 430))
        if sc.get('diem'):
            SB.score_badge(bg, cx, int(H * 0.80), sc['diem'])
    # bóng chân nhân vật chính (tĩnh)
    for (ma, bc, xf, hh, fl) in sc.get('chars', []):
        SB.soft_shadow(bg, int(W * xf), GY, w=int(hh * 0.30))
    # tiêu đề / info
    if sc.get('big'):
        SB.title_card(bg, sc['big'], sc.get('small'))
    else:
        if sc.get('title'):
            SB.pop_text(bg, sc['title'], W // 2, int(H * 0.045), sc.get('tsize', 56), (255, 234, 150), 8)
        info_panel(bg, sc.get('info'))
    return bg


def place_char(im, ma, bc, mi, xf, hh, fl, gt, phase):
    """Dán nhân vật có NHỊP NHẸ (thở/nhún) theo thời gian tuyệt đối gt."""
    br = math.sin(2 * math.pi * (gt * 0.42 + phase))        # ~2.4s/chu kỳ, lệch pha mỗi người
    sc = 1.0 + 0.007 * br
    spr = SH.sprite(ma, bc, mi, h=hh, flip=fl)
    dy = int(3.4 * br)
    SB.paste_mid(im, spr, int(W * xf), GY + dy, sc=sc)


def slow_zoom(img, gt):
    """Phóng nhẹ LIÊN TỤC theo thời gian tuyệt đối (không reset theo câu → không giật)."""
    z = 1.016 + 0.014 * math.sin(2 * math.pi * gt / 11.0)
    cw, ch = int(W / z), int(H / z)
    x = (W - cw) // 2 + int((W - cw) * 0.12 * math.sin(2 * math.pi * gt / 17.0))
    y = (H - ch) // 2
    x = max(0, min(W - cw, x))
    return img.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)


def compose_line(base, sc, speaker, mouth, gt):
    im = base.copy()
    for (ma, bc, xf, hh, fl) in sc['chars']:
        mi = mouth if ma == speaker else 'mim'
        bcc = bc
        phase = xf  # pha theo vị trí
        place_char(im, ma, bcc, mi, xf, hh, fl, gt, phase)
    return slow_zoom(im.convert('RGB'), gt)


# ───────────────────────── HIỆU ỨNG RIÊNG (không có trong SB.DEMOS) ─────────────────────────
def fx_khoidong():
    """Hiệu ứng mở màn ①②: hai vũ khí BỔ XUỐNG + tia lực + nổ bụi phá núi lấp sông."""
    import math as _m
    bg = SB.bg_song()
    d = ImageDraw.Draw(bg, 'RGBA')
    # hai vũ khí nghiêng như đang bổ xuống
    t1 = SB.treasure_img('bao_truong', 500).rotate(28, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(t1, (int(W * 0.06), int(H * 0.16)))
    t2 = SB.treasure_img('dinh_ba', 500).rotate(-26, expand=True, resample=Image.BICUBIC)
    bg.alpha_composite(t2, (int(W * 0.56), int(H * 0.14)))
    # vệt lực (speed lines) chéo theo hướng bổ
    for i in range(-5, 6):
        d.line([(int(W * 0.22) + i * 30, int(H * 0.20)), (int(W * 0.30) + i * 30, int(H * 0.60))],
               fill=(255, 255, 255, 120), width=5)
        d.line([(int(W * 0.78) + i * 30, int(H * 0.18)), (int(W * 0.70) + i * 30, int(H * 0.58))],
               fill=(255, 255, 255, 120), width=5)
    # 2 điểm va chạm: vòng sóng + sao nổ + bụi
    for cx, col in [(int(W * 0.24), (210, 190, 140)), (int(W * 0.72), (210, 190, 140))]:
        cy = int(H * 0.72)
        for r in (70, 120, 175, 230):
            d.ellipse([cx - r, cy - r * 0.42, cx + r, cy + r * 0.42], outline=col + (160,), width=8)
        for a in range(0, 360, 30):
            an = _m.radians(a)
            d.line([cx + _m.cos(an) * 60, cy + _m.sin(an) * 34, cx + _m.cos(an) * 150, cy + _m.sin(an) * 84],
                   fill=(255, 244, 190, 170), width=6)
        d.regular_polygon((cx, cy, 70), 12, fill=(255, 250, 220, 180))
    SB.pop_text(bg, 'ĐỒ GIỮ NHÀ · PHÁ NÚI LẤP SÔNG', W // 2, int(H * 0.055), 54, (255, 230, 120), 9)
    return bg.convert('RGB')


FX_LOCAL = {'khoidong': fx_khoidong}


# ───────────────────────── NHẠC THEME (đàn tranh + dây + trống) ─────────────────────────
_BUTTER_LP = {}
def _lp(x, fc):
    key = round(fc)
    if key not in _BUTTER_LP:
        _BUTTER_LP[key] = sps.butter(2, min(0.99, fc / (SR / 2)))
    b, a = _BUTTER_LP[key]
    return sps.lfilter(b, a, x)


def _pluck(f, dur, amp=0.16, decay=0.9916, bright=4200):
    n = max(1, int(dur * SR)); N = max(2, int(round(SR / f)))
    x = np.zeros(n); m = min(N, n)
    x[:m] = (np.random.randn(m) * np.hanning(m))
    a = np.zeros(N + 1); a[0] = 1.0; a[N] = -decay
    y = sps.lfilter([1.0], a, x); y = _lp(y, bright)
    y *= np.exp(-np.arange(n) / (0.85 * SR))
    return amp * y / (np.max(np.abs(y)) or 1)


def _pad(freqs, dur, amp=0.09):
    n = max(1, int(dur * SR)); t = np.arange(n) / SR; w = np.zeros(n)
    for f in freqs:
        for det in (0.996, 1.004):
            ff = f * det
            for h in range(1, 7):
                w += np.sin(2 * np.pi * ff * h * t) / h
    w = _lp(w, 2200) / (len(freqs) * 2)
    e = np.ones(n); at, rl = int(0.35 * SR), int(0.55 * SR)
    e[:at] = np.linspace(0, 1, at)
    if rl < n:
        e[-rl:] *= np.linspace(1, 0, rl)
    return amp * w * e


def _taiko(amp=0.22):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = np.linspace(118, 46, n)
    body = np.sin(2 * np.pi * f * t) * np.exp(-t * 6)
    hit = np.random.randn(n) * np.exp(-t * 46) * 0.4
    return amp * (body + hit)


def _gong(amp=0.16):
    n = int(1.8 * SR); t = np.arange(n) / SR
    w = sum(np.sin(2 * np.pi * (174 * p) * t) for p in (1.0, 2.76, 5.4, 8.9))
    w = w * np.exp(-t * 1.7) + 0.18 * np.random.randn(n) * np.exp(-t * 6)
    return amp * w / 4


def _flute(f, dur, amp=0.05):
    n = max(1, int(dur * SR)); t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 4.5 * t)
    w = np.sin(2 * np.pi * f * t * vib) + 0.12 * np.sin(2 * np.pi * 2 * f * t)
    breath = _lp(np.random.randn(n), 2500) * 0.05
    e = np.ones(n); at = int(0.12 * SR); rl = int(0.25 * SR)
    e[:at] = np.linspace(0, 1, at)
    if rl < n:
        e[-rl:] *= np.linspace(1, 0, rl)
    return amp * (w + breath) * e


_N = {'A3': 220.0, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.0,
      'A4': 440.0, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25}
_CHORDS = [('A3', 'C4', 'E4'), ('A3', 'C4', 'G4'), ('C4', 'E4', 'G4'), ('D4', 'G4', 'A4')]
_MELODY = [('E4', 1), ('G4', 1), ('A4', 2), ('C5', 1), ('A4', 1), ('G4', 2),
           ('E4', 1), ('G4', 1), ('C5', 1), ('D5', 1), ('D5', 1), ('C5', 1), ('A4', 2)]
_FLUTE_BARS = {1, 3}


def theme_tay_du(total_s):
    np.random.seed(7)
    buf = np.zeros(int(total_s * SR) + SR)
    beat = 0.70; bar = 4 * beat
    bi, tt = 0, 0.0
    while tt < total_s:
        chord = [_N[k] for k in _CHORDS[bi % len(_CHORDS)]]
        SH.put(buf, tt, _pad(chord, bar * 0.98, amp=0.085))
        SH.put(buf, tt, _taiko(0.20))
        SH.put(buf, tt + 2 * beat, _taiko(0.13))
        if bi % 4 == 0:
            SH.put(buf, tt, _gong(0.14))
        if (bi % len(_CHORDS)) in _FLUTE_BARS:
            SH.put(buf, tt + 0.2, _flute(_N['A4'], bar * 0.7, amp=0.04))
        tt += bar; bi += 1
    tt, i = 0.0, 0
    while tt < total_s:
        key, bt = _MELODY[i % len(_MELODY)]
        dur = bt * beat
        SH.put(buf, tt, _pluck(_N[key], dur + 0.4, amp=0.17))
        i += 1; tt += dur
    return buf[:int(total_s * SR) + SR]


# ───────────────────────── ÂM THANH ─────────────────────────
def build_audio(segs, voices, total_s):
    buf = np.zeros(int(total_s * SR) + SR)
    th = theme_tay_du(total_s); buf[:th.size] += th
    n = int(total_s * SR); t = np.arange(n) / SR
    buf[:n] += 0.020 * np.sin(2 * np.pi * 110 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))
    SH.put(buf, 0.02, _gong(0.18))   # mở màn cho đỡ "hụt" đầu video
    for s in segs:
        st = s['start']
        if s.get('fanfare'):
            SH.put(buf, st, SH.whoosh(0.4, 0.5))
            for k, f in enumerate([392, 440, 523, 587, 659]):
                SH.put(buf, st + 0.12 * k, SH.tone(f, 0.5, amp=0.09, r=0.35))
            for k in range(3):
                SH.put(buf, st + 0.22 + 0.14 * k, SH.clash(0.16))
        if s['kind'] == 'title':
            SH.put(buf, st, SH.thud(0.4))
            SH.put(buf, st + 0.05, SH.tone(293.66, 1.1, amp=0.08, r=0.8))
            SH.put(buf, st + 0.05, SH.tone(392.0, 1.1, amp=0.05, r=0.8))
        elif s['kind'] == 'fx':
            SH.put(buf, st, SH.whoosh(0.34, 0.4))
            SH.put(buf, st + 0.12, SH.thud(0.4))
            SH.put(buf, st + 0.12, SH.clash(0.2))
        elif s['kind'] == 'line':
            if s['speaker'] == 'ngo-khong':
                SH.put(buf, st, SH.whoosh(0.22))
            else:
                SH.put(buf, st, SH.whoosh(0.16))
    for s in segs:
        if s['kind'] == 'line' and s.get('vi') is not None:
            v = voices[s['vi']]
            i0 = int(s['start'] * SR); i1 = min(len(buf), i0 + v.size)
            buf[i0:i1] *= 0.4
            SH.put(buf, s['start'], v, g=0.98)
    buf = 0.92 * buf / (np.max(np.abs(buf)) or 1)
    return buf


# ───────────────────────── SEGMENTS ─────────────────────────
def build_segments(scenes, voices):
    """Phẳng hoá scenes → segments; đánh dấu group (đổi group = dissolve)."""
    segs = []
    vi = 0
    for gi, sc in enumerate(scenes):
        has_line = bool(sc.get('lines'))
        if sc.get('big') and not has_line:
            # title thuần (ít dùng — s_title)
            segs.append({'kind': 'title', 'sc': sc, 'group': sc['id'] + '_t',
                         'nf': int(round(sc.get('dur', 1.8) * FPS)), 'fanfare': False})
            continue
        first = True
        for (ma, text) in sc.get('lines', []):
            v = voices[vi]
            nf = int(round((v.size / SR + GAP) * FPS))
            segs.append({'kind': 'line', 'sc': sc, 'group': sc['id'], 'speaker': ma,
                         'nf': nf, 'vi': vi, 'fanfare': sc.get('fanfare', False) and first})
            first = False
            vi += 1
        if sc.get('fx'):
            segs.append({'kind': 'fx', 'sc': sc, 'group': sc['id'] + '_fx',
                         'nf': int(round(1.6 * FPS)), 'fxkey': sc['fx'], 'fanfare': False})
    # mốc thời gian
    acc = 0
    for s in segs:
        s['start'] = acc / FPS
        s['f0'] = acc
        acc += s['nf']
    return segs, acc


# ───────────────────────── RENDER 1 CỤM ─────────────────────────
DISS = 5   # số khung dissolve khi đổi cảnh (ngắn hơn → bớt ghosting)


def render_part(part, audio_only=False, concat_only=False):
    scenes = [s for s in SCENES if s['part'] == part]
    work = os.path.join(ROOT, 'build', 'thu-hoathinh', 'phapbao-p%d' % part)
    os.makedirs(work, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(SH.WORK, exist_ok=True)

    print('• Giọng ZeroTTS (cụm %d)…' % part, flush=True)
    voices = gen_voices(scenes, work)
    segs, total_f = build_segments(scenes, voices)
    total_s = total_f / FPS
    print('• Cụm %d: %.1fs · %d khung · %d đoạn' % (part, total_s, total_f, len(segs)), flush=True)

    mseq = {s['vi']: SH.mouths_for(voices[s['vi']]) for s in segs if s['kind'] == 'line'}

    if not audio_only:
        for old in glob.glob(os.path.join(glob.escape(work), 'f_*.png')):
            try: os.remove(old)
            except OSError: pass
        print('• Render khung…', flush=True)
        base_cache = {}
        prev_group = None
        prev_last = Image.new('RGB', (W, H), (0, 0, 0))   # khung trước (để dissolve)
        gi = 0
        for si, s in enumerate(segs):
            sc = s['sc']
            new_group = (s['group'] != prev_group)
            # base của cảnh (cache theo id cảnh — nền/thẻ tĩnh)
            if s['kind'] == 'fx':
                if s['fxkey'] in FX_LOCAL:
                    fx_img = FX_LOCAL[s['fxkey']]()
                else:
                    fx_img = SB.DEMOS[s['fxkey']][0]()   # RGB full frame hiệu ứng
            else:
                if sc['id'] not in base_cache:
                    base_cache[sc['id']] = build_base(sc)
                base = base_cache[sc['id']]
            nf = s['nf']
            ms = mseq.get(s.get('vi'))
            for k in range(nf):
                gt = (s['f0'] + k) / FPS
                if s['kind'] == 'line':
                    mouth = 'mim'
                    if ms:
                        mouth = ms[min(len(ms) - 1, int((k / max(1, nf)) * len(ms)))]
                    out = compose_line(base, sc, s['speaker'], mouth, gt)
                elif s['kind'] == 'title':
                    out = slow_zoom(base.convert('RGB'), gt)
                else:  # fx
                    out = slow_zoom(fx_img, gt)   # demo_* trả RGB sẵn
                # dissolve khi ĐỔI cảnh (group) — chỉ ở DISS khung đầu group
                if new_group and k < DISS:
                    a = (k + 1) / (DISS + 1)
                    out = Image.blend(prev_last, out, a)
                out.save(os.path.join(work, 'f_%05d.png' % gi))
                last_out = out
                gi += 1
            prev_group = s['group']
            prev_last = last_out
            print('\r  %d/%d  %s' % (si + 1, len(segs), s['group']), end='', flush=True)
        # fade-out cuối cụm
        for j in range(DISS):
            a = 1 - (j + 1) / (DISS + 1)
            Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), prev_last, a).save(os.path.join(work, 'f_%05d.png' % gi))
            gi += 1
        total_f = gi
        total_s = total_f / FPS
        print('\n  (đã render %d khung)' % total_f, flush=True)
    else:
        total_f = len(glob.glob(os.path.join(glob.escape(work), 'f_*.png')))
        total_s = total_f / FPS
        print('• Dùng %d khung sẵn có' % total_f, flush=True)

    print('• Tổng hợp tiếng…', flush=True)
    buf = build_audio(segs, voices, total_s)
    wav = os.path.join(work, 'tieng.wav')
    sf.write(wav, buf.astype(np.float32), SR)

    print('• Ghép + mux…', flush=True)
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    silent = os.path.join(work, 'silent.mp4')
    subprocess.run([ff, '-y', '-framerate', str(FPS), '-i', os.path.join(work, 'f_%05d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', silent],
                   check=True, capture_output=True)
    out = os.path.join(OUTDIR, 'phapbao-p%d.mp4' % part)
    subprocess.run([ff, '-y', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', out], check=True, capture_output=True)
    print('XONG cụm %d →' % part, out, '| %.1fs' % total_s, flush=True)
    return out


def concat_all():
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    parts = [os.path.join(OUTDIR, 'phapbao-p%d.mp4' % p) for p in (1, 2, 3)]
    parts = [p for p in parts if os.path.exists(p)]
    if not parts:
        print('Chưa có cụm nào để ghép.'); return
    lst = os.path.join(OUTDIR, '_concat.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace('\\', '/'))
    out = os.path.join(OUTDIR, 'phapbao-full.mp4')
    subprocess.run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out],
                   check=True, capture_output=True)
    print('XONG ghép full →', out, '(%d cụm)' % len(parts))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', default='1', help='1|2|3|all')
    ap.add_argument('--audio', action='store_true', help='chỉ dựng lại tiếng (dùng khung cũ)')
    ap.add_argument('--concat', action='store_true', help='ghép 3 cụm → phapbao-full.mp4')
    a = ap.parse_args()
    if a.concat:
        concat_all()
    elif a.part == 'all':
        for p in (1, 2, 3):
            render_part(p, audio_only=a.audio)
        concat_all()
    else:
        render_part(int(a.part), audio_only=a.audio)
