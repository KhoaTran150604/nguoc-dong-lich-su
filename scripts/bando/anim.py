import json, math, cairosvg, os
g=json.load(open('data/vn.json'))
W,H=1080,1920; FPS=30; DUR=13.0
COS=math.cos(math.radians(16))
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def seg(t,a,b): return ease((t-a)/(b-a))
def lerp(a,b,u): return a+(b-a)*u
# camera: center lon/lat and px-per-degree
CAM0=(108.0,16.0,80); CAM1=(107.35,20.55,520)
EST=(106.82,20.86)   # cửa sông Bạch Đằng (xấp xỉ)
SEA=(108.6,20.05)
def cam(t):
    u=seg(t,2.0,4.0); return (lerp(CAM0[0],CAM1[0],u),lerp(CAM0[1],CAM1[1],u),CAM0[2]*((CAM1[2]/CAM0[2])**u))
def P(lon,lat,c):
    cx,cy,s=c; return W/2+(lon-cx)*COS*s, H*0.46-(lat-cy)*s
def path_d(c):
    out=[]
    for poly in g['coordinates']:
        out.append("M"+" L".join(f"{P(lo,la,c)[0]:.1f},{P(lo,la,c)[1]:.1f}" for lo,la in poly[0])+" Z")
    return " ".join(out)
def text(x,y,s,size,col,anchor="middle",w=600,op=1):
    return f'<text x="{x}" y="{y}" font-family="Be Vietnam Pro SemiBold" font-size="{size}" fill="{col}" text-anchor="{anchor}" opacity="{op:.2f}">{s}</text>'
