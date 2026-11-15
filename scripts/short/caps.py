from PIL import Image, ImageDraw, ImageFont
import json, textwrap, re, cairosvg
F=lambda n,s: ImageFont.truetype(f'fonts/{n}.ttf', s)
fsub=F('BeVietnamPro-SemiBold',54); ftop=F('BeVietnamPro-Medium',38); ftitle=F('PlayfairDisplay-ExtraBold',96)
SC=[
 ("s1","NGƯỢC DÒNG SỬ VIỆT",[("Hàng nghìn cọc nhọn giấu dưới mặt sông…",2.2),("…đã đổi vận mệnh cả dân tộc.",2.2)]),
 ("s2","NĂM 938",[("Quân Nam Hán do Lưu Hoằng Tháo chỉ huy",4.15),("theo đường biển tiến vào nước ta.",2.1)]),
 ("s3","CỬA SÔNG BẠCH ĐẰNG",[("Ngô Quyền cho quân đẽo cọc gỗ, đầu bịt sắt,",3.13),("đóng ngầm ở cửa sông Bạch Đằng.",2.22)]),
 ("s4","NƯỚC TRIỀU LÊN",[("Nước triều lên, bãi cọc chìm hẳn.",2.62),("Thuyền nhẹ của ta khiêu chiến, rồi giả thua, nhử giặc vào sâu.",4.08)]),
 ("s5","NƯỚC TRIỀU RÚT",[("Nước triều rút. Hàng cọc nhô lên.",2.76),("Thuyền giặc to nặng đâm vào cọc, vỡ và đắm.",2.69),("Hoằng Tháo tử trận.",1.65)]),
 ("s6","BÀI HỌC CON NƯỚC",[("Kế ấy dựa vào hiểu biết con nước của chính người dân Bạch Đằng.",3.53),("350 năm sau, Trần Hưng Đạo dùng lại đúng cách này.",3.97)]),
 ("s7","938",[("Chiến thắng ấy khép lại hơn một nghìn năm Bắc thuộc.",3.6)]),
]
def cap(top, sub, fn):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    tw=d.textlength(top,font=ftop)+ (len(top)*6)
    # top label with letterspacing
    x=(1080-tw)/2; 
    for ch in top:
        d.text((x,250),ch,font=ftop,fill=(233,196,110,255)); x+=d.textlength(ch,font=ftop)+6
    d.line([(440,310),(640,310)],fill=(179,38,30,255),width=4)
    if sub:
        lines=textwrap.wrap(sub,width=28)
        lh=74; total=lh*len(lines)+40; y0=1470
        d.rounded_rectangle([70,y0-20,1010,y0-20+total],radius=24,fill=(10,8,6,170))
        for i,l in enumerate(lines):
            w=d.textlength(l,font=fsub); d.text(((1080-w)/2,y0+i*lh),l,font=fsub,fill=(245,235,215,255))
    im.save(fn)
plan=[]
for sid,top,subs in SC:
    parts=[]
    for j,(t,dur) in enumerate(subs):
        fn=f'png/{sid}_c{j}.png'; cap(top,t,fn); parts.append((fn,dur))
    plan.append((sid,parts))
# end card
import re as _re
html=open('assets/brand/design-canvas/AvatarV2.dc.html').read()
svg=_re.search(r'<svg.*?</svg>',html,_re.S).group(0).replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1)
cairosvg.svg2png(bytestring=svg.encode(),write_to='png/emblem.png',output_width=560,output_height=560)
im=Image.new('RGBA',(1080,1920),(20,17,15,255)); d=ImageDraw.Draw(im)
em=Image.open('png/emblem.png'); im.alpha_composite(em,(260,330))
def ctext(y,t,f,col):
    w=d.textlength(t,font=f); d.text(((1080-w)/2,y),t,font=f,fill=col)
ctext(960,"Ngược Dòng Sử Việt",ftitle,(242,230,204,255))
ctext(1110,"CHẶNG SAU",ftop,(233,196,110,255))
ctext(1175,"Sau Bạch Đằng, Ngô Quyền làm gì?",F("BeVietnamPro-SemiBold",50),(245,235,215,255))
ctext(1330,"Theo dõi để ngược dòng tiếp",ftop,(201,145,94,255))
im.convert('RGB').save('png/s8_end.png')
plan.append(("s8",[("png/s8_end.png",6.1)]))
json.dump(plan,open('plan.json','w'),ensure_ascii=False)
print(sum(d for _,p in plan for _,d in p))
