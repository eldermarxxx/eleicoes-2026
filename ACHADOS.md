# Auditoria independente – Eleição presidencial 2026 (2º turno)

**Status: varredura completa concluída** (26/10/2026). Os números do 2º turno fecham com o oficial.
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

### Varredura total (COMPLETA: 499.207 BUs lidos de 517.179 seções; 17.823 agregadas)
- **Recontagem pelos BUs: Lula 64.256.232 e Flávio 59.826.041. Oficial: idêntico, diferença zero.** (51,79%)
- Brancos 1.430.496; nulos 2.723.305.
- SHA-512 fora do manifesto assinado: **0**. Voto sem habilitação: **0**. Intervalo <10s entre votos: **0**.
- Correlação, dentro da UF, de voto rápido (<8s) com a virada de Lula: +0,044; de voto sem biometria: -0,035.
- Votos depois das 17h: 34.221 de 128,1 milhões (0,027%). Depois das 19h: 11.
- Log x BU no comparecimento: 1.435 divergências (0,3%), compatíveis com urnas trocadas durante o dia. 2.631 urnas votaram como contingência registrada.
- **Urnas cujo código de carga não consta em nenhuma tabela oficial: 51** (0,010%). Somam 7.231 votos de Lula e 5.346 de Flávio (57,5% x 42,5%);
  nas mesmas seções no 1º turno: 6.395 x 5.257 (54,9% x 45,1%). Estão em AP, PA, SE, BA, MG, MA, SP, PR, AC, MT, RO, sem padrão de partido.
  Falha de registro de custódia, a ser perguntada ao TSE. Impacto máximo: ordem de 1 mil votos de diferença, contra margem de 4,43 milhões.
  Observação: 7 urnas de Aracaju-SE (zona 2) ligadas ao mesmo computador de carga (RSEWGM04) têm 2 a 4 códigos de carga no histórico; pergunta para o TSE, não acusação.
- Verificação de assinatura com ERRO nos logs: 125 urnas (quase todas na carga, em setembro). Não conferido se houve nova verificação com sucesso.
- Relógio voltou no dia: 101 urnas. Datas futuras (26/10 a 31/10) em dezenas de urnas, em ligamentos de teste.
- Status no índice: 478.154 "Totalizada", 21.053 "Recebida" (o BU foi lido e somado e o total fechou), 41 "Não instalada", 108 sem arquivo (404).

### Seções "sinalizadas" (≥1 voto sem biometria após 17h) x demais da mesma zona
Critério sugerido pela análise independente de samuraitrc (<https://github.com/samuraitrc/eleicoes-2026-analises>), aplicado aos BUs de todas as seções. Script: `scripts/teste_sinalizadas.py`.
- 5.444 seções sinalizadas (ele achou 5.244; método de fuso diferente), 2.070 zonas com controles. Somam **5.699 votos** sem biometria após 17h.
- Virada de Lula (2º menos 1º turno) nas sinalizadas menos controles da mesma zona: **+0,12 p.p.** (IC95% +0,06 a +0,18). Efeito minúsculo: cerca de 1,8 mil votos líquidos sobre 1,5 milhão de votos dessas seções.
- Dose-resposta: mais votos sem biometria após 17h não dá mais virada (correlação -0,06).
- Mesmo que todos os 5.699 votos fossem de Lula, seriam 0,1% da margem de 4,43 milhões.

## O que ainda NÃO foi testado (os testes mais fortes)

1. **Fotos dos boletins impressos (QR code) x arquivos publicados.** É o único teste 100% fora do TSE. Precisa de fotos de fiscais e eleitores.
2. **Verificação criptográfica completa do 2º turno** (assinatura digital e certificados, e recontagem do RDV). A ferramenta DataUrnas-BR fez isso no 1º turno, sem divergência.
3. ~~Todas as seções do 2º turno~~ **Feito**: recontagem completa idêntica ao oficial.
4. **Modelo de urna dentro do mesmo local de votação**, para a hipótese de adulteração no software.
5. **Aglomerado do sul do MS, seção por seção.**
6. **Para onde foram os eleitores da terceira via.** Precisa de pesquisa pós-eleitoral.

## Como reproduzir
Scripts em `scripts/`; dados pequenos em `dados/`. Fontes: cdn.tse.jus.br (dados abertos) e
resultados.tse.jus.br/oficial/ele2026 (pleito 3221, eleição 6258). Ordem sugerida no README.