random_stakes=[(0.00,0.00),(0.04,0.03),(-0.03,0.04),(0.06,-0.02),(-0.05,-0.01),(0.02,-0.05),(0.08,0.05),(-0.07,0.05),(0.1,0.0),(0.0,0.08),(-0.02,-0.08),(0.05,0.09)]
def frame(t):
    c=cam(t)
    b=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#16222A"/>']
    # sea grid lines for depth
    b.append(f'<path d="{path_d(c)}" fill="#C9A24A" stroke="#5A3A14" stroke-width="2"/>')
    for (lo,la),pts_ in [((112.0,16.5),[(0,0),(0.5,0.35),(-0.4,0.45)]),((113.6,9.6),[(0,0),(0.6,0.4),(-0.5,0.5),(0.2,-0.5)])]:
        for dx,dy in pts_:
            x,y=P(lo+dx,la+dy,c); b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(3,c[2]*0.06):.1f}" fill="#C9A24A"/>')
    if t<2.0:
        x,y=P(112.0,17.3,c); b.append(text(x,y,"Hoàng Sa",26,"#C9A24A"))
        x,y=P(113.6,10.5,c); b.append(text(x,y,"Trường Sa",26,"#C9A24A"))
    # enemy arrow
    u=seg(t,4.3,6.6)
    if u>0:
        x0,y0=P(*SEA,c); x1,y1=P(*EST,c)
        cxm,cym=(x0+x1)/2+60,(y0+y1)/2+160
        # quadratic bezier sampled to u
        pts=[]
        for i in range(41):
            v=u*i/40; bx=(1-v)**2*x0+2*(1-v)*v*cxm+v*v*x1; by=(1-v)**2*y0+2*(1-v)*v*cym+v*v*y1; pts.append((bx,by))
        b.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="#D3302A" stroke-width="16" stroke-linecap="round" stroke-dasharray="1 0"/>')
        hx,hy=pts[-1]; px,py=pts[-3]; ang=math.degrees(math.atan2(hy-py,hx-px))
        sink=seg(t,10.2,11.2)
        if t<10.2:
            b.append(f'<polygon points="0,-26 50,0 0,26" fill="#D3302A" transform="translate({hx:.1f} {hy:.1f}) rotate({ang:.1f})"/>')
        # enemy ships following
        for k,off in enumerate([0.0,0.12,0.24]):
            v=max(0,u-off)
            if v<=0: continue
            bx=(1-v)**2*x0+2*(1-v)*v*cxm+v*v*x1; by=(1-v)**2*y0+2*(1-v)*v*cym+v*v*y1
            op=1-sink
            b.append(f'<g transform="translate({bx+30:.1f} {by+40+k*10:.1f})" opacity="{op:.2f}"><path d="M-28,0 L28,0 L20,12 L-22,12 Z" fill="#D3302A" stroke="#F2E6CC" stroke-width="2"/><path d="M-4,0 L-4,-34 L16,-28 L16,-4 Z" fill="#D3302A" stroke="#F2E6CC" stroke-width="2"/></g>')
            if sink>0:
                b.append(f'<g transform="translate({bx+30:.1f} {by+40+k*10:.1f})" opacity="{sink:.2f}"><line x1="-20" y1="-20" x2="20" y2="20" stroke="#F3D27A" stroke-width="8"/><line x1="20" y1="-20" x2="-20" y2="20" stroke="#F3D27A" stroke-width="8"/></g>')
    # stakes
    us=seg(t,6.8,7.8)
    if us>0:
        ex,ey=P(*EST,c)
        for i,(dx,dy) in enumerate(random_stakes):
            a=max(0,min(1,us*len(random_stakes)-i))
            x,y=P(EST[0]+dx,EST[1]+dy,c)
            b.append(f'<g opacity="{a:.2f}"><polygon points="{x:.1f},{y-16:.1f} {x+8:.1f},{y+10:.1f} {x-8:.1f},{y+10:.1f}" fill="#F2E6CC" stroke="#14110F" stroke-width="2"/></g>')
    # tide overlay
    tide=seg(t,8.0,8.8)-seg(t,9.6,10.3)
    if tide>0:
        ex,ey=P(*EST,c)
        b.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{120:.0f}" ry="{110:.0f}" fill="#3A7CA5" opacity="{0.85*tide:.2f}"/>')
    # labels
    top=""
    if t<2.0: top="VIỆT NAM NGÀY NAY"
    elif t<4.0: top="NGƯỢC VỀ NĂM 938 · CỬA SÔNG BẠCH ĐẰNG"
    elif t<6.8: top="QUÂN NAM HÁN TIẾN VÀO TỪ BIỂN"
    elif t<8.0: top="BÃI CỌC NGẦM Ở CỬA SÔNG"
    elif t<9.8: top="NƯỚC TRIỀU LÊN · CỌC CHÌM"
    elif t<11.4: top="NƯỚC TRIỀU RÚT · THUYỀN GIẶC MẮC CỌC"
    else: top="THẮNG LỢI BẠCH ĐẰNG 938"
    b.append(f'<rect x="80" y="160" width="920" height="110" rx="20" fill="#14110F" opacity="0.85"/>')
    b.append(text(540,232,top,40,"#F3D27A"))
    if t>=6.8:
        ex,ey=P(*EST,c); b.append(text(ex-150,ey-120,"Bạch Đằng",38,"#F2E6CC"))
    # legend
    b.append(f'<rect x="80" y="1560" width="920" height="170" rx="20" fill="#14110F" opacity="0.8"/>')
    b.append(f'<line x1="130" y1="1615" x2="210" y2="1615" stroke="#D3302A" stroke-width="12"/>'+text(240,1628,"Quân Nam Hán",36,"#F2E6CC","start"))
    b.append(f'<polygon points="170,1648 180,1682 160,1682" fill="#F2E6CC"/>'+text(240,1682,"Bãi cọc ngầm",36,"#F2E6CC","start"))
    b.append(f'<ellipse cx="760" cy="1615" rx="34" ry="20" fill="#3A7CA5"/>'+text(810,1628,"Triều lên",36,"#F2E6CC","start"))
    b.append(text(540,1840,"Bản đồ minh họa, vị trí gần đúng",28,"#8A7A66"))
    b.append('</svg>')
    fade=min(1,t/0.4,(DUR-t)/0.4)
    return "".join(b), fade
n=int(DUR*FPS)
for i in range(n):
    s,f=frame(i/FPS)
    cairosvg.svg2png(bytestring=s.encode(), write_to=f'frames/{i:04d}.png')
