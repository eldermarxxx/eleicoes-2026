# Auditoria independente – Eleição presidencial 2026 (2º turno)

**Status: parcial e preliminar** (atualizado em 26/10/2026). Os números abaixo mudam conforme a varredura avança.
Nada aqui é prova de fraude nem de ausência de fraude; veja os limites no [README](README.md).

Premissa: não confiar no TSE. Cada teste diz de qual dado depende.
Hipótese testada: houve manipulação de votos a favor de Lula no 2º turno?
Regra: publicar tudo o que foi testado, inclusive o que não deu em nada.
Convenções: "L" = Lula, "F" = Flávio Bolsonaro; BU = boletim de urna; "z" = zona; "s" = seção.

## Ranking dos indícios (do mais fraco ao mais forte)

| # | Suspeita | Teste | Resultado | Força |
|---|----------|-------|-----------|-------|
| 1 | "Surgiram 11 milhões de votos" | Conta 1º→2º turno com totais oficiais | Fecha no voto: 9,32 mi (terceira via) + 0,87 mi (brancos) + 0,95 mi (nulos) + 2,96 mi (comparecimento a mais) = 14,10 mi = ganho de Lula + Flávio | Descartado |
| 2 | "Ia pau a pau e virou" | Ordem de chegada dos BUs (1º turno, horário de recebimento de cada seção) | Sul e Sudeste chegam antes, Nordeste e áreas remotas depois; a curva vira sozinha. No 1º turno Flávio abriu 51x40 e fechou 47x45 | Descartado (padrão geográfico) |
| 3 | Votos depois das 17h/19h (prorrogação do STF) | Logs de 5.191 seções, amostra de 200 por UF | 0,027% dos votos depois das 17h; 0 depois das 19h. Projeção nacional de cerca de 35 mil votos, contra margem de 4,43 mi | Descartado como causa do resultado |
| 4 | Votos "injetados" em rajada | Intervalo entre votos nos logs | Mínimo de 19s; nenhum intervalo abaixo de 10s | Sem sinal |
| 5 | Comparecimento inflado por seção | Log do 2º turno x comparecimento do 1º turno, mesma seção | Mediana +1,05 pt; 99% abaixo de +7,1 pts; nenhuma seção acima dos aptos; maior alta +16,6 pts | Sem sinal |
| 6 | Pausa na apuração (1º turno, 19h06 a 20h08) | Campo "horário de recebimento do BU" do arquivo `detalhe_votacao_secao` | Os BUs continuaram sendo recebidos durante a pausa, o que é compatível com a explicação do TSE (travou a divulgação). Houve também uma queda abrupta de recebimentos entre 19h30 e 19h50 em todas as UFs, que não foi explicada e pode refletir o fim das seções comuns. A composição de votos por lote seguiu contínua, sem salto | Sem efeito no voto; a queda de 19h30 é uma pergunta em aberto |
| 7 | Transferência "improvável" da terceira via | Regressão ecológica por município (5.571) | 2º turno muito bem explicado pelo 1º (R² = 0,992). Coeficientes por candidato instáveis (alguns > 1), então não dá para afirmar quanto de Caiado/Renan/Zema foi para cada lado | Inconclusivo; precisa de pesquisa pós-eleitoral |
| 8 | Aglomerado no sul do MS (Amambai, Paranhos, Tacuru, Laguna Carapã) | Maior excesso de Lula sobre o modelo e maior alta de comparecimento da amostra | Região com aldeias Guarani-Kaiowá (ex.: EE Indígena Mboeroy). **Hipótese (não testada):** mobilização local. Peso de dezenas de milhares de eleitores | Melhor alvo para investigar; não muda o resultado. Ainda não analisado seção por seção |

## "Lula cresceu em todos os estados": é estranho? (controle com 2022)

Métrica: fatia de Lula nos votos de Lula + adversário, do 1º para o 2º turno.

