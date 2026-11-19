# Garrafas são de fato menores? Tamanho aparente de criadouros de *Aedes aegypti* em vídeos aéreos da base MBG

Repositório de reprodutibilidade do projeto final de **Métodos de Computação Experimental e Quantitativa (MCEQ 12576)**, PUC-Campinas, 2º semestre de 2026.

**Autores:** Gabriel Medeia de Campos ([e-mail]) e Enzo Pampana Garofalo (enzo.garofalo07@gmail.com), Engenharia de Software, PUC-Campinas.

- Artigo: [`artigo.pdf`](artigo.pdf)
- Vídeo da equipe (YouTube, não listado): [link do vídeo]
- Protocolo pré-registrado (18/11/2026): [`protocolo.pdf`](protocolo.pdf)

---

## 1. Pergunta e hipóteses

Silva Zendron et al. (CISTI 2024) obtiveram mAP@.5 de apenas 0,58 na classe *garrafa* com YOLOv7 e atribuíram o resultado ao tamanho reduzido das garrafas nas imagens de drone, mas não mediram esse tamanho. Este estudo testa essa explicação usando somente as anotações públicas da base MBG.

**Pergunta:** nos vídeos da base MBG usados pelos autores (02, 06, 09 e 12), as garrafas ocupam área relativa menor na imagem do que os demais objetos anotados?

Sendo η a mediana da área relativa por objeto:

- **H0:** η_garrafa = η_demais
- **H1 (unilateral):** η_garrafa < η_demais

**Tipo de estudo:** observacional. A classe do objeto não foi atribuída por sorteio, e por isso não fazemos afirmações causais.

## 2. Base de dados

| Campo | Valor |
|---|---|
| Nome | Mosquito Breeding Grounds (MBG) Database, v1 |
| Autoria | SMT/COPPE/UFRJ (Passos et al., 2022) |
| Fonte | https://www02.smt.ufrj.br/~tvdigital/database/mosquito/ |
| Data de acesso | 18/11/2026 |
| Licença | [preencher conforme a página da base] |
| Arquivos usados | XMLs de anotação (formato CVAT) dos vídeos 02, 06, 09 e 12 |
| Medição original | Vídeos gravados com drone em trajetória pré-programada; anotação manual quadro a quadro no CVAT; cada objeto é um *track* com identificador próprio |

| Vídeo | Altitude | Resolução |
|---|---|---|
| 02 | 15 m | 3840 × 2160 px |
| 06 | 16 m | 3840 × 2160 px |
| 09 | 40 m | 3840 × 2160 px |
| 12 | 40 m | 4096 × 2160 px |

As altitudes vêm de Passos et al. (2022). **Premissa:** a numeração dos vídeos em Silva Zendron et al. coincide com a da base.

> **Redistribuição dos dados.** [Escolher uma das opções conforme a licença.]
> - *A licença permite:* os XMLs originais estão em `dados/brutos/`, sem nenhuma alteração.
> - *A licença não permite ou não está clara:* `dados/brutos/` está vazia. Baixe os XMLs dos vídeos 02, 06, 09 e 12 na página da base e salve-os nessa pasta (ver Seção 4).

## 3. Estrutura do repositório

```
.
├── README.md
├── requirements.txt
```

## 4. Como reexecutar

Requisito: Python 3.13.

```bash
# 1. Clonar o repositório
git clone [link do repositório]
cd [nome-do-repositorio]

# 2. Criar o ambiente e instalar as dependências
python3.13 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. (Somente se dados/brutos/ estiver vazia) baixar os XMLs dos vídeos
#    02, 06, 09 e 12 na página da MBG e salvá-los em dados/brutos/

# 4. Rodar o pipeline completo
bash run_all.sh
```

Também é possível rodar cada etapa separadamente:

```bash
python scripts/01_extrair.py   # gera dados/limpos/objetos.csv
python scripts/02_analise.py   # gera resultados/tabela1.csv e resultados/testes.txt
python scripts/03_figura.py    # gera resultados/figura1.png
```

Todo sorteio (teste de permutação e bootstrap) usa a semente fixa `numpy.random.default_rng(2026)`, então os resultados são idênticos a cada execução.

## 5. O que cada script faz

**`01_extrair.py`**: lê os XMLs CVAT e gera uma linha por objeto (*track*). Para cada objeto, calcula a área relativa em cada quadro em que ele está visível como (largura × altura da *bounding box*) / (largura × altura do quadro) e guarda a **mediana** desses valores, em % do quadro. A área relativa compensa a diferença de resolução entre os vídeos. Usar o objeto como unidade de análise (e não o quadro) evita pseudorreplicação, porque o mesmo objeto aparece em dezenas de quadros seguidos. Nenhum objeto é excluído: todos têm ao menos 10 quadros visíveis. Total: **96 objetos**.

