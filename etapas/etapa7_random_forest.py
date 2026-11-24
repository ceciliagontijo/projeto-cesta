import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor

DADOS = Path(__file__).parent.parent / "dados"
series = pd.read_csv(DADOS / "series_produtos.csv", index_col="Mes_Ano_Data", parse_dates=True)
INICIO_TESTE = 24     # o mesmo das etapas 5 e 6

# transformar preço em variação (%)
# Random Forest prevê a variação do proximo mês, e não o preço
variacao = series.pct_change()          # (preço do mês / preço do mês anterior) - 1



#   var_lag1, var_lag2, var_lag3 = variação dos 3 meses anteriores
#   mes = mês do ano (1 a 12), para captar safra/época
#   Produto = qual produto (cada um vira uma coluna 0/1)
#   alvo = variação deste mês 
linhas = []
for produto in series.columns:
    v = variacao[produto].values
    p = series[produto].values
    for t in range(4, len(series)):        
        linhas.append({"Produto": produto,
                       "Mes_Ano_Data": series.index[t],
                       "t": t,
                       "var_lag1": v[t - 1],
                       "var_lag2": v[t - 2],
                       "var_lag3": v[t - 3],
                       "mes": series.index[t].month,
                       "preco_anterior": p[t - 1],
                       "Real": p[t],
                       "alvo": v[t]})
tabela = pd.DataFrame(linhas)

# Produto como colunas 0/1: Produto_Arroz = 1 se a linha é do arroz
X_todas = pd.get_dummies(tabela[["var_lag1", "var_lag2", "var_lag3", "mes", "Produto"]],
                         columns=["Produto"], dtype=int)
print("Linhas na tabela:", len(tabela), "| Colunas usadas pelo modelo:", X_todas.shape[1])

# treina os meses anteriores para as previsões futuras
resultados = []
for t in range(INICIO_TESTE, len(series)):
    treino = tabela["t"] < t
    teste = tabela["t"] == t

    modelo = RandomForestRegressor(
        n_estimators=300,      # 300 árvores (mais árvores = resultado mais estável)
        min_samples_leaf=5,    # cada "folha" precisa de 5 exemplos: evita decorar ruído
        random_state=42,       # semente fixa: o resultado é sempre o mesmo ao rodar de novo
    )
    modelo.fit(X_todas[treino], tabela.loc[treino, "alvo"])

    var_prevista = modelo.predict(X_todas[teste])
    previsto = tabela.loc[teste, "preco_anterior"].values * (1 + var_prevista)

    parte = tabela.loc[teste, ["Produto", "Mes_Ano_Data", "Real"]].copy()
    parte["Modelo"] = "Random Forest"
    parte["Previsto"] = previsto
    resultados.append(parte)

rf = pd.concat(resultados, ignore_index=True)

# Quais informações o último modelo mais usou?
importancia = pd.Series(modelo.feature_importances_, index=X_todas.columns)
importancia = importancia.sort_values(ascending=False)
print("\nImportância das variáveis (modelo do último mês):")
print(importancia.head(8).round(3).to_string())

# juntar com os outros modelos e comparar
previsoes = pd.read_csv(DADOS / "previsoes.csv", parse_dates=["Mes_Ano_Data"])
previsoes = previsoes[previsoes["Modelo"] != "Random Forest"]   # evita duplicar se rodar 2x
previsoes = pd.concat([previsoes, rf], ignore_index=True)
previsoes["Erro"] = previsoes["Previsto"] - previsoes["Real"]

def metricas(g):
    return pd.Series({
        "MAE":  g["Erro"].abs().mean(),
        "RMSE": np.sqrt((g["Erro"] ** 2).mean()),
        "MAPE": 100 * (g["Erro"].abs() / g["Real"]).mean(),
    })

erros = previsoes.groupby(["Produto", "Modelo"]).apply(metricas).reset_index()

print("\nMAPE (%) por produto e modelo:")
print(erros.pivot(index="Produto", columns="Modelo", values="MAPE").round(1).to_string())
print("\nMédia geral por modelo:")
print(erros.groupby("Modelo")[["MAE", "RMSE", "MAPE"]].mean().round(2).to_string())

previsoes.to_csv(DADOS / "previsoes.csv", index=False)
erros.to_csv(DADOS / "erros_modelos.csv", index=False)
print("\nArquivos salvos: previsoes.csv, erros_modelos.csv")