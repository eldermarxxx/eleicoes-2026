# Varredura completa do 2º turno (pleito 3221): para cada seção baixa índice, BU, log e manifesto assinado (vota.vsc),
# confere os SHA-512, decodifica o BU e extrai do log a custódia (carga, datas, relógio, assinaturas) e os tempos de voto.
# Retomável: pula seções já gravadas em varredura_2t.jsonl. Uso: python varredura_total.py [ufs...] [--threads N]
import json,sys,os,random,subprocess,hashlib,urllib.request,datetime as dt,collections as C,re,time
from concurrent.futures import ThreadPoolExecutor
from bu import le_bu
B='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
OUT='varredura_2t.jsonl'
UFS='ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to zz'.split()
P=lambda s:dt.datetime.strptime(s,'%d/%m/%Y %H:%M:%S')
norm=lambda m:re.sub(r'\d+','N',m)

def get(u):
    for t in range(4):
        try: return urllib.request.urlopen(u,timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code==404: raise
            err=e
        except Exception as e: err=e
        time.sleep(2**t)
    raise err

def secoes(uf):
    j=json.loads(get(f'{B}/config/{uf}/{uf}-p003221-cs.json'))
    # 'nsp' = seção agregada a outra (vota na urna da seção principal; não tem arquivos próprios)
    return [(uf,m['cd'],z['cd'],s['ns'],s.get('nsp','')) for a in j['abr'] for m in a['mu'] for z in m['zon'] for s in z['sec']]

def analisa_log(txt):
    L=[x for x in (l.split('\t') for l in txt.splitlines()) if len(x)>=5]
    r={'datas':dict(C.Counter(x[0][:10] for x in L))}
    r['carga']=[re.sub(r'\D','',x[4].split('Código de carga')[1].split('gravado')[0]).lstrip('0') for x in L if 'Código de carga' in x[4]]
    r['maquina']=sorted({x[4].split(': ',1)[1] for x in L if 'Mídia de carga gerada pelo computador' in x[4]})
    r['relogio_digitado']=[x[0]+'|'+x[4].split(': ',1)[1] for x in L if 'Data e hora que foi digitada' in x[4]]
    r['assinatura_erro']=[x[0]+' '+x[4] for x in L if 'Verificação de assinatura' in x[4] and 'SUCESSO' not in x[4]]
    r['modelo']=sorted({x[4].split(': ')[-1] for x in L if 'Identificação do Modelo de Urna' in x[4]})
    r['erros']=dict(C.Counter(norm(x[4]) for x in L if x[1]=='ERRO'))
    E=[x for x in L if x[0].startswith('25/10/2026')]
    pronta=[P(x[0]) for x in E if x[4].startswith('Urna pronta para receber votos')]
    off=round((8*60-(pronta[0].hour*60+pronta[0].minute))/60) if pronta else 0  # relógio local -> Brasília
    hab=None; bio=False; votos=[]; dur=[]; sem_hab=0; volta=0; ant=None
    for x in E:
        t=P(x[0])
        if ant and t<ant: volta+=1
        ant=t; m=x[4]
        if m.startswith('Aguardando digitação do identificador'): bio=False
        elif 'Tipo de habilitação do eleitor [biométrica]' in m: bio=True
        elif m.startswith('Eleitor foi habilitado'): hab=t
        elif m.startswith('O voto do eleitor foi computado'):
            if hab is None: sem_hab+=1
            else: dur.append((t-hab).total_seconds())
            votos.append((t+dt.timedelta(hours=off),bio)); hab=None
    gaps=[(b[0]-a[0]).total_seconds() for a,b in zip(votos,votos[1:])]
    t17=dt.datetime(2026,10,25,17); t19=dt.datetime(2026,10,25,19)
    dur.sort()
    r.update(fuso=off,prontas=len(pronta),votos=len(votos),sem_bio=sum(not b for _,b in votos),voto_sem_habilitacao=sem_hab,relogio_voltou=volta,
             apos17=sum(t>=t17 for t,_ in votos),apos17_sem_bio=sum(t>=t17 and not b for t,b in votos),apos19=sum(t>=t19 for t,_ in votos),
             primeiro=votos[0][0].strftime('%H:%M:%S') if votos else '',ultimo=votos[-1][0].strftime('%H:%M:%S') if votos else '',
             dur_mediana=dur[len(dur)//2] if dur else None,dur_min=dur[0] if dur else None,dur_lt5=sum(d<5 for d in dur),dur_lt8=sum(d<8 for d in dur),
             gap_min=min(gaps) if gaps else None,gap_lt10=sum(g<10 for g in gaps))
    return r

def varre(sec):
    uf,m,z,s,nsp=sec; base=f'{B}/dados/{uf}/{m}/{z}/{s}'
    r={'sec':'/'.join(sec[:4])}
    if nsp: r['agregada_a']=nsp; return r
    try:
        aux=json.loads(get(f'{base}/p003221-{uf}-m{m}-z{z}-s{s}-aux.json'))
        r['st']=aux.get('st'); r['n_hashes']=len(aux['hashes'])
        h=([x for x in aux['hashes'] if x['st']=='Totalizado'] or aux['hashes'])[-1]
        r['recebido']=h.get('dr','')+' '+h.get('hr',''); r['st_hash']=h['st']; r['tipos']=sorted(a['tp'] for a in h['arq'])
        f={}
        for a in h['arq']:
            if a['tp'] in ('bu','busa','log','vota'):
                try: f[a['tp']]=get(f"{base}/{h['hash']}/{a['nm']}")
                except urllib.error.HTTPError as e: r.setdefault('arq_404',[]).append(a['tp'])
        if 'vota' in f: r['hash_ok']={k:hashlib.sha512(v).digest() in f['vota'] for k,v in f.items() if k!='vota'}
        bu=f.get('bu') or f.get('busa')
        if bu:
            b=le_bu(bu); r['bu']={'comparec':b['comparec'],'bio':b['bio'],'aptos':b['aptos'],'tipo':b['urna_tipo'],'carga':[c.lstrip('0') for c in (b['carga'] or [])],'votos':{str(k):v for k,v in b['votos'].items()}}
        if 'log' in f:
            txt=subprocess.run(['tar','-xOf','-','logd.dat'],input=f['log'],capture_output=True).stdout.decode('latin-1')
            r['log']=analisa_log(txt)
    except Exception as e: r['erro']=f'{type(e).__name__}: {str(e)[:80]}'
    return r

if __name__=='__main__':
    args=sys.argv[1:]; th=8
    if '--threads' in args: i=args.index('--threads'); th=int(args[i+1]); del args[i:i+2]
    ufs=args or UFS
    feitos=set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try: feitos.add(json.loads(l)['sec'])
            except Exception: pass
    todas=[]
    for uf in ufs:
        try: todas+=secoes(uf)
        except Exception as e: print('sem config',uf,e,flush=True)
    random.seed(2026); random.shuffle(todas)  # ordem aleatória: resultado parcial já é amostra nacional
    falta=[x for x in todas if '/'.join(x[:4]) not in feitos]
    print(f'total {len(todas)}, já feitas {len(todas)-len(falta)}, faltam {len(falta)}',flush=True)
    t0=time.time()
    with ThreadPoolExecutor(th) as ex, open(OUT,'a') as out:
        for i,r in enumerate(ex.map(varre,falta),1):
            out.write(json.dumps(r,ensure_ascii=False)+'\n')
            if i%2000==0:
                out.flush(); v=i/(time.time()-t0)
                print(f'{i}/{len(falta)}  {v:.1f} seções/s  ~{(len(falta)-i)/v/3600:.1f} h restantes',flush=True)
    print('fim',flush=True)
