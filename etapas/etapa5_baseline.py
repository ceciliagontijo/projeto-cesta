import pandas as pd
import numpy as np
from pathlib import Path

DADOS = Path(__file__).parent.parent / "dados"
mensal = pd.read_csv(DADOS / "preco_mensal_mercado.csv", parse_dates=["Mes_Ano_Data"])

# Para cada produto e mês, o preço "típico" = mediana entre os mercados.
series = mensal.groupby(["Produto", "Mes_Ano_Data"])["PPK"].median().unstack("Produto")

# Só os produtos que têm preço nos 48 meses
series = series.dropna(axis=1)
print("Produtos com série completa:", list(series.columns))
print("Meses:", len(series))


# Os modelos (cada um recebe o passado e devolve 1 previsão)
def ingenuo(passado):
    # "o mês que vem vai ser igual a este mês"
    return passado[-1]

def media_movel(passado, janela=3):
    # média dos últimos 3 meses
    return np.mean(passado[-janela:])

modelos = {"Ingênuo": ingenuo, "Média móvel (3)": media_movel}

# Teste de previsão a partir do mês 25 
INICIO_TESTE = 24

linhas = []
for produto in series.columns:
    valores = series[produto].values          # os 48 preços, em ordem
    for t in range(INICIO_TESTE, len(valores)):
        passado = valores[:t]                  # tudo ANTES do mês t
        real = valores[t]                     
        for nome, modelo in modelos.items():
            linhas.append({"Produto": produto,
                           "Mes_Ano_Data": series.index[t],
                           "Modelo": nome,
                           "Real": real,
                           "Previsto": modelo(passado)})

previsoes = pd.DataFrame(linhas)
print("Previsões feitas:", len(previsoes))

# Medir os erros
previsoes["Erro"] = previsoes["Previsto"] - previsoes["Real"]

def metricas(g):
    return pd.Series({
        "MAE":  g["Erro"].abs().mean(),                          # erro médio em R$
        "RMSE": np.sqrt((g["Erro"] ** 2).mean()),                # pune erros grandes
        "MAPE": 100 * (g["Erro"].abs() / g["Real"]).mean(),      # erro médio em %
    })

erros = previsoes.groupby(["Produto", "Modelo"]).apply(metricas).reset_index()

print("\nMAPE (%) por produto e modelo:")
print(erros.pivot(index="Produto", columns="Modelo", values="MAPE").round(1).to_string())

print("\nMédia geral por modelo:")
print(erros.groupby("Modelo")[["MAE", "RMSE", "MAPE"]].mean().round(2).to_string())

series.to_csv(DADOS / "series_produtos.csv")
previsoes.to_csv(DADOS / "previsoes.csv", index=False)
erros.to_csv(DADOS / "erros_modelos.csv", index=False)
print("\nArquivos salvos: series_produtos.csv, previsoes.csv, erros_modelos.csv")