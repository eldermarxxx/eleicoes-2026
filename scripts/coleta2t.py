# Amostra aleatória de logs de urna do 2º turno (pleito 3221), direto do site de resultados do TSE.
# Uso: python3 -I coleta2t.py <seções por UF>   -> grava 2t_amostra.csv
import json,random,subprocess,sys,csv,os,urllib.request,datetime as dt
from concurrent.futures import ThreadPoolExecutor
B='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
UFS='ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to'.split()
N=int(sys.argv[1]); random.seed(2026)
get=lambda u:urllib.request.urlopen(u,timeout=60).read()
def secoes(uf):
    j=json.loads(get(f'{B}/config/{uf}/{uf}-p003221-cs.json'))
    return [(uf,m['cd'],z['cd'],s['ns']) for a in j['abr'] for m in a['mu'] for z in m['zon'] for s in z['sec']]
P=lambda s:dt.datetime.strptime(s,'%d/%m/%Y %H:%M:%S')
def analisa(sec):
    uf,m,z,s=sec
    try:
        aux=json.loads(get(f'{B}/dados/{uf}/{m}/{z}/{s}/p003221-{uf}-m{m}-z{z}-s{s}-aux.json'))
        h=[x for x in aux['hashes'] if x['st']=='Totalizado'] or aux['hashes']
        log=[a['nm'] for a in h[-1]['arq'] if a['tp']=='log'][0]
        raw=get(f"{B}/dados/{uf}/{m}/{z}/{s}/{h[-1]['hash']}/{log}")
        txt=subprocess.run(['tar','-xOf','-','logd.dat'],input=raw,capture_output=True).stdout.decode('latin-1')
    except Exception as e: return {'uf':uf,'mun':m,'zona':z,'secao':s,'erro':str(e)[:80]}
    L=[l.split('\t') for l in txt.splitlines() if l.startswith('25/10/2026')]
    pronta=[P(x[0]) for x in L if len(x)>4 and x[4].startswith('Urna pronta para receber votos')]
    off=round((8*60-(pronta[0].hour*60+pronta[0].minute))/60) if pronta else None  # fuso local -> Brasília
    votos=[]; bio=False
    for x in L:
        if len(x)<5: continue
        if x[4].startswith('Aguardando digitação do identificador'): bio=False
        elif 'Tipo de habilitação do eleitor [biométrica]' in x[4]: bio=True
        elif x[4].startswith('O voto do eleitor foi computado'): votos.append((P(x[0])+dt.timedelta(hours=off or 0),bio))
    gaps=[(b[0]-a[0]).total_seconds() for a,b in zip(votos,votos[1:])]
    t17=dt.datetime(2026,10,25,17); t19=dt.datetime(2026,10,25,19)
    return {'uf':uf,'mun':m,'zona':z,'secao':s,'erro':'','fuso':off,'votos':len(votos),
        'sem_bio':sum(not b for _,b in votos),'apos17':sum(t>=t17 for t,_ in votos),'apos17_sem_bio':sum(t>=t17 and not b for t,b in votos),
        'apos19':sum(t>=t19 for t,_ in votos),'primeiro':votos[0][0].strftime('%H:%M:%S') if votos else '','ultimo':votos[-1][0].strftime('%H:%M:%S') if votos else '',
        'gap_lt5s':sum(g<5 for g in gaps),'gap_lt10s':sum(g<10 for g in gaps),'gap_min':min(gaps) if gaps else '',
        'reinicios':sum(1 for x in L if len(x)>4 and x[4].startswith('Urna pronta para receber votos'))-1}
amostra=[]
for uf in UFS:
    t=secoes(uf); amostra+=random.sample(t,min(N,len(t)))
with ThreadPoolExecutor(8) as ex: res=list(ex.map(analisa,amostra))
with open('2t_amostra.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list({k:0 for r in res for k in r})); w.writeheader(); w.writerows(res)
print(len(res),'seções;',sum(1 for r in res if r['erro']),'erros')
