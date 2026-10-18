"""Original deterministic material maps, not downloaded images or product photos."""
import numpy as np
from PIL import Image
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
rng=np.random.default_rng(582)
n=512
yy,xx=np.mgrid[0:n,0:n].astype(float)/n
def save(name,a):
    Image.fromarray(np.clip(a*255,0,255).astype(np.uint8),'RGB').save(ROOT+'/'+name+'.png')
def normals(height,strength=1):
    dy,dx=np.gradient(height)
    norm=np.stack([-dx*strength,-dy*strength,np.ones_like(dx)],axis=-1)
    norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
    return norm*.5+.5
warp=.035*np.sin(2*np.pi*yy*2)+.015*np.sin(2*np.pi*yy*5)
phase=(xx+warp)*2*np.pi*40
grain=.5+.5*np.sin(phase+.2*np.sin(xx*2*np.pi*8))
grain=grain**4
coarse=.5+.5*np.sin((xx+.01*np.sin(yy*2*np.pi*3))*2*np.pi*7)
value=.35+.3*grain+.16*coarse+.045*rng.normal(size=(n,n))
wood=np.stack([.26+.40*value,.12+.25*value,.045+.12*value],axis=-1)
save('oak_basecolor',wood)
save('oak_normal',normals(grain,1.5))
threads=np.sin(xx*2*np.pi*128)*np.sin(yy*2*np.pi*128)
height=.5+.22*threads+.1*rng.normal(size=(n,n))
save('velvet_normal',normals(height,.8))
fuzz=.82+.18*rng.random((n,n))+.04*threads
blue=np.stack([.04*fuzz,.105*fuzz,.14*fuzz],axis=-1)
save('velvet_basecolor',blue)
