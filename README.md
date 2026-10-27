# Auditoria independente dos dados públicos da eleição presidencial de 2026 (2º turno)

**Resultados parciais e preliminares.** Este repositório reúne os scripts e os achados de uma auditoria feita por
um cidadão, a partir exclusivamente de dados que o TSE publica. A análise foi feita com apoio de uma IA (Claude).
Nada aqui é prova de fraude, e nada aqui é prova de ausência de fraude. Veja os limites abaixo.

## Premissa
Não confiar nos números do TSE: quando possível, refazer a conta a partir dos arquivos que cada urna gera e assina
(boletim de urna, registro digital do voto, log) e comparar com o total divulgado.

## Resultado principal (varredura completa)
Boletins de urna (BU) de **499.207 urnas** (todas as seções com arquivo publicado; 17.823 são seções agregadas, sem urna própria),
decodificados com a especificação ASN.1 oficial, somam **Lula 64.256.232 e Flávio Bolsonaro 59.826.041**.
**Os dois números são idênticos aos totais oficiais do TSE, voto a voto.**

Conclusão defensável: o total divulgado corresponde exatamente ao que as urnas registraram nos arquivos públicos.
Limite: 108 seções listadas deram 404 e 41 constam como "Não instalada"; o fato de o total fechar no voto indica que não pesam no resultado.
Não verificamos a assinatura digital em si (veja Limites).

## O que foi testado
Todos os testes, inclusive os que não deram em nada, estão em [ACHADOS.md](ACHADOS.md), do indício mais fraco ao
mais forte. Resumo:

- A conta 1º → 2º turno fecha no voto (a "origem dos 11 milhões" é terceira via + brancos/nulos + 2,96 milhões de comparecimento a mais).
- A "virada" na noite da apuração é a ordem geográfica de chegada das seções, e Lula crescer em todos os estados
  tem precedente: em 2022 foi Bolsonaro que cresceu em 28 de 28 estados.
- Logs de urna: votos depois das 17h são 0,03%; depois das 19h, praticamente nenhum; nenhum intervalo abaixo de
  10 segundos entre dois votos; nenhum voto sem eleitor habilitado.
- Voto rápido e voto sem biometria **não** acompanham a virada de Lula seção a seção.
- **Achado real, pequeno:** em 51 de 499 mil urnas (0,010%) o código de carga gravado pela própria urna não consta em
  nenhuma versão da tabela pública de correspondência esperada. Somam 12,6 mil votos (57,5% Lula, contra 54,9% nas mesmas
  seções no 1º turno). Tratado como falha de registro de custódia a ser perguntada ao TSE, e não como fraude.

## Limites (leia antes de citar)
- Parcial. O ranking e os números mudam conforme a varredura avança.
- Só enxerga dados publicados. O que ocorreu dentro do software da urna antes de assinar não é visível aqui.
- A verificação conferiu se o **SHA-512 de cada arquivo consta do manifesto assinado pela urna**.
  A **assinatura digital em si e a cadeia de certificados não foram verificadas** (para isso, veja o projeto
  [DataUrnas-BR](https://github.com/alissonlinneker/DataUrnas-BR), que fez isso no 1º turno).
- Os testes por município (transferência de votos) são análises ecológicas: mostram associação, não o voto de
  cada pessoa. O sigilo do voto impede isso.
- Faltam o teste mais forte, que é a comparação com **fotos dos boletins impressos** nas seções (QR code, fora do
  controle do TSE), e a verificação completa de assinaturas do 2º turno.

## Fontes (todas públicas)
- Dados abertos do TSE: <https://dadosabertos.tse.jus.br>
- Arquivos de urna seção a seção: `https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/...`
- Resultados por município: `https://resultados.tse.jus.br/oficial/ele2026/6258/dados/...`
- Tabelas de correspondência esperada: `https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/correspesp/`

## Como reproduzir
Requer Python 3.11+ e `asn1tools` (`pip install asn1tools numpy`). O `bu.py` precisa dos arquivos
`bu.asn1` e `assinatura.asn1` (spec v2) em uma pasta `spec/` ao lado dele. Eles são publicados pelo TSE e
reproduzidos em <https://github.com/alissonlinneker/DataUrnas-BR/tree/main/spec/v2>.
Os dados brutos (centenas de MB) não estão no repositório; os scripts baixam tudo do TSE.

Ordem sugerida: `coleta_mun2t.py` → `forense1t.py` → `transferencia.py` → `varredura_total.py` → `analise_varredura.py`.

## Contribua
Se encontrar erro, **abra uma issue**. A ideia é que qualquer pessoa consiga refazer e contestar. Correções já feitas
durante a análise estão registradas em ACHADOS.md (por exemplo, "arquivos 404" que na verdade são seções agregadas).

## Licença
Código: MIT. Dados originais: TSE (licença CC BY, conforme o portal de dados abertos).
