# Dossiê de uma seção no 2º turno: BU (votos), hashes assinados, linha do tempo do log.
import sys,json,urllib.request,subprocess,hashlib,pickle,collections as C
from bu import le_bu
B='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
get=lambda u:urllib.request.urlopen(u,timeout=60).read()
def dossie(uf,m,z,s):
    base=f'{B}/dados/{uf}/{m}/{z}/{s}'
    aux=json.loads(get(f'{base}/p003221-{uf}-m{m}-z{z}-s{s}-aux.json'))
    out={'hashes_publicados':[(h['hash'][:12],h['dr'],h['hr'],h['st']) for h in aux['hashes']]}
    h=([x for x in aux['hashes'] if x['st']=='Totalizado'] or aux['hashes'])[-1]
    f={a['tp']:get(f"{base}/{h['hash']}/{a['nm']}") for a in h['arq']}
    out['hash_ok']={k:hashlib.sha512(v).digest() in f['vota'] for k,v in f.items() if k!='vota'}
    out['bu']=le_bu(f['bu'])
    L=[l.split('\t') for l in subprocess.run(['tar','-xOf','-','logd.dat'],input=f['log'],capture_output=True).stdout.decode('latin-1').splitlines()]
    out['dias']=dict(C.Counter(x[0][:10] for x in L if len(x)>4))
    out['chave']=[x[0]+' '+x[4] for x in L if len(x)>4 and any(t in x[4] for t in ('Código de carga','Mídia de carga gerada pelo computador','Iniciando aplicação','Votação encerrada','Urna pronta para receber','zerésima','Data e hora que foi digitada'))]
    return out
if __name__=='__main__':
    print(json.dumps(dossie(*sys.argv[1:5]),ensure_ascii=False,indent=1,default=str))
