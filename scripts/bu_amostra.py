# Baixa e decodifica o BU (presidente) das seções da amostra do 2º turno -> bu_amostra_2t.json
import json,csv,urllib.request
from concurrent.futures import ThreadPoolExecutor
from bu import le_bu
B='https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221'
get=lambda u:urllib.request.urlopen(u,timeout=60).read()
def um(k):
    uf,m,z,s=k
    try:
        base=f'{B}/dados/{uf}/{m}/{z}/{s}'
        aux=json.loads(get(f'{base}/p003221-{uf}-m{m}-z{z}-s{s}-aux.json'))
        h=([x for x in aux['hashes'] if x['st']=='Totalizado'] or aux['hashes'])[-1]
        b=le_bu(get(f"{base}/{h['hash']}/"+[a['nm'] for a in h['arq'] if a['tp']=='bu'][0]))
        return ['/'.join(k),{'comparec':b['comparec'],'bio':b['bio'],'aptos':b['aptos'],'votos':{str(a):c for a,c in b['votos'].items()}}]
    except Exception as e: return ['/'.join(k),{'erro':str(e)[:60]}]
am=[(r['uf'],r['mun'],r['zona'],r['secao']) for r in csv.DictReader(open('2t_amostra.csv'))]
with ThreadPoolExecutor(8) as ex: res=dict(ex.map(um,am))
json.dump(res,open('bu_amostra_2t.json','w'))
print(len(res),sum('erro' in v for v in res.values()))
