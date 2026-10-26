# Análise da varredura do 2º turno (funciona com o arquivo parcial). Uso: python3 -I analise_varredura.py
import json,pickle,collections as C,numpy as np
OFICIAL={'13':64256232,'22':59826041}
E=pickle.load(open('corresp_2t.pkl','rb'))
import csv,glob
CONT={r['CD_CARGA_URNA_ESPERADA'].lstrip('0'):r for f in glob.glob('corresp/ccont_2t_*.csv') for r in csv.DictReader(open(f,encoding='latin-1'),delimiter=';')}
v1,d1=pickle.load(open('cache_1t.pkl','rb'))
R=[json.loads(l) for l in open('varredura_2t.jsonl')]
k1=lambda s:(lambda u,m,z,x:(u.upper(),str(int(m)),str(int(z)),str(int(x))))(*s.split('/'))
ag=[r for r in R if 'agregada_a' in r]; er=[r for r in R if 'erro' in r]; ok=[r for r in R if 'bu' in r]
print(f"seções lidas {len(R)} | com BU {len(ok)} | agregadas {len(ag)} | erros {len(er)}", C.Counter(r['erro'][:45] for r in er).most_common(3))
print("status do índice:",C.Counter(r.get('st') for r in R if 'agregada_a' not in r).most_common())
print("arquivos 404 dentro de seção publicada:",[(r['sec'],r['arq_404']) for r in R if r.get('arq_404')][:10])

print("\n== Integridade ==")
hb=[r['sec'] for r in ok if r.get('hash_ok') and not all(r['hash_ok'].values())]
print("SHA-512 que NÃO consta do manifesto assinado:",len(hb),hb[:10])
mis=[(r['sec'],r['log']['votos'],r['bu']['comparec']) for r in ok if 'log' in r and r['log']['votos']!=r['bu']['comparec']]
print("votos no log ≠ comparecimento no BU:",len(mis),mis[:8])

print("\n== Custódia (urna que votou x tabela oficial) ==")
cls=C.Counter(); fora=[]
for r in ok:
    e=E.get(tuple(r['sec'].split('/'))); cod=r.get('log',{}).get('carga') or r['bu']['carga']  # carga da urna que gerou o log (a última)
    extra=[c for c in r['bu']['carga'] if c not in CONT and (not e or c!=e['CD_CARGA_URNA_ESPERADA'].lstrip('0'))]
    if extra: cls['BU cita urna fora das tabelas']+=1
    if not e: cls['seção fora da tabela']+=1; continue
    if e['CD_CARGA_URNA_ESPERADA'].lstrip('0') in cod: cls['esperada']+=1
    elif any(c in CONT for c in cod): cls['contingência registrada']+=1
    else: cls['FORA DE QUALQUER TABELA']+=1; fora.append(r)
print(cls)
L=F=L1=F1=0
for r in fora:
    vv=r['bu']['votos']; a=v1.get(k1(r['sec']),{}); L+=vv.get('13',0); F+=vv.get('22',0); L1+=a.get('L',0); F1+=a.get('F',0)
    print(f"  {r['sec']} carga {r['bu']['carga']} máquina {r.get('log',{}).get('maquina')} dias {list(r.get('log',{}).get('datas',{}))[:3]} | 2T L{vv.get('13',0)} F{vv.get('22',0)} | 1T L{a.get('L')} F{a.get('F')}")
if fora: print(f"  soma fora-de-tabela: 2T Lula {L} Flávio {F} | mesmas seções no 1T: Lula {L1} Flávio {F1}")

print("\n== Log ==")
lg=[r['log'] for r in ok if 'log' in r]
print("assinatura com ERRO:",sum(bool(x['assinatura_erro']) for x in lg),"| relógio voltou no dia:",sum(x['relogio_voltou']>0 for x in lg),
      "| voto sem habilitação:",sum(x['voto_sem_habilitacao'] for x in lg),"| intervalos <10s:",sum(x['gap_lt10'] for x in lg))
fut=C.Counter(d for x in lg for d in x['datas'] if d[3:5]=='10' and int(d[:2])>25 or d[6:]>'2026'); print("datas depois de 25/10 no relógio:",fut.most_common(5))
V=sum(x['votos'] for x in lg); print(f"votos {V:,} | após 17h {sum(x['apos17'] for x in lg):,} | após 19h {sum(x['apos19'] for x in lg)} | sem bio {100*sum(x['sem_bio'] for x in lg)/max(V,1):.1f}%")

print("\n== Recontagem a partir dos BUs ==")
t=C.Counter()
for r in ok: t.update(r['bu']['votos'])
f=len(ok)/max(len(ok)+len(er),1)
print(f"Lula {t['13']:,}  Flávio {t['22']:,}  brancos {t['branco']:,}  nulos {t['nulo']:,}  ({len(ok)} urnas)")
if len(er)==0 and len(R)>490000: print("diferença p/ oficial: Lula",t['13']-OFICIAL['13'],"Flávio",t['22']-OFICIAL['22'])
else: print(f"Lula {100*t['13']/(t['13']+t['22']):.2f}% dos votos de Lula+Flávio (oficial 51,79%)")

print("\n== Tempo na cabine x virada de Lula (dentro da UF) ==")
X=[]
for r in ok:
    a=v1.get(k1(r['sec'])); vv=r['bu']['votos']; x=r.get('log')
    if not a or not x or x['votos']<30 or a['L']+a['F']<30 or vv.get('13',0)+vv.get('22',0)<30: continue
    X.append((r['sec'][:2],x['dur_lt8']/x['votos'],x['sem_bio']/x['votos'],vv.get('13',0)/(vv.get('13',0)+vv.get('22',0))-a['L']/(a['L']+a['F'])))
if X:
    uf=np.array([x[0] for x in X]); fa,nb,dl=(np.array([x[i] for x in X]) for i in (1,2,3))
    dm=lambda a:a-np.array([a[uf==u].mean() for u in uf])
    print(f"{len(X)} seções | corr(<8s, virada) {np.corrcoef(dm(fa),dm(dl))[0,1]:+.3f} | corr(sem biometria, virada) {np.corrcoef(dm(nb),dm(dl))[0,1]:+.3f}")
