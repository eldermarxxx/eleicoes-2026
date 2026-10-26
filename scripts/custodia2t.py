# Varredura de custódia nos logs completos das urnas (amostra do 2º turno).
# Por seção: datas em que a urna foi ligada, carga (computador/mídia), relógio digitado,
# verificações de assinatura sem sucesso, eventos depois do encerramento, voto sem habilitação, duração de cada eleitor.
import json,csv,subprocess,urllib.request,datetime as dt,collections as C,re
from concurrent.futures import ThreadPoolExecutor
B='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
get=lambda u:urllib.request.urlopen(u,timeout=60).read()
P=lambda s:dt.datetime.strptime(s,'%d/%m/%Y %H:%M:%S')
norm=lambda m:re.sub(r'\d+','N',m)
def varre(sec):
    uf,m,z,s=sec
    try:
        aux=json.loads(get(f'{B}/dados/{uf}/{m}/{z}/{s}/p003221-{uf}-m{m}-z{z}-s{s}-aux.json'))
        h=([x for x in aux['hashes'] if x['st']=='Totalizado'] or aux['hashes'])[-1]
        log=[a['nm'] for a in h['arq'] if a['tp']=='log'][0]
        raw=get(f"{B}/dados/{uf}/{m}/{z}/{s}/{h['hash']}/{log}")
        L=[l.split('\t') for l in subprocess.run(['tar','-xOf','-','logd.dat'],input=raw,capture_output=True).stdout.decode('latin-1').splitlines()]
    except Exception as e: return {'sec':sec,'erro':str(e)[:60]}
    L=[x for x in L if len(x)>=5]
    r={'sec':sec,'erro':'','recebido_tse':h.get('dr','')+' '+h.get('hr',''),'linhas':len(L)}
    r['datas']=dict(C.Counter(x[0][:10] for x in L))
    r['carga']=[x[4] for x in L if 'Mídia de carga gerada pelo computador' in x[4] or 'Código de carga' in x[4] or 'Número de série da MR' in x[4] or 'Modelo de Urna' in x[4] or 'Identificador da mídia de carga' in x[4] or 'Data e hora que foi digitada' in x[4]]
    r['assinatura_falha']=[x[0]+' '+x[4] for x in L if 'Verificação de assinatura' in x[4] and 'SUCESSO' not in x[4]]
    r['niveis']=dict(C.Counter(x[1] for x in L))
    r['erros']=dict(C.Counter(norm(x[4]) for x in L if x[1] not in('INFO',)))
    # dia da eleição
    E=[x for x in L if x[0].startswith('25/10/2026')]
    enc=[i for i,x in enumerate(E) if x[4].startswith('Votação encerrada')]
    r['apos_encerramento']=dict(C.Counter(norm(x[4]) for x in E[enc[-1]+1:])) if enc else 'sem_encerramento'
    r['encerramentos']=len(enc)
    hab=None; dur=[]; sem_hab=0; tempo_volta=0; ant=None
    for x in E:
        t=P(x[0])
        if ant and t<ant: tempo_volta+=1
        ant=t
        if x[4].startswith('Eleitor foi habilitado'): hab=t
        elif x[4].startswith('O voto do eleitor foi computado'):
            if hab is None: sem_hab+=1
            else: dur.append((t-hab).total_seconds())
            hab=None
    dur.sort()
    r.update(voto_sem_habilitacao=sem_hab,relogio_voltou=tempo_volta,votos=len(dur)+sem_hab,
             dur_min=dur[0] if dur else None,dur_mediana=dur[len(dur)//2] if dur else None,dur_lt8s=sum(d<8 for d in dur))
    return r
am=[(r['uf'],r['mun'],r['zona'],r['secao']) for r in csv.DictReader(open('2t_amostra.csv'))]
with ThreadPoolExecutor(8) as ex, open('custodia_2t.jsonl','w') as f:
    for r in ex.map(varre,am): f.write(json.dumps(r,ensure_ascii=False)+'\n')
print('ok')