Colunas de `objetos.csv`: `video`, `altitude_m`, `track_id`, `classe`, `grupo` (garrafa/demais), `n_quadros`, `area_rel_pct`.

**`02_analise.py`**: aplica a regra do protocolo e roda as análises (Seção 6).

**`03_figura.py`**: gera a Figura 1, com a área relativa de cada objeto por classe em escala log (círculos para 15–16 m, triângulos para 40 m e um traço na mediana de cada classe).

## 6. Análise: confirmatória × exploratória

### Regra fixada no protocolo (18/11/2026)

- Se os vídeos a 40 m tivessem **≥ 10 garrafas**, a análise usaria só esses vídeos.
- Caso contrário, o teste seria aplicado em cada estrato de altitude, com **α = 0,025** (correção de Bonferroni).
- Teste principal: Mann-Whitney unilateral. Teste alternativo, previsto para n < 10 em algum grupo: permutação da diferença de medianas (10.000 permutações).
- Tamanho de efeito: delta de Cliff, com IC de 95% por bootstrap (10.000 reamostragens).

### Aplicação da regra

Os vídeos 09 e 12 (40 m) não contêm garrafas, então a análise foi estratificada. O estrato de 40 m não admite o teste, e o de 15–16 m tem 8 garrafas (< 10), o que aciona o teste de permutação. Foi feito **um único teste confirmatório**.

### Análises exploratórias (fora do protocolo)

Aparecem em `resultados/testes.txt` sob o rótulo `EXPLORATÓRIA`:

- (a) Kruskal-Wallis entre as classes com 3 ou mais objetos;
- (b) comparação descritiva entre a área das garrafas a 15–16 m e a de pneus, baldes e piscinas a 40 m.

## 7. Correspondência com o artigo e resultados esperados

| Saída | No artigo |
|---|---|
| `resultados/tabela1.csv` | Tabela 1 |
| `resultados/figura1.png` | Figura 1 |
| `resultados/testes.txt` | Seção 4 (teste confirmatório e análises exploratórias) |

Depois de rodar o pipeline, você deve obter exatamente estes valores:

| Resultado | Valor |
|---|---|
| Objetos analisados | 96 |
| Garrafas, 15–16 m: n, mediana (IIQ) | 8; 0,017% (0,014–0,030) |
| Demais, 15–16 m: n, mediana (IIQ) | 27; 0,127% (0,094–0,180) |
| Diferença de medianas (IC 95%) | −0,110 p.p. [−0,140; −0,080] |
| Permutação unilateral | p < 0,001 |
| Mann-Whitney unilateral | U = 6; p < 0,001 |
| Delta de Cliff (IC 95%) | −0,94 [−1,00; −0,81] |
| Kruskal-Wallis (exploratória) | H = 44,8; p < 0,001 |

## 8. Ambiente

Python 3.13, NumPy 2.5, pandas 3.0, SciPy 1.18 e [biblioteca da figura + versão]. As versões exatas estão em `requirements.txt`.

## 9. Limitações principais

- Há apenas 8 garrafas, e 7 delas vêm do vídeo 02, então o grupo garrafa se confunde com a cena desse vídeo.
- A *bounding box* mede o retângulo anotado, não o objeto em si, e a área relativa não equivale à área vista pela rede após o redimensionamento.
- Os resultados valem apenas para os quatro vídeos analisados e não se estendem à base completa nem à MBG-V2.

A discussão completa está na Seção 5 do artigo.

## 10. Uso de Inteligência Artificial

Utilizamos o Claude (Anthropic) para discutir o protocolo, gerar os scripts de extração, análise e figura e redigir uma versão preliminar do texto. Todos os números foram produzidos pela execução deste código e conferidos pela equipe.

## 11. Referências

- Passos, W. L. et al. 2022. Automatic detection of *Aedes aegypti* breeding grounds based on deep networks with spatio-temporal consistency. *Computers, Environment and Urban Systems* 93, 101754.
- Silva Zendron, L. A. et al. 2026. Innovative mosquito breeding site detection: leveraging YOLOv7 with transformer technology. In *CISTI 2024*, LNNS v. 1753, Springer. https://doi.org/10.1007/978-3-032-12888-1_12
- Cliff, N. 1993. Dominance statistics: ordinal analyses to answer ordinal questions. *Psychological Bulletin* 114(3), 494–509. https://doi.org/10.1037/0033-2909.114.3.494
- SMT/COPPE/UFRJ. Mosquito Breeding Grounds (MBG) Database. https://www02.smt.ufrj.br/~tvdigital/database/mosquito/. Acesso em: 18 nov. 2026.
