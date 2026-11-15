import math, random, cairosvg
W,H=1296,2304
random.seed(4)
def sky(top,bot):
    return f'<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient><linearGradient id="wt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A3A44"/><stop offset="1" stop-color="#0E161C"/></linearGradient></defs><rect width="{W}" height="{H}" fill="url(#sk)"/>'
def sun(x,y,r,col="#E8B65A",op=0.9):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="{op}"/>'
def hills(y,col,amp=60,seed=1):
    random.seed(seed); pts=[f"0,{H}",f"0,{y}"]
    for i in range(0,W+80,80): pts.append(f"{i},{y-random.randint(0,amp)}")
    pts.append(f"{W},{H}"); return f'<polygon points="{" ".join(pts)}" fill="{col}"/>'
def water(y):
    s=f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="url(#wt)"/>'
    for i in range(40):
        yy=y+20+i*28; x=random.randint(-100,W)
        s+=f'<line x1="{x}" y1="{yy}" x2="{x+random.randint(80,260)}" y2="{yy}" stroke="#C9915E" stroke-width="3" opacity="{0.12+0.2*random.random():.2f}"/>'
    return s
def stake(x,base,top,w=26):
    return (f'<polygon points="{x-w/2},{base} {x+w/2},{base} {x+w/2},{top+40} {x},{top} {x-w/2},{top+40}" fill="#4A3020" stroke="#1A0F08" stroke-width="3"/>'
            f'<polygon points="{x-w/2+2},{top+40} {x},{top} {x+w/2-2},{top+40}" fill="#9AA3A8"/>')
def stakes_row(base,top,n=14,x0=60,x1=None,jit=30,w=26):
    x1=x1 or W-60; s=""
    for i in range(n):
        x=x0+(x1-x0)*i/(n-1)+random.randint(-15,15)
        s+=stake(x,base,top+random.randint(-jit,jit),w)
    return s
def junk(x,y,sc=1.0,tilt=0,col="#1B1310"):
    return (f'<g transform="translate({x} {y}) rotate({tilt}) scale({sc})">'
      f'<path d="M-170,0 L170,0 L130,60 L-140,60 Z" fill="{col}"/>'
      f'<rect x="-170" y="-20" width="40" height="22" fill="{col}"/><rect x="130" y="-30" width="45" height="32" fill="{col}"/>'
      f'<line x1="-40" y1="0" x2="-40" y2="-260" stroke="{col}" stroke-width="8"/><line x1="70" y1="0" x2="70" y2="-200" stroke="{col}" stroke-width="7"/>'
      f'<path d="M-40,-250 L60,-240 L40,-20 L-40,-20 Z" fill="{col}" opacity="0.92"/>'
      f'<path d="M70,-195 L150,-185 L135,-25 L70,-25 Z" fill="{col}" opacity="0.92"/>'
      + "".join(f'<line x1="-40" y1="{-230+k*45}" x2="{55-k*3}" y2="{-222+k*45}" stroke="#5A3A20" stroke-width="3"/>' for k in range(5))
      + '</g>')
def canoe(x,y,sc=1.0,col="#1B1310"):
    s=f'<g transform="translate({x} {y}) scale({sc})"><path d="M-110,0 Q0,30 110,0 L95,18 Q0,40 -95,18 Z" fill="{col}"/>'
    for k in range(4):
        px=-60+k*40; s+=f'<circle cx="{px}" cy="-28" r="9" fill="{col}"/><rect x="{px-6}" y="-20" width="12" height="22" fill="{col}"/><line x1="{px}" y1="-5" x2="{px-30}" y2="30" stroke="{col}" stroke-width="4"/>'
    return s+'</g>'
