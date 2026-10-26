import pickle,collections as C,datetime as dt,statistics as st
v,d=pickle.load(open('cache_1t.pkl','rb'))
I=lambda r,c:int(r[c] or 0)
print("== 1. Consistência interna ==")
e=C.Counter(); ex=C.defaultdict(list)
for k,r in d.items():
    if k not in v: continue
    a=v[k]; ap,co,ab=I(r,'QT_APTOS'),I(r,'QT_COMPARECIMENTO'),I(r,'QT_ABSTENCOES')
    tot=sum(a.values())
    for nome,ok in [('votos==comparecimento',tot==co),('comparec<=aptos',co<=ap),('comparec+abst==aptos',co+ab==ap),
                    ('nominais==L+F+outros',I(r,'QT_VOTOS_NOMINAIS')==a['L']+a['F']+a['O']),
                    ('brancos bate',I(r,'QT_VOTOS_BRANCOS')==a['B']),('nulos bate',I(r,'QT_VOTOS_NULOS')==a['N'])]:
        if not ok: e[nome]+=1; ex[nome].append((k,ap,co,tot))
print(f"{len(v)} seções testadas"); 
for n in ['votos==comparecimento','comparec<=aptos','comparec+abst==aptos','nominais==L+F+outros','brancos bate','nulos bate']: print(f"  {n:25s} falhas: {e[n]}", ex[n][:3])
print("\n== 2. Origem do voto ==")
o=C.defaultdict(lambda:[0,0,0,0])
for k,r in d.items():
    if k in v: x=o[r['DS_ORIGEM_VOTO']]; x[0]+=1; x[1]+=v[k]['L']; x[2]+=v[k]['F']; x[3]+=v[k]['L']+v[k]['F']+v[k]['O']
for t,(s,l,f,w) in o.items(): print(f"  {t:22s} seções {s:7d}  L {100*l/max(w,1):5.1f}% F {100*f/max(w,1):5.1f}%  válidos {w:,}")
print("\n== 3. Outliers (seções com >=100 aptos) ==")
rows=[]
for k,r in d.items():
    if k not in v: continue
    ap,co=I(r,'QT_APTOS'),I(r,'QT_COMPARECIMENTO'); a=v[k]; w=a['L']+a['F']+a['O']
    if ap>=100 and w>0: rows.append((k,ap,co/ap,a['L']/w,a['F']/w,w))
tu=[x[2] for x in rows]; print(f"  comparecimento: mediana {st.median(tu):.3f}, p99 {sorted(tu)[int(.99*len(tu))]:.3f}")
for lim in (.95,.98,1.0): print(f"  comparecimento >= {lim:.0%}: {sum(t>=lim for t in tu)} seções")
for nome,i in (('Lula',3),('Flávio',4)):
    for lim in (.9,.95,.99): print(f"  {nome} >= {lim:.0%} dos válidos: {sum(x[i]>=lim for x in rows)} seções")
    sus=[x for x in rows if x[2]>=.95 and x[i]>=.9]; print(f"  {nome}: comparecimento>=95% E voto>=90% (assinatura de 'enchimento'): {len(sus)}", [(x[0],x[1],round(x[2],3),round(x[i],3)) for x in sus[:8]])
print("\n== 4. Fingerprint: média de voto por faixa de comparecimento ==")
fx=C.defaultdict(lambda:[0,0,0,0])
for x in rows:
    b=min(int(x[2]*20),19); y=fx[b]; y[0]+=1; y[1]+=x[3]*x[5]; y[2]+=x[4]*x[5]; y[3]+=x[5]
for b in sorted(fx): s,l,f,w=fx[b]; print(f"  compar {b*5:3d}-{b*5+5:3d}%: {s:7d} seções  L {100*l/w:5.1f}  F {100*f/w:5.1f}")
pickle.dump(rows,open('rows_1t.pkl','wb'))