| | 2022 (Lula x Bolsonaro) | 2026 (Lula x Flávio) |
|---|---|---|
| UFs em que o mesmo candidato cresceu | **28 de 28, todas para Bolsonaro** (de -0,5 a -2,7 pts para Lula) | **27 de 27, todas para Lula** (de +1,2 a +4,3 pts) |
| Municípios em que o mesmo candidato cresceu | 98% para Bolsonaro | 97% para Lula |
| Virada média por município | -1,69 pts | +2,95 pts |
| "Empurrão" fixo que sobra no modelo de redistribuição | -1,39 pts (para Bolsonaro) | +1,98 pts (para Lula) |

- Um candidato crescer no país inteiro é o padrão normal de 2º turno no Brasil. Aconteceu em 2022 a favor de Bolsonaro,
  com a mesma forma.
- Em 2026 a virada é maior onde a terceira via era maior (correlação +0,59 entre UFs). Goiás (Caiado) tem a maior
  terceira via e está entre as maiores viradas. Isso é o rastro de redistribuição de votos, não de % fixo injetado.
- O "empurrão" fixo existe nos dois anos, em sentidos opostos. **Interpretação (não provada):** reflete quem passou
  a votar ou deixou de votar entre os turnos (2026: +2,96 milhões de eleitores) e trocas de lado. O fato verificável
  é que o mesmo resíduo aparece em 2022 com sinal contrário.
- Script do controle: trechos em `transferencia.py` e dados de 2022 em `mun_2022.pkl`.

## Cadeia de custódia das urnas (amostra de 5.191 seções do 2º turno)

Cruzamento: o que cada urna gravou no próprio log (código de carga, computador, data) x a tabela oficial
"Correspondências esperadas" (qual urna deveria estar em cada seção) x o BU publicado.
Script: `custodia2t.py` (varredura) e `secao2t.py` (dossiê de uma seção, com conferência do SHA-512 assinado).

| Achado | Números | Leitura |
|--------|---------|---------|
| Urna que votou = urna esperada | 5.159 de 5.191 (99,4%) | Normal |
| Urna que votou é de contingência registrada | 31 | Troca de urna prevista nas regras; todas constam da tabela de contingência |
| **Urna fora de qualquer tabela oficial** | **1: Laranjal do Jari-AP, zona 7, seção 19** | Carregada em 24/10 às 10h00 (computador RAPWGM09); código 373.114.434.983.038.692.379.051 não aparece nas tabelas de 24/10 nem de 25/10. O BU foi totalizado. Votos: Lula 129, Flávio 104 (1º turno: 132 x 129). Na varredura maior (abaixo) aparecem mais 3; a estimativa nacional é de dezenas de seções, e não centenas |
| Esperada carregada no dia da eleição, mas votou a urna antiga | 2 (Primavera-PA s.158; Ibotirama-BA s.2) | A tabela de 25/10 aponta uma urna nova que não foi a que votou |
| ~~Arquivo listado, mas 404~~ **CORRIGIDO** | Os 209 casos da amostra são **seções agregadas** (campo `nsp` na configuração do TSE): os eleitores votam na urna da seção principal e a seção não tem arquivos próprios. **Não é falha.** | A estimativa anterior de "19 mil urnas sem arquivo" estava errada |
| Arquivo listado, mas 404 de verdade | Atibaia-SP s.436: status "Recebida" (não "Totalizada") e arquivos 404 | Caso isolado até agora; a varredura total vai medir |
| Verificação de assinatura com ERRO | 2 (ambas na carga, em setembro) | Ainda não conferido se houve nova verificação com sucesso |
| Relógio da urna com data futura | 2 (27/10 e 29/10) | Relógio errado em algum momento da vida da urna |
| Voto computado sem eleitor habilitado | 0 | Normal |
| Hash SHA-512 de BU, RDV e log x manifesto assinado | Confere nos 10 dossiês abertos | Verifica só que o hash do arquivo consta do manifesto (`vota.vsc`). **A assinatura digital e a cadeia de certificados não foram verificadas aqui** |