def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'
S={}
# 1 hook: underwater stakes, dark
b=sky("#0B1014","#16222A")+water(700)
b+=f'<rect x="0" y="700" width="{W}" height="8" fill="#C9915E" opacity="0.5"/>'
b+=stakes_row(2304,1250,n=12,jit=60,w=34)
b+=f'<rect x="0" y="700" width="{W}" height="{H-700}" fill="#0E161C" opacity="0.35"/>'
S['s1']=b
# 2 fleet from sea at dusk
b=sky("#3A2418","#C27A3E")+sun(900,820,170)+hills(1050,"#2A1A12",50,2)+water(1050)
b+=junk(380,1180,0.9)+junk(820,1120,0.7)+junk(1100,1090,0.5)+junk(200,1080,0.45)
S['s2']=b
# 3 stakes prepared: low tide, men driving stakes
b=sky("#5A3A26","#B07A48")+hills(1100,"#3A2618",80,3)+water(1250)
b+=stakes_row(1700,1150,n=10,jit=50,w=36)
for x in (300,700,1000):
    b+=f'<g fill="#1B1310"><circle cx="{x}" cy="1180" r="22"/><rect x="{x-16}" y="1200" width="32" height="90"/><line x1="{x}" y1="1215" x2="{x+60}" y2="1120" stroke="#1B1310" stroke-width="10"/><rect x="{x+40}" y="1090" width="60" height="34"/></g>'
S['s3']=b
# 4 high tide, stakes hidden, canoes lure ships
b=sky("#2A2A3A","#6A5A6A")+hills(1000,"#1E1A22",60,4)+water(1000)
b+=stakes_row(2304,1500,n=12,jit=40,w=30)
b+=f'<rect x="0" y="1000" width="{W}" height="{H-1000}" fill="#0E161C" opacity="0.55"/>'
b+=canoe(350,1080,1.1)+canoe(560,1110,0.9)+junk(980,1060,0.75)+junk(1220,1030,0.5)
S['s4']=b
# 5 tide recedes, ships crash on stakes, fire
b=sky("#3A1810","#C4502A")+hills(1050,"#2A120C",70,5)+water(1300)
b+=stakes_row(1700,1140,n=13,jit=60,w=34)
b+=junk(420,1230,0.95,-14)+junk(930,1210,0.8,11)
for x,y in [(420,980),(930,1000),(640,1060)]:
    b+=f'<ellipse cx="{x}" cy="{y}" rx="70" ry="120" fill="#E8762A" opacity="0.55"/><ellipse cx="{x}" cy="{y+30}" rx="40" ry="80" fill="#F3C25A" opacity="0.7"/>'
S['s5']=b
# 6 locals & 1288 echo: two timelines, riverbank villagers looking at tide
b=sky("#1E1712","#4A3424")+water(1400)
b+=f'<circle cx="648" cy="900" r="330" fill="none" stroke="#C9915E" stroke-width="6" opacity="0.6"/><circle cx="648" cy="900" r="300" fill="none" stroke="#C9915E" stroke-width="2" opacity="0.5" stroke-dasharray="6 12"/>'
b+=stakes_row(1650,1330,n=9,jit=30,w=30)
for x in (250,420,1000):
    b+=f'<g fill="#120D0A"><path d="M{x-45},1220 L{x},1170 L{x+45},1220 Z"/><circle cx="{x}" cy="1235" r="18"/><rect x="{x-18}" y="1250" width="36" height="110"/></g>'
S['s6']=b
# 7 dawn, independence: sunrise over river, canoes
b=sky("#2A1A12","#E8A84A")+sun(648,1000,230,"#F3D27A",0.95)+hills(1080,"#2A1A12",50,7)+water(1080)
b+=f'<rect x="548" y="1100" width="200" height="600" fill="#F3D27A" opacity="0.18"/>'
b+=canoe(380,1150,1.0)+canoe(900,1170,0.9)
S['s7']=b
# 8 end card bg
b=f'<rect width="{W}" height="{H}" fill="#14110F"/>'
S['s8']=b
for k,v in S.items():
    open(f'svg/{k}.svg','w').write(svg(v))
    cairosvg.svg2png(bytestring=svg(v).encode(), write_to=f'png/{k}.png')
print("ok")
