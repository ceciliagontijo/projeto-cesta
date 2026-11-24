# Preços da Cesta Básica em Campinas

Projeto de extensão: exploração de 48 meses (set/2022 a ago/2026) de preços de itens da cesta básica coletados em supermercados de Campinas.

O projeto responde duas questões:

1. **Previsão de preços:** é possível prever o preço de cada produto no mês seguinte melhor do que repetir o preço do mês atual?
2. **Custo da cesta entre mercados:** quanto se economiza escolhendo o mercado, e os mercados mais baratos são sempre os mesmos?

A explicação completa dos métodos e dos resultados está no relatório técnico.

## Estrutura

```
projeto-cesta/
├── dados/
│   ├── ICB_DADOS_2026.xlsx        ← base original (nunca é alterada)
│   └── *.csv                      ← arquivos gerados pelos scripts
├── etapas/
│   ├── etapa1_explorar.py
│   ├── etapa2_limpar.py
│   ├── etapa3_cesta.py
│   ├── etapa4_ranking.py
│   ├── etapa5_baseline.py
│   ├── etapa6_arima.py
│   └── etapa7_random_forest.py
├── cesta_exploracao.pbix          ← painéis do Power BI
├── requirements.txt
└── README.md
```

## Scripts

| Script | O que faz | Gera |
| --- | --- | --- |
| `etapa1_explorar.py` | Exploração inicial: período, produtos, mercados, valores faltantes | — |
| `etapa2_limpar.py` | Limpeza: unifica nomes, remove outliers, um preço por mercado/produto/mês | `registros_limpos.csv`, `preco_mensal_mercado.csv` |
| `etapa3_cesta.py` | Custo da cesta (DIEESE) por mercado, economia e validação com o valor oficial | `cesta_mercado_mes.csv`, `cesta_resumo_mensal.csv` |
| `etapa4_ranking.py` | Estabilidade do ranking dos mercados (correlação de Spearman) | `estabilidade_ranking.csv` |
| `etapa5_baseline.py` | Séries por produto, modelos ingênuo e média móvel, validação walk-forward | `series_produtos.csv`, `previsoes.csv`, `erros_modelos.csv` |
| `etapa6_arima.py` | Teste ADF, escolha da ordem pelo AIC e ARIMA | atualiza `previsoes.csv` e `erros_modelos.csv`; `arima_ordens.csv` |
| `etapa7_random_forest.py` | Random Forest com lags e mês do ano | atualiza `previsoes.csv` e `erros_modelos.csv` |

## Como rodar

Requisitos: Python 3.10 ou superior.

```bash
pip install -r requirements.txt

python etapas/etapa1_explorar.py
python etapas/etapa2_limpar.py
python etapas/etapa3_cesta.py
python etapas/etapa4_ranking.py
python etapas/etapa5_baseline.py
python etapas/etapa6_arima.py
python etapas/etapa7_random_forest.py
```

- Os scripts devem rodar **nessa ordem**: cada um lê os arquivos gerados pelos anteriores. As etapas 5, 6 e 7 acrescentam seus modelos ao mesmo `previsoes.csv`.
- Os caminhos são relativos à localização dos scripts, então eles podem ser executados de qualquer pasta.
- No macOS, use `python3`; se o pip recusar a instalação ("externally-managed-environment"), crie um ambiente virtual com `python3 -m venv .venv` e `source .venv/bin/activate`.
- O Random Forest usa semente fixa (`random_state=42`), então os resultados são sempre os mesmos.

## Power BI

O arquivo `cesta_exploracao.pbix` (Power BI Desktop, Windows) lê os CSVs da pasta `dados/`. Ao abrir em outro computador, atualize o caminho dos arquivos em **Transformar dados → Configurações da fonte de dados → Alterar fonte**.

Os CSVs usam ponto como separador decimal. No Power BI em português, configure **Arquivo → Opções → Arquivo atual → Configurações regionais → Localidade para importação: Inglês (Estados Unidos)**.

## Fontes

- Base de dados fornecida na disciplina (mesma base do Observatório PUC-Campinas).
- Observatório PUC-Campinas — valores mensais publicados da cesta básica de Campinas.
- DIEESE — Metodologia da Pesquisa Nacional da Cesta Básica de Alimentos (Decreto-Lei 399/1938).
