import zipfile,csv,io,collections,datetime as dt
key=lambda r:(r['SG_UF'],r['CD_MUNICIPIO'],r['NR_ZONA'],r['NR_SECAO'])
# votos por seção
v=collections.defaultdict(lambda:[0,0,0])  # lula, flavio, outros
with zipfile.ZipFile('votacao_secao_2026_BR.zip').open('votacao_secao_2026_BR.csv') as f:
    for r in csv.DictReader(io.TextIOWrapper(f,encoding='latin-1'),delimiter=';'):
        if r['DS_CARGO']!='Presidente': continue
        q=int(r['QT_VOTOS']); n=r['NM_VOTAVEL']; a=v[key(r)]
        if 'LULA' in n: a[0]+=q
        elif 'BOLSONARO' in n: a[1]+=q
        elif n not in('VOTO NULO','VOTO BRANCO'): a[2]+=q
# detalhe (presidente)
d={}
with zipfile.ZipFile('detalhe_votacao_secao_2026.zip').open('detalhe_votacao_secao_2026_BR.csv') as f:
    for r in csv.DictReader(io.TextIOWrapper(f,encoding='latin-1'),delimiter=';'):
        if r['DS_CARGO']=='Presidente': d[key(r)]=r
print("seções detalhe:",len(d)," seções votos:",len(v))
falt=[k for k in d if k not in v]; extra=[k for k in v if k not in d]
print("no detalhe sem votos:",len(falt)," nos votos sem detalhe:",len(extra))
c=collections.Counter((d[k]['ST_SECAO_INSTALADA'],d[k]['ST_SECAO_ANULADA'],d[k]['DS_ORIGEM_VOTO'],d[k]['QT_COMPARECIMENTO']=='0') for k in falt); print(c)
print("aptos nas faltantes:",sum(int(d[k]['QT_APTOS']) for k in falt))
# linha do tempo de recebimento
P=lambda s:dt.datetime.strptime(s,'%d/%m/%Y %H:%M:%S')
b=collections.defaultdict(lambda:[0,0,0,0])
for k,r in d.items():
    if k not in v or not r['DT_RECEBIMENTO_BU_HOR_TSE'].strip(): continue
    t=P(r['DT_RECEBIMENTO_BU_HOR_TSE']); t=t.replace(minute=t.minute//10*10,second=0)
    x=b[t]; x[0]+=1; x[1]+=v[k][0]; x[2]+=v[k][1]; x[3]+=v[k][2]
cs=cl=cf=co=0; tot=len(v)
print("hora(10min)  seções  %acum  Lula%/Flávio% (válidos do bloco)")
for t in sorted(b):
    s,l,f_,o=b[t]; cs+=s; cl+=l; cf+=f_; co+=o
    w=l+f_+o
    if dt.datetime(2026,10,4,17)<=t<=dt.datetime(2026,10,5,1): print(t.strftime('%d %H:%M'),f"{s:7d} {100*cs/tot:6.1f}%  bloco L {100*l/w:5.1f} F {100*f_/w:5.1f} | acum L {100*cl/(cl+cf+co):5.2f} F {100*cf/(cl+cf+co):5.2f}")
