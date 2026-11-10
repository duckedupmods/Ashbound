"""Finds parts of an armour piece that touch nothing else: every piece mesh split into its boxes, boxes that touch joined,
anything left over listed with where it sits (player pixels). Halos on abbot, acolyte, bellows and stormhelm float on purpose.

    python tools/armor_islands.py
"""
import json,sys,os
sys.path.insert(0,'E:/EFTest/game/tools')
import armoricons as A
R='E:/EFTest/game/src/main/resources/assets/ashbound/animmodels/armor/'
TOL=float(os.environ.get('TOL','0.02'))
def comps(path):
    d=json.load(open(path))['vertices']
    P=d['positions']['array']
    tris=[]
    for part in d['parts'].values():
        a=part['array']
        for t in range(0,len(a),9): tris.append((a[t],a[t+3],a[t+6]))
    par={}
    def f(x):
        while par.setdefault(x,x)!=x:
            par[x]=par[par[x]];x=par[x]
        return x
    key=lambda i:(round(P[3*i],4),round(P[3*i+1],4),round(P[3*i+2],4))
    for t in tris:
        for b in t[1:]: par[f(key(t[0]))]=f(key(b))
    box={}
    for k in list(par):
        r=f(k)
        b=box.setdefault(r,[list(k),list(k)])
        for i in range(3):
            b[0][i]=min(b[0][i],k[i]);b[1][i]=max(b[1][i],k[i])
    return list(box.values())
def groups(bs):
    n=len(bs);p=list(range(n))
    def f(x):
        while p[x]!=x:
            p[x]=p[p[x]];x=p[x]
        return x
    for i in range(n):
        for j in range(i):
            if all(bs[i][0][a]<=bs[j][1][a]+TOL and bs[j][0][a]<=bs[i][1][a]+TOL for a in range(3)):
                p[f(i)]=f(j)
    g={}
    for i in range(n): g.setdefault(f(i),[]).append(bs[i])
    return list(g.values())
ids=A.pieces();out={}
for s,items in ids.items():
    for it in items:
        g=groups(comps(R+it+'.json'))
        if len(g)>1:
            g.sort(key=lambda x:-len(x))
            out[it]=[len(x) for x in g]
print(len(out));
for k,v in out.items(): print(k,v)
print('---')
for it,_ in out.items():
    g=groups(comps(R+it+'.json'));g.sort(key=lambda x:-len(x))
    r=[]
    for x in g[1:]:
        lo=[min(b[0][i] for b in x) for i in range(3)];hi=[max(b[1][i] for b in x) for i in range(3)]
        m=[round(16*(lo[i]+hi[i])/2,1) for i in range(3)];z=[round(16*(hi[i]-lo[i]),1) for i in range(3)]
        r.append('%d@%s sz%s'%(len(x),m,z))
    m=g[0];lo=[min(b[0][i] for b in m) for i in range(3)];hi=[max(b[1][i] for b in m) for i in range(3)]
    print(it,'main x%.1f..%.1f y%.1f..%.1f z%.1f..%.1f'%(16*lo[0],16*hi[0],16*lo[1],16*hi[1],16*lo[2],16*hi[2]),' | '.join(r))
