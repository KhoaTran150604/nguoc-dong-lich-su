import math, cairosvg, sys

W,H=1080,1920; FPS=30; DUR=14.0
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def seg(t,a,b): return ease((t-a)/(b-a))
def lerp(a,b,u): return a+(b-a)*u
BED=1520            # đáy sông
def junk(x,y,sc,tilt,op=1):
    col="#2A1A12"
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt:.1f}) scale({sc})" opacity="{op:.2f}">'
      f'<path d="M-150,0 L150,0 L115,55 L-125,55 Z" fill="{col}"/>'
      f'<line x1="-30" y1="0" x2="-30" y2="-230" stroke="{col}" stroke-width="8"/><line x1="60" y1="0" x2="60" y2="-180" stroke="{col}" stroke-width="7"/>'
      f'<path d="M-30,-222 L55,-214 L38,-18 L-30,-18 Z" fill="#B3261E"/><path d="M60,-175 L130,-166 L118,-22 L60,-22 Z" fill="#B3261E"/>'
      + "".join(f'<line x1="-30" y1="{-200+k*42}" x2="{50-k*3}" y2="{-193+k*42}" stroke="#5A1A12" stroke-width="3"/>' for k in range(5))+'</g>')
def canoe(x,y,sc):
    col="#14110F"; s=f'<g transform="translate({x:.1f} {y:.1f}) scale({sc})"><path d="M-100,0 Q0,28 100,0 L86,16 Q0,36 -86,16 Z" fill="{col}"/>'
    for k in range(4):
        px=-55+k*36; s+=f'<circle cx="{px}" cy="-26" r="8" fill="{col}"/><rect x="{px-5}" y="-19" width="10" height="20" fill="{col}"/><line x1="{px}" y1="-4" x2="{px+28}" y2="28" stroke="{col}" stroke-width="4"/>'
    return s+'</g>'
STAKES=[230+i*115 for i in range(6)]
def stake(x,top):
    return (f'<polygon points="{x-22},{BED} {x+22},{BED} {x+22},{top+50} {x},{top} {x-22},{top+50}" fill="#5A3A22" stroke="#1A0F08" stroke-width="3"/>'
            f'<polygon points="{x-20},{top+50} {x},{top} {x+20},{top+50}" fill="#B8C0C4"/>')
def frame(t):
    # water level: high (stakes hidden) 0-7.5s, then falls
    wl=lerp(860,1230,seg(t,7.5,9.5))
    # sky color warms as battle
    b=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1E1A"/><stop offset="1" stop-color="#8A5A3A"/></linearGradient><linearGradient id="wt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2F5468" stop-opacity="0.92"/><stop offset="1" stop-color="#132430" stop-opacity="0.97"/></linearGradient></defs>',
       f'<rect width="{W}" height="{H}" fill="url(#sk)"/>',
       f'<polygon points="0,840 160,780 330,820 520,770 700,815 880,780 1080,820 1080,{H} 0,{H}" fill="#3A2618"/>',
       f'<rect x="0" y="{BED}" width="{W}" height="{H-BED}" fill="#3A2A1C"/>']
    for x in STAKES: b.append(stake(x,1040+((x*37)%50)))
    # boats float at waterline
    # canoes: start mid-right, lure left (5.0-8s), then turn aside to bank
    cx=lerp(700,170,seg(t,2.5,7.0)); b.append(canoe(cx,wl-16,1.6)); b.append(canoe(cx+250,wl-12,1.35))
    # junks chase from right
    sink=seg(t,10.0,12.5)
    for k,(x0,x1) in enumerate([(1350,470),(1700,830)]):
        x=lerp(x0,x1,seg(t,3.2,9.8))
        y=wl-50+ (0 if t<9.8 else sink*170)
        tilt=(-1 if k==0 else 1)*14*sink
        op=1-0.6*sink
        b.append(junk(x,y,1.25 if k==0 else 1.05,tilt,op))
    b.append(f'<rect x="0" y="{wl:.1f}" width="{W}" height="{BED-wl:.1f}" fill="url(#wt)"/>')
    b.append(f'<line x1="0" y1="{wl:.1f}" x2="{W}" y2="{wl:.1f}" stroke="#C9E0EA" stroke-width="4" opacity="0.6"/>')
    # fire/splash on impact
    if t>9.8:
        a=seg(t,9.8,10.4)*(1-seg(t,12.6,13.6))
        for x in (470,830):
            b.append(f'<ellipse cx="{x}" cy="{wl-230:.0f}" rx="100" ry="170" fill="#E8762A" opacity="{0.6*a:.2f}"/><ellipse cx="{x}" cy="{wl-190:.0f}" rx="55" ry="105" fill="#F3C25A" opacity="{0.8*a:.2f}"/>')
    # tide arrow indicator
    lab = "NƯỚC TRIỀU LÊN · CỌC CHÌM DƯỚI NƯỚC" if t<7.5 else ("NƯỚC TRIỀU RÚT" if t<9.8 else "THUYỀN GIẶC ĐÂM VÀO CỌC")
    if t<2.5: lab="SÔNG BẠCH ĐẰNG, NĂM 938"
    elif t<5.0 and t>=2.5: lab="THUYỀN NHẸ CỦA TA RA KHIÊU CHIẾN"
    elif t<7.5: lab="GIẢ THUA, NHỬ GIẶC VÀO SÂU"
    b.append(f'<rect x="70" y="200" width="940" height="110" rx="20" fill="#14110F" opacity="0.85"/>')
    b.append(f'<text x="540" y="272" font-family="Be Vietnam Pro SemiBold" font-size="40" fill="#F3D27A" text-anchor="middle">{lab}</text>')
    # mực nước gauge
    b.append(f'<rect x="1010" y="840" width="22" height="680" rx="11" fill="#14110F" opacity="0.6"/><rect x="1010" y="{wl:.1f}" width="22" height="{BED-wl:.1f}" rx="11" fill="#3A7CA5"/>')
    b.append(f'<text x="960" y="820" font-family="Be Vietnam Pro SemiBold" font-size="26" fill="#C9E0EA" text-anchor="middle">Mực nước</text>')
    b.append('</svg>'); return "".join(b)
for i in range(int(DUR*FPS)):
    cairosvg.svg2png(bytestring=frame(i/FPS).encode(), write_to=f'frames/{i:04d}.png')
