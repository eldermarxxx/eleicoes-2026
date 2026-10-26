# Resultado de presidente do 2º turno por município (site de resultados do TSE) -> mun_2t.csv
import json,csv,urllib.request
from concurrent.futures import ThreadPoolExecutor
B='https://resultados.tse.jus.br/oficial/ele2026/6258'
get=lambda u:json.loads(urllib.request.urlopen(u,timeout=60).read())
cm=get(f'{B}/config/mun-e006258-cm.json')
muns=[(a['cd'],m['cd'],m['nm']) for a in cm['abr'] for m in a['mu'] if a['cd']!='zz']
def um(x):
    uf,mu,nm=x
    for t in range(3):
        try: j=get(f'{B}/dados/{uf}/{uf}{mu}-c0001-e006258-u.json'); break
        except Exception as e: err=e
    else: return {'uf':uf,'mun':mu,'nome':nm,'erro':str(err)[:60]}
    c={k['nm']:int(k['vap']) for a in j['carg'][0]['agr'] for p in a['par'] for k in p['cand']}
    return {'uf':uf,'mun':mu,'nome':nm,'erro':'','aptos':j['e']['te'],'comparec':j['e']['c'],'brancos':j['v']['vb'],'nulos':j['v']['tvn'],
            'lula':c.get('LUIZ INÁCIO LULA DA SILVA',0),'flavio':c.get('FLAVIO NANTES BOLSONARO',0),'secoes_tot':j['s']['st'],'secoes':j['s']['ts']}
with ThreadPoolExecutor(8) as ex: res=list(ex.map(um,muns))
with open('mun_2t.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['uf','mun','nome','erro','aptos','comparec','brancos','nulos','lula','flavio','secoes_tot','secoes']); w.writeheader(); w.writerows(res)
print(len(res),'municípios;',sum(1 for r in res if r['erro']),'erros')
