# Leitor mínimo de BU (spec ASN.1 oficial do TSE) e conferência dos hashes SHA-512 assinados pela urna (vota.vsc).
import asn1tools,hashlib,os
D=os.path.dirname(os.path.abspath(__file__))
BU=asn1tools.compile_files(f'{D}/spec/bu.asn1',codec='ber')
AS=asn1tools.compile_files(f'{D}/spec/assinatura.asn1',codec='ber')
def le_bu(raw):
    env=BU.decode('EntidadeEnvelopeGenerico',raw); b=BU.decode('EntidadeBoletimUrna',env['conteudo'])
    out={'comparec':b['qtdEleitoresCompareceram'],'bio':(b.get('detalhamentoComparecimento') or {}).get('qtdEleitoresHabilitadosPorBiometria'),
         'urna_tipo':b['urna'].get('tipoUrna'),'carga':b.get('historicoCodigosCarga'),'aptos':None,'votos':{}}
    for e in b['resultadosVotacaoPorEleicao']:
        for rv in e['resultadosVotacao']:
            for t in rv['totaisVotosCargo']:
                if t['codigoCargo']!=('cargoConstitucional','presidente'): continue
                out['aptos']=e['qtdEleitoresAptos']
                for vv in t['votosVotaveis']:
                    k=vv['tipoVoto'] if vv['tipoVoto']!='nominal' else vv['identificacaoVotavel']['codigo']
                    out['votos'][k]=out['votos'].get(k,0)+vv['quantidadeVotos']
    return out
def hashes_assinados(raw):
    e=AS.decode('EntidadeAssinaturaEcourna',raw)
    r={}
    for lado in ('assinaturaSW','assinaturaHW'):
        a=AS.decode('Assinatura',e[lado]['conteudoAutoAssinado'])
        for f in a['arquivosAssinados']: r.setdefault(f['nomeArquivo'],set()).add(f['assinatura']['hash'])
    return r
def confere(arquivos,vsc):
    h=hashes_assinados(vsc); res={}
    for nome,raw in arquivos.items():
        alvo=[v for k,v in h.items() if k.split('.')[0][-3:] in nome or k in nome]
        res[nome]=any(hashlib.sha512(raw).digest() in s for s in alvo) if alvo else None
    return res,sorted(h)
if __name__=='__main__':
    print(le_bu(open('s-bu.dat','rb').read()))
    print(confere({'bu':open('s-bu.dat','rb').read(),'log':open('s.jez','rb').read()},open('s-vota.vsc','rb').read()))
