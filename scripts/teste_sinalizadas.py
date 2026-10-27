# Seções com >=1 voto sem biometria após 17h ("sinalizadas", critério do samuraitrc) x demais da MESMA zona: virada de Lula 1T->2T.
import json,pickle,collections as C,numpy as np
v1,_=pickle.load(open('cache_1t.pkl','rb'))
k1=lambda s:(lambda u,m,z,x:(u.upper(),str(int(m)),str(int(z)),str(int(x))))(*s.split('/'))
Z=C.defaultdict(lambda:([],[]))  # zona -> (flag deltas, ctrl deltas)
n=0;flg=[];dose=[]
for l in open('varredura_2t.jsonl'):
    r=json.loads(l)
    if 'bu' not in r or 'log' not in r: continue
    a=v1.get(k1(r['sec'])); v=r['bu']['votos']; L,F=v.get('13',0),v.get('22',0)
    if not a or a['L']+a['F']<30 or L+F<30: continue
    d=100*(L/(L+F)-a['L']/(a['L']+a['F'])); x=r['log']['apos17_sem_bio']
    Z[r['sec'].rsplit('/',1)[0]][1 if x==0 else 0].append(d)
    if x>0: dose.append((x,d,r['bu']['comparec']))
pares=[(np.mean(f)-np.mean(c),len(f)) for f,c in Z.values() if f and c]
D=np.array([p[0] for p in pares]);W=np.array([p[1] for p in pares])
m=np.average(D,weights=W); rng=np.random.default_rng(2026)
bs=[np.average(D[i],weights=W[i]) for i in (rng.integers(0,len(D),len(D)) for _ in range(2000))]
print(f"seções sinalizadas {sum(len(f) for f,c in Z.values())} | zonas com ambos {len(D)}")
print(f"virada de Lula, sinalizada menos controle da mesma zona: {m:+.3f} p.p. (IC95% por zona {np.percentile(bs,2.5):+.3f} a {np.percentile(bs,97.5):+.3f})")
fl=np.array([x for f,c in Z.values() if f and c for x in f]);print(f"média virada sinalizadas {fl.mean():+.3f} | todas as controles {np.mean([x for f,c in Z.values() for x in c]):+.3f}")
d=np.array(dose);print(f"dose-resposta (nº de votos sem bio após 17h x virada, só sinalizadas): corr {np.corrcoef(d[:,0],d[:,1])[0,1]:+.3f}")
for lo,hi in((1,1),(2,2),(3,5),(6,999)):
    s=d[(d[:,0]>=lo)&(d[:,0]<=hi)];print(f"  {lo}-{hi} votos: {len(s)} seções, virada média {s[:,1].mean():+.2f}, votos totais dessas {int(s[:,2].sum())}")
print("votos sem bio após 17h no total das sinalizadas:",int(d[:,0].sum()))
