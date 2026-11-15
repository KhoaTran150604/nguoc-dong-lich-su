import math, io, cairosvg
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
W,H=1080,1920; FPS=30; DUR=15.0; R=1.8
COS=math.cos(math.radians(21)); LON0,LAT0,S0=102.0,26.5,260.0
def pj(lon,lat): return ((lon-LON0)*COS*S0,(LAT0-lat)*S0)
BIG=Image.open('map_big.png').convert('RGB')
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def seg(t,a,b): return ease((t-a)/(b-a))
def lerp(a,b,u): return a+(b-a)*u
WIDE=(109.3,21.6,0.5); CLOSE=(106.95,20.9,1.55); END=(107.2,21.0,1.15)
def cam(t):
    u=seg(t,6.0,7.6); v=seg(t,12.4,14.2)
    a=WIDE; b=CLOSE
    c=(lerp(a[0],b[0],u),lerp(a[1],b[1],u),a[2]*(b[2]/a[2])**u)
    if v>0: c=(lerp(c[0],END[0],v),lerp(c[1],END[1],v),c[2]*(END[2]/c[2])**v)
    return c
def to_screen(lon,lat,c):
    bx,by=pj(lon,lat); cx,cy=pj(c[0],c[1]); z=c[2]
    return W/2+(bx-cx)*z, H*0.52+(by-cy)*z
def path_at(pts,u):
    # piecewise linear on lon/lat list
    if u<=0: return pts[0]
    L=[math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)]; tot=sum(L); d=u*tot
    for i,l in enumerate(L):
        if d<=l: f=d/l; return (lerp(pts[i][0],pts[i+1][0],f),lerp(pts[i][1],pts[i+1][1],f))
        d-=l
    return pts[-1]
HAN=[(113.26,23.13),(112.6,21.7),(110.9,20.9),(109.2,20.6),(108.0,20.55),(107.4,20.68)]
NGO=[(105.85,21.03),(106.2,21.05),(106.55,21.02)]
HAN_END=(107.02,20.80)
STAKES=[(106.93,20.80),(106.97,20.86),(107.01,20.81),(106.95,20.89),(107.03,20.87),(106.99,20.77),(107.05,20.83),(106.91,20.85)]
def banner(x,y,name,col,dark,scale=1.0,tilt=0,op=1.0,glow=0):
    s=[f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt:.1f}) scale({scale:.2f})" opacity="{op:.2f}">']
    if glow>0: s.append(f'<circle cx="0" cy="-150" r="150" fill="#F3D27A" opacity="{0.35*glow:.2f}"/>')
    s.append('<ellipse cx="0" cy="4" rx="34" ry="10" fill="#000" opacity="0.35"/>')
    s.append('<line x1="0" y1="0" x2="0" y2="-300" stroke="#3A2618" stroke-width="8"/><polygon points="-9,-300 0,-326 9,-300" fill="#C8C8C8"/>')
    s.append('<line x1="-78" y1="-268" x2="78" y2="-268" stroke="#3A2618" stroke-width="7"/>')
    s.append(f'<rect x="-70" y="-266" width="140" height="190" fill="{col}" stroke="{dark}" stroke-width="5"/>')
    s.append(f'<rect x="-70" y="-266" width="140" height="40" fill="#F2E6CC" stroke="{dark}" stroke-width="4"/>')
    s.append(f'<text x="0" y="-238" font-family="Be Vietnam Pro SemiBold" font-size="22" fill="#2A1A10" text-anchor="middle">{name}</text>')
    # portrait placeholder: helmet silhouette
    s.append(f'<g transform="translate(0 -150)"><circle cx="0" cy="0" r="34" fill="{dark}"/><path d="M-40,-4 Q0,-62 40,-4 L32,-2 Q0,-46 -32,-2 Z" fill="{dark}"/><rect x="-46" y="34" width="92" height="36" rx="12" fill="{dark}"/></g>')
    s.append(f'<polygon points="-70,-76 70,-76 0,-56" fill="{col}" stroke="{dark}" stroke-width="4"/>')
    s.append('</g>'); return "".join(s)
