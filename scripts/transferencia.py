# Modelo de transferência de votos 1º->2º turno por município (Goodman/OLS, sem intercepto).
# Pergunta: o voto de Lula no 2º turno é explicado pela composição do 1º turno do próprio município?
import pickle,csv,collections as C,numpy as np
v,d=pickle.load(open('cache_1t.pkl','rb'))
nomes={'AUGUSTO JORGE CURY':'cury','RENAN ANTONIO FERREIRA DOS SANTOS':'renan','RONALDO RAMOS CAIADO':'caiado','ROMEU ZEMA NETO':'zema'}
m1=C.defaultdict(C.Counter)
import zipfile,io
with zipfile.ZipFile('votacao_secao_2026_BR.zip').open('votacao_secao_2026_BR.csv') as f:
    for r in csv.DictReader(io.TextIOWrapper(f,encoding='latin-1'),delimiter=';'):
        if r['DS_CARGO']!='Presidente': continue
        n=r['NM_VOTAVEL']; k='lula' if 'LULA' in n else 'flavio' if 'BOLSONARO' in n else 'bn' if n in('VOTO BRANCO','VOTO NULO') else nomes.get(n,'outros')
        m1[(r['SG_UF'],r['CD_MUNICIPIO'].zfill(5))][k]+=int(r['QT_VOTOS'])
for k,r in d.items(): m1[(k[0],k[1].zfill(5))]['aptos']+=int(r['QT_APTOS'])
m2={(r['uf'].upper(),r['mun']):r for r in csv.DictReader(open('mun_2t.csv'))}
print("2T soma municípios: Lula",sum(int(r['lula']) for r in m2.values()),"Flávio",sum(int(r['flavio']) for r in m2.values()))
ks=[k for k in m1 if k in m2 and m1[k]['aptos']>0]; print("municípios pareados:",len(ks),"de",len(m1),len(m2))
X=[];Y=[];W=[];UF=[]
for k in ks:
    a=m1[k]; ap=a['aptos']; comp1=sum(a[x] for x in ('lula','flavio','bn','cury','renan','caiado','zema','outros'))
    X.append([a['lula']/ap,a['flavio']/ap,a['cury']/ap,a['renan']/ap,a['caiado']/ap,a['zema']/ap+a['outros']/ap,a['bn']/ap,(ap-comp1)/ap])
    r=m2[k]; Y.append([int(r['lula'])/ap,int(r['flavio'])/ap]); W.append(ap); UF.append(k[0])
X=np.array(X);Y=np.array(Y);W=np.array(W,float)
sw=np.sqrt(W)[:,None]
B,*_=np.linalg.lstsq(X*sw,Y*sw,rcond=None)
lab=['Lula 1T','Flávio 1T','Cury','Renan','Caiado','Zema+outros','branco/nulo 1T','abstenção 1T']
print("\nFração de cada grupo do 1º turno que foi para (Lula, Flávio) no 2º:")
for l,b in zip(lab,B): print(f"  {l:16s} Lula {b[0]:6.2f}  Flávio {b[1]:6.2f}")
P=X@B; res=(Y[:,0]-P[:,0])*W
R2=1-np.sum(W*(Y[:,0]-P[:,0])**2)/np.sum(W*(Y[:,0]-np.average(Y[:,0],weights=W))**2)
print(f"\nR² ponderado (Lula 2T): {R2:.4f}")
print("Excesso de Lula sobre o modelo, por UF (votos):")
e=C.Counter()
for u,x in zip(UF,res): e[u]+=x
for u,x in sorted(e.items(),key=lambda t:-abs(t[1]))[:10]: print(f"  {u} {x:+,.0f}")
o=np.argsort(-(Y[:,0]-P[:,0])); print("\nMunicípios com maior excesso de Lula (pontos do eleitorado):")
for i in o[:10]: print("  ",ks[i],m2[ks[i]]['nome'],f"obs {Y[i,0]:.3f} prev {P[i,0]:.3f} aptos {int(W[i])}")
pickle.dump((ks,X,Y,W,B),open('transf.pkl','wb'))
