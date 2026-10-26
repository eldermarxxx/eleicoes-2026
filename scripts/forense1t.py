# Testes forenses no 1º turno (presidente), por seção. Fontes: votacao_secao + detalhe_votacao_secao do TSE.
import zipfile,csv,io,collections,datetime as dt,statistics as st,pickle
key=lambda r:(r['SG_UF'],r['CD_MUNICIPIO'],r['NR_ZONA'],r['NR_SECAO'])
v=collections.defaultdict(lambda:{'L':0,'F':0,'O':0,'B':0,'N':0})
with zipfile.ZipFile('votacao_secao_2026_BR.zip').open('votacao_secao_2026_BR.csv') as f:
    for r in csv.DictReader(io.TextIOWrapper(f,encoding='latin-1'),delimiter=';'):
        if r['DS_CARGO']!='Presidente': continue
        q=int(r['QT_VOTOS']); n=r['NM_VOTAVEL']; a=v[key(r)]
        a['L' if 'LULA' in n else 'F' if 'BOLSONARO' in n else 'B' if n=='VOTO BRANCO' else 'N' if n=='VOTO NULO' else 'O']+=q
d={}
with zipfile.ZipFile('detalhe_votacao_secao_2026.zip').open('detalhe_votacao_secao_2026_BR.csv') as f:
    for r in csv.DictReader(io.TextIOWrapper(f,encoding='latin-1'),delimiter=';'):
        if r['DS_CARGO']=='Presidente': d[key(r)]=r
pickle.dump((dict(v),d),open('cache_1t.pkl','wb'))
