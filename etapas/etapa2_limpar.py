import pandas as pd
from pathlib import Path


DADOS = Path(__file__).parent.parent / "dados"
df = pd.read_excel(DADOS / "ICB_DADOS_2026.xlsx")
print("Linhas no início:", len(df))

# PASSO 1 - Unificar nomes de produtos
nomes = {
    "Carne Acem":       "Carne Bovina Acem",
    "Carne Coxão Mole": "Carne Bovina Coxão Mole",
    "Carne Pernil":     "Carne Suína Pernil",
    "Pernil":           "Carne Suína Pernil",
    "Farinha":          "Farinha de Trigo",
    "Macarrão":         "Macarrão com Ovos",
    "Pão":              "Pão Francês",
}
df["Produto"] = df["Produto"].replace(nomes)

# não dá para analisar tendências de alimentos que aparecem poucas vezes, então removemos.
raros = ["Carne Bovina Alcatra", "Carne Bovina Músculo", "Carne Bovina Patinho"]
df = df[~df["Produto"].isin(raros)]       # ~ significa "NÃO"
print("Linhas após remover produtos raros:", len(df))


# PASSO 2 - Remover preços absurdos (outliers)
# Um registro é considerado erro se for mais de 3x MAIOR
# ou mais de 3x MENOR que essa mediana.
# Comparar só com o mesmo mês evita que preços de outros
# meses (inclusive do futuro) influenciem a regra.
mediana_mes = df.groupby(["Mes_Ano_Data", "Produto"])["PPK"].transform("median")
razao = df["PPK"] / mediana_mes        
outlier = (razao > 3) | (razao < 1/3)

print("\nOutliers encontrados:", outlier.sum())
print(df[outlier][["Mes_Ano_Data", "Estab", "Produto", "Preco", "Quantidade", "PPK"]]
      .sort_values("Produto").to_string())

df = df[~outlier]
print("\nLinhas após remover outliers:", len(df))

# PASSO 3 - Um preço por mercado, produto e mês
# Um mercado pode ter várias marcas do mesmo produto no mesmo mês.
# Ficamos com a MEDIANA delas: o preço "típico" daquele mercado.
mensal = (df.groupby(["Mes_Ano_Data", "Estab", "Produto"], as_index=False)["PPK"]
            .median())
print("\nLinhas na tabela mensal:", len(mensal))

# PASSO 4 - Salvar
df.to_csv(DADOS / "registros_limpos.csv", index=False)
mensal.to_csv(DADOS / "preco_mensal_mercado.csv", index=False)
print("\nArquivos salvos na pasta dados/")