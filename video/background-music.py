import numpy as np, wave, sys
sr=44100; dur=64.5; n=int(sr*dur); t=np.arange(n)/sr
rng=np.random.default_rng(7)
def midi(m): return 440*2**((m-69)/12)
# slow luxurious progression, 4 s per chord: Am9 - Fmaj7 - Cmaj7 - G6 ...
prog=[[45,57,60,64,71],[41,57,60,64,69],[48,55,59,64,67],[43,55,59,62,64]]
out=np.zeros(n); L=np.zeros(n); R=np.zeros(n)
cl=4.0
for ci in range(int(np.ceil(dur/cl))+1):
    ch=prog[ci%4]; st=ci*cl; s0=int(st*sr); s1=min(n,int((st+cl+2.0)*sr))
    if s0>=n: break
    tt=np.arange(s1-s0)/sr
    env=np.minimum(1,tt/1.6)*np.clip((cl+2.0-tt)/2.0,0,1)
    for k,m in enumerate(ch):
        f=midi(m)
        for det,pan in [(-0.12,0.2),(0.12,0.8)]:
            ph=rng.uniform(0,6.28)
            w=np.sin(2*np.pi*(f+det)*tt+ph)+0.3*np.sin(2*np.pi*2*(f+det)*tt+ph)+0.12*np.sin(2*np.pi*3*(f+det)*tt)
            a=(0.5 if k==0 else 0.22)*env*w
            L[s0:s1]+=a*(1-pan); R[s0:s1]+=a*pan
    # soft piano-like arpeggio notes
    arp=[ch[2]+12,ch[3]+12,ch[4]+12,ch[3]+12]
    for j,m in enumerate(arp):
        ns=st+j*1.0; a0=int(ns*sr)
        if a0>=n: continue
        a1=min(n,a0+int(3.5*sr)); tt=np.arange(a1-a0)/sr; f=midi(m)
        e=np.exp(-tt*1.6)*np.minimum(1,tt/0.008)
        w=(np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*3)+0.12*np.sin(2*np.pi*3*f*tt)*np.exp(-tt*5))*e*0.18
        pan=0.35+0.3*(j%2)
        L[a0:a1]+=w*(1-pan); R[a0:a1]+=w*pan
# simple reverb: multi-tap feedback delays
def rev(x):
    y=x.copy()
    for d,g in [(0.031,0.5),(0.047,0.45),(0.071,0.4),(0.113,0.35),(0.173,0.3),(0.257,0.25),(0.389,0.2)]:
        k=int(d*sr); y[k:]+=g*x[:-k]
    return y
L=rev(rev(L)*0.5); R=rev(rev(R)*0.5)
fade=np.minimum(1,t/2.5)*np.clip((dur-t)/3.0,0,1)
L*=fade; R*=fade
m=max(np.abs(L).max(),np.abs(R).max()); L/=m; R/=m
st=np.stack([L,R],1)*0.8
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
