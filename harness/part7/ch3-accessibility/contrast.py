def lin(c):
    c/=255
    return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
def L(rgb):
    r,g,b=rgb; return .2126*lin(r)+.7152*lin(g)+.0722*lin(b)
def cr(a,b):
    la,lb=sorted((L(a),L(b)),reverse=True); return (la+.05)/(lb+.05)
over=lambda fg,a,bg: tuple(round(a*f+(1-a)*b) for f,b in zip(fg,bg))
hx=lambda s: tuple(int(s[i:i+2],16) for i in (1,3,5))
pages={'white':(255,255,255),'black':(0,0,0),'grey':(128,128,128),'red':(255,0,0)}
def run(name,glass,a,tones):
    print(name)
    for p,rgb in pages.items():
        g=over(glass,a,rgb)
        print(' ',p,[round(cr(hx(t),g),2) for t in tones])
run('dark .88',(22,28,44),.88,['#c4ccdf','#a9b3cc'])
run('light .88',(255,255,255),.88,['#3c4760','#4d5870'])
run('old dark .58',(22,28,44),.58,['#6f7a94'])
