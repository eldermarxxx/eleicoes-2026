import io, zipfile, urllib.request, sys
class R(io.RawIOBase):
    def __init__(s,u):
        s.u=u; s.p=0
        s.n=int(urllib.request.urlopen(urllib.request.Request(u,method='HEAD')).headers['Content-Length'])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.p
    def seek(s,o,w=0):
        s.p={0:o,1:s.p+o,2:s.n+o}[w]; return s.p
    def readinto(s,b):
        if s.p>=s.n: return 0
        e=min(s.p+len(b),s.n)-1
        d=urllib.request.urlopen(urllib.request.Request(s.u,headers={'Range':f'bytes={s.p}-{e}'})).read()
        b[:len(d)]=d; s.p+=len(d); return len(d)
u=sys.argv[1]
z=zipfile.ZipFile(io.BufferedReader(R(u),1<<20))
l=z.infolist(); print(len(l),"entradas")
from collections import Counter
print(Counter(i.filename.rsplit('.',1)[-1] for i in l))
for i in l[:6]: print(i.filename,i.file_size)
j=next(i for i in l if i.filename.endswith('.jez'))
open(j.filename.split('/')[-1],'wb').write(z.read(j)); print("baixou",j.filename)