### Tempo na cabine (habilitação até o voto computado) x resultado da urna
5.189 seções com log + BU do 2º turno + resultado do 1º turno da mesma seção.
- Tempo mediano na cabine: 10s nos estados só com presidente; 15 a 17s nos estados com 2º turno de governador
  (DF, RN, AM, AC, ES, TO). Isso é o comportamento humano esperado (mais cargos, mais tempo).
- Fração de eleitores com menos de 8s: mediana 9%, p90 31%.
- Se votos fossem "injetados" rápido a favor de Lula, as seções com mais votos rápidos teriam virada maior para Lula.
  Resultado: correlação dentro da UF de +0,04 (quase nula). Quintil com menos votos rápidos: +2,65 pts para Lula;
  quintil com mais: +2,99 pts.
- Fração de votos sem biometria x virada de Lula: correlação -0,001 (nula).
- Intervalo mínimo entre dois votos na mesma urna: 19s (nenhum caso abaixo de 10s).
- Log x BU no comparecimento: 16 divergências, que são urnas trocadas durante o dia (o log publicado é da urna final).

### Varredura total (parcial: 41.090 urnas, cerca de 8%, ordem aleatória)
- **Recontagem pelos BUs, sem RR** (RR entrou inteiro no teste): **Lula 51,79%** dos votos de Lula+Flávio;
  IC95% de 51,63 a 51,95. **Oficial: 51,79%.**
- SHA-512 fora do manifesto assinado: 0. Voto sem habilitação: 0. Intervalo <10s entre votos: 0.
- **Urnas que votaram com código de carga ausente das tabelas oficiais de 24/10 e de 25/10:**

| Seção | Carga da urna (segundo o próprio log) | 2º turno | 1º turno (mesma seção) |
|---|---|---|---|
| Laranjal do Jari-AP z7 s19 (amostra) | 24/10, véspera | L129 x F104 | L132 x F129 |
| Ananindeua-PA z107 s341 | 15/10, entre os turnos | L175 x F152 | L155 x F142 |
| Salvador-BA z8 s606 | 24/10, véspera | L260 x F82 | L194 x F78 |
| São Luís-MA z1 s125 | 28/09; votou no 1º turno | L218 x F79 | L191 x F80 |

  São cerca de 3 em 41 mil urnas, o que daria uns 35 no país. Somam menos de mil votos, com virada parecida com a média.
  É falha de registro de custódia, a ser perguntada ao TSE; não muda o resultado.
- Verificação de assinatura com ERRO: 18 urnas, quase todas em `infomidia.vsc` durante a carga (setembro),
  e 1 no dia 25/10 (arquivo de voz do sintetizador). Ainda não conferido se houve nova verificação com sucesso.
- Relógio com data futura (26/10/2026 a 25/09/2029): 19 urnas, cerca de 64 linhas cada, todas também com 25/10.
  O padrão é de relógio ajustado errado num ligamento de teste.
- Votos depois das 19h: 2 (SP, 19h00min25s e 19h00min57s; eleitores que estavam na fila).

## O que ainda NÃO foi testado (os testes mais fortes)

1. **Fotos dos boletins impressos (QR code) x arquivos publicados.** É o único teste 100% fora do TSE. Precisa de fotos de fiscais e eleitores.
2. **Verificação criptográfica completa do 2º turno** (assinatura digital e certificados, e recontagem do RDV). A ferramenta DataUrnas-BR fez isso no 1º turno, sem divergência.
3. **Todas as seções do 2º turno.** A varredura de cerca de 517 mil seções está em andamento (mais da metade lida).
4. **Modelo de urna dentro do mesmo local de votação**, para a hipótese de adulteração no software.
5. **Aglomerado do sul do MS, seção por seção.**
6. **Para onde foram os eleitores da terceira via.** Precisa de pesquisa pós-eleitoral.

## Como reproduzir
Scripts em `scripts/`; dados pequenos em `dados/`. Fontes: cdn.tse.jus.br (dados abertos) e
resultados.tse.jus.br/oficial/ele2026 (pleito 3221, eleição 6258). Ordem sugerida no README.
