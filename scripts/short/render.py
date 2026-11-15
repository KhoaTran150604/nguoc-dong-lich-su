import json, subprocess, os
plan=json.load(open('plan.json'))
ENC=['-c:v','libx264','-crf','20','-preset','veryfast','-pix_fmt','yuv420p','-r','30']
files=[]
for sid,parts in plan:
    total=sum(d for _,d in parts); n=round(total*30)
    out=f'clips/{sid}.mp4'; tmp=f'clips/{sid}.tmp.mp4'
    if sid=='s8':
        cmd=['ffmpeg','-y','-loglevel','error','-framerate','30','-i',parts[0][0],'-vf',f'format=yuv420p,loop=-1:1,trim=duration={total},fade=t=in:st=0:d=0.4',*ENC,tmp]
    else:
        inputs=['-loop','1','-framerate','30','-t',str(total),'-i',f'png/{sid}.png']
        for fn,_ in parts: inputs+=['-i',fn]
        fc=f"[0:v]scale=2160:3840,zoompan=z='1+0.07*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30[bg];"
        t=0; last='bg'
        for i,(fn,d) in enumerate(parts):
            fc+=f"[{last}][{i+1}:v]overlay=0:0:enable='between(t,{t:.2f},{t+d-0.001:.2f})'[v{i}];"; last=f'v{i}'; t+=d
        fc+=f"[{last}]fade=t=in:st=0:d=0.35,fade=t=out:st={total-0.35:.2f}:d=0.35,trim=duration={total}[out]"
        cmd=['ffmpeg','-y','-loglevel','error',*inputs,'-filter_complex',fc,'-map','[out]',*ENC,tmp]
    subprocess.run(cmd,check=True); os.rename(tmp,out); files.append(out); print(sid,'ok')
open('list.txt','w').write("".join(f"file '{f}'\n" for f in files))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','list.txt','-c','copy','Short1-BachDang938-ban-nhap.mp4'],check=True)