def overlay(t,c):
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">']
    z=c[2]
    # trails
    uh=seg(t,2.5,6.0); un=seg(t,3.6,6.0)
    def trail(pts,u,col):
        n=40; pp=[to_screen(*path_at(pts,u*i/n),c) for i in range(n+1)]
        return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pp)}" fill="none" stroke="{col}" stroke-width="{max(5,7*z):.1f}" stroke-dasharray="{14*z+6:.0f} {10*z+5:.0f}" stroke-linecap="round" opacity="0.9"/>'
    if uh>0: o.append(trail(HAN,uh,"#9E2A1E"))
    if un>0: o.append(trail(NGO,un,"#8A6A1A"))
    # stakes
    us=seg(t,7.6,8.6)
    tide=seg(t,8.6,9.3)-seg(t,10.0,10.7)
    for i,p in enumerate(STAKES):
        a=max(0,min(1,us*len(STAKES)-i))
        if a<=0: continue
        x,y=to_screen(*p,c); s=1.0
        o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale(1.7)" opacity="{a*(1-0.75*tide):.2f}"><polygon points="-9,22 9,22 9,-8 0,-26 -9,-8" fill="#6A4428" stroke="#2A1A10" stroke-width="3"/><polygon points="-8,-8 0,-26 8,-8" fill="#C8CED2"/></g>')
    if tide>0:
        x,y=to_screen(106.98,20.83,c)
        o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{230:.0f}" ry="{170:.0f}" fill="#3A7CA5" opacity="{0.55*tide:.2f}"/>')
    # banners
    hp=path_at(HAN,uh)
    if t>10.3: hp=(lerp(hp[0],HAN_END[0],seg(t,10.3,11.0)),lerp(hp[1],HAN_END[1],seg(t,10.3,11.0)))
    np_=path_at(NGO,un)
    defeat=seg(t,11.0,11.6)
    hx,hy=to_screen(*hp,c); nx,ny=to_screen(*np_,c)
    sc=0.62 if z<1 else 0.75
    o.append(banner(hx,hy,"HOẰNG THÁO","#A8382A","#4A1410",sc,-18*defeat,1-0.45*defeat))
    if defeat>0:
        o.append(f'<g transform="translate({hx:.1f} {hy-110*sc:.1f})" opacity="{defeat:.2f}"><line x1="-90" y1="-90" x2="90" y2="90" stroke="#B3261E" stroke-width="26" stroke-linecap="round"/><line x1="90" y1="-90" x2="-90" y2="90" stroke="#B3261E" stroke-width="26" stroke-linecap="round"/></g>')
    win=seg(t,11.8,12.6)
    o.append(banner(nx,ny,"NGÔ QUYỀN","#D9B44A","#5A3A10",sc*(1+0.25*win),0,1,win))
    # top label
    if t<2.5: lab="NĂM 938"
    elif t<6.0: lab="NAM HÁN THEO ĐƯỜNG BIỂN TIẾN VÀO"
    elif t<7.6: lab="NGÔ QUYỀN CHẶN Ở CỬA BẠCH ĐẰNG"
    elif t<8.6: lab="ĐÓNG CỌC NGẦM DƯỚI LÒNG SÔNG"
    elif t<10.3: lab="NƯỚC TRIỀU LÊN · CỌC CHÌM"
    elif t<11.8: lab="NƯỚC RÚT · THUYỀN GIẶC MẮC CỌC"
    else: lab="NGÔ QUYỀN ĐẠI THẮNG"
    o.append(f'<rect x="70" y="150" width="940" height="110" rx="18" fill="#14110F" opacity="0.88" stroke="#C9A24A" stroke-width="3"/>')
    o.append(f'<text x="540" y="222" font-family="Be Vietnam Pro SemiBold" font-size="40" fill="#F3D27A" text-anchor="middle">{lab}</text>')
    o.append(f'<text x="540" y="1830" font-family="Be Vietnam Pro" font-size="26" fill="#C9B89A" text-anchor="middle">Bản đồ minh họa, ranh giới và vị trí gần đúng</text>')
    o.append('</svg>'); return "".join(o)
def frame(t):
    c=cam(t); z=c[2]
    cx,cy=pj(c[0],c[1])
    vw,vh=W/z,H/z; left=cx-vw/2; top=cy-vh*0.52
    box=(int(left*R),int(top*R),int((left+vw)*R),int((top+vh)*R))
    img=Image.new('RGB',(W,H),(20,17,15))
    crop=BIG.crop(box).resize((W,H),Image.BILINEAR)
    # mask outside map extents
    mw,mh=BIG.size
    x0=max(0,-box[0]); y0=max(0,-box[1]); x1=min(box[2]-box[0], mw-box[0]); y1=min(box[3]-box[1], mh-box[1])
    sx=W/(box[2]-box[0]); sy=H/(box[3]-box[1])
    region=(int(x0*sx),int(y0*sy),int(x1*sx),int(y1*sy))
    img.paste(crop.crop(region),region[:2])
    ov=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=overlay(t,c).encode()))).convert('RGBA')
    img=img.convert('RGBA'); img.alpha_composite(ov); return img.convert('RGB')
import sys
if len(sys.argv)>1:
    for t in map(float,sys.argv[1:]): frame(t).resize((360,640)).save(f'prev_{t}.jpg')
else:
    for i in range(int(DUR*FPS)): frame(i/FPS).save(f'frames/{i:04d}.jpg',quality=90)
