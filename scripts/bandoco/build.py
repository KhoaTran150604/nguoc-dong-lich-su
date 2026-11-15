import json, math, random, base64, io
import numpy as np
from PIL import Image, ImageFilter
from shapely.geometry import shape, box, Polygon, MultiPolygon
from shapely.ops import unary_union
import cairosvg
random.seed(7); np.random.seed(7)
W,H=1080,1920; FPS=30; DUR=15.0
COS=math.cos(math.radians(21))
LON0,LAT0,S0=102.0,26.5,260.0      # base projection
def pj(lon,lat): return ((lon-LON0)*COS*S0,(LAT0-lat)*S0)
reg=json.load(open('data/region.json'))
VIEW=box(101.5,15.5,118.5,27.5)
def proj_geom(g):
    def ring(c): return [pj(x,y) for x,y in c]
    polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
    return MultiPolygon([Polygon(ring(p.exterior.coords),[ring(i.coords) for i in p.interiors]) for p in polys if not p.is_empty])
land={k:shape(v).intersection(VIEW) for k,v in reg.items()}
allland=unary_union(list(land.values()))
LANDP=proj_geom(allland).buffer(0)
def d_of(g):
    polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
    out=[]
    for p in polys:
        if p.is_empty: continue
        out.append("M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in p.exterior.coords)+" Z")
        for i in p.interiors: out.append("M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in i.coords)+" Z")
    return " ".join(out)
# territories (minh họa)
viet=proj_geom(land['704'].intersection(box(102,17.8,110,23.5)))
NH=Polygon([(104.6,22.8),(105.6,24.0),(107.3,25.3),(110.3,26.0),(113.6,25.6),(116.0,24.7),(117.4,23.9),(117.4,21),(111.6,17.6),(108.4,17.6),(108.0,21.4),(106.9,21.6)])
namhan=proj_geom(land['156'].intersection(NH))
MW,MH=pj(118.5,15.5)
# parchment texture
def texture(w,h,base,var,seed):
    rng=np.random.default_rng(seed)
    n=rng.random((h//8+1,w//8+1)); im=Image.fromarray((n*255).astype('uint8')).resize((w,h),Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
    a=np.asarray(im).astype(float)/255
    rgb=np.stack([np.clip(base[i]+(a-0.5)*var,0,255) for i in range(3)],-1).astype('uint8')
    buf=io.BytesIO(); Image.fromarray(rgb).save(buf,'JPEG',quality=80); return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()
tw,th=int(MW/2),int(MH/2)
SEA_TX=texture(tw,th,(92,128,140),60,1)
LAND_TX=texture(tw,th,(212,184,138),55,2)
parts=[]
parts.append(f'<defs><clipPath id="landclip"><path d="{d_of(LANDP)}"/></clipPath></defs>')
parts.append(f'<image href="{SEA_TX}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none"/>')
# coastal wave rings
for i,dist in enumerate([60,38,20]):
    ring=LANDP.buffer(dist).difference(LANDP.buffer(dist-5))
    parts.append(f'<path d="{d_of(ring)}" fill="#B8D2D8" opacity="{0.25+0.15*i:.2f}"/>')
parts.append(f'<path d="{d_of(LANDP.buffer(8))}" fill="#E4D5B0" opacity="0.8"/>')
parts.append(f'<image href="{LAND_TX}" x="0" y="0" width="{MW:.0f}" height="{MH:.0f}" preserveAspectRatio="none" clip-path="url(#landclip)"/>')
parts.append(f'<path d="{d_of(viet)}" fill="#D9B44A" opacity="0.55"/>')
parts.append(f'<path d="{d_of(namhan)}" fill="#B5503A" opacity="0.45"/>')
parts.append(f'<path d="{d_of(LANDP)}" fill="none" stroke="#5A3A20" stroke-width="5"/>')
# rivers (approx): Sông Hồng, Bạch Đằng
for pts in [[(103.6,22.6),(104.6,21.9),(105.3,21.3),(105.9,20.9),(106.5,20.3)],[(106.4,21.2),(106.7,20.95),(106.82,20.86)]]:
    d="M"+" L".join(f"{pj(*p)[0]:.1f},{pj(*p)[1]:.1f}" for p in pts)
    parts.append(f'<path d="{d}" fill="none" stroke="#6E98A6" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
# mountains & trees
def mountain(x,y,s):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><polygon points="-40,20 0,-34 40,20" fill="#A88A62" stroke="#5A3A20" stroke-width="3"/>'
            f'<polygon points="0,-34 40,20 8,20" fill="#7A5E40"/><polygon points="-10,-20 0,-34 10,-20 4,-16 -4,-18" fill="#F2E6CC"/></g>')
def tree(x,y): return f'<g transform="translate({x:.0f} {y:.0f})"><line x1="0" y1="0" x2="0" y2="14" stroke="#4A3220" stroke-width="3"/><circle cx="0" cy="-4" r="10" fill="#5E7A44"/></g>'
inner=LANDP.buffer(-60)
cnt=0
while cnt<170:
    lon=random.uniform(102,117.5); lat=random.uniform(17,26.5); x,y=pj(lon,lat)
    from shapely.geometry import Point
    if inner.contains(Point(x,y)):
        parts.append(mountain(x,y,random.uniform(0.7,1.2)) if random.random()<0.6 else tree(x,y)); cnt+=1
def label(lon,lat,t,size,col="#2A1A10",font="Playfair Display",ls=4):
    x,y=pj(lon,lat); return f'<text x="{x:.0f}" y="{y:.0f}" font-family="{font}" font-weight="800" font-size="{size}" fill="{col}" text-anchor="middle" letter-spacing="{ls}">{t}</text>'
parts.append(label(104.4,22.7,"TĨNH HẢI QUÂN",60))
parts.append(label(112.0,24.4,"NAM HÁN",72))
parts.append(label(113.3,18.6,"BIỂN ĐÔNG",62,"#E8EEF0"))
def city(lon,lat,name):
    x,y=pj(lon,lat)
    return (f'<g transform="translate({x:.0f} {y:.0f})"><rect x="-22" y="-18" width="44" height="26" fill="#C8A878" stroke="#3A2618" stroke-width="3"/>'
            f'<polygon points="-26,-18 0,-38 26,-18" fill="#8A3A24" stroke="#3A2618" stroke-width="3"/></g>'
            f'<text x="{x:.0f}" y="{y+46:.0f}" font-family="Playfair Display" font-weight="800" font-size="34" fill="#2A1A10" text-anchor="middle">{name}</text>')
parts.append(city(105.85,21.03,"Đại La"))
parts.append(city(105.75,19.85,"Ái Châu"))
parts.append(city(113.26,23.13,"Hưng Vương"))
x,y=pj(106.9,20.75); parts.append(f'<text x="{x+20:.0f}" y="{y+70:.0f}" font-family="Playfair Display" font-weight="800" font-size="30" fill="#1E3A44" text-anchor="middle">Cửa Bạch Đằng</text>')
MAP="".join(parts)
open('map_static.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{MW:.0f}" height="{MH:.0f}">{MAP}</svg>')
json.dump({"MW":MW,"MH":MH},open('meta.json','w'))
open('map_body.txt','w').write(MAP)
print(MW,MH)
