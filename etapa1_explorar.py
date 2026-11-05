import pandas as pd   

df = pd.read_excel("dados/ICB_DADOS_2026.xlsx")

print("Tamanho (linhas, colunas):", df.shape)
print("\nPrimeiras linhas:")
print(df.head())          # mostra as 5 primeiras linhas

print("\nTipo de cada coluna:")
print(df.dtypes)          # texto, número ou data?

print("\nPrimeiro mês:", df["Mes_Ano_Data"].min())
print("Último mês:", df["Mes_Ano_Data"].max())
print("Quantidade de meses:", df["Mes_Ano_Data"].nunique())   # nunique = nº de valores diferentes

print("\nRegistros por produto:")
print(df["Produto"].value_counts())   # conta quantas vezes cada produto aparece

print("\nQuantidade de mercados:", df["Estab"].nunique())
meses_por_mercado = df.groupby("Estab")["Mes_Ano_Data"].nunique()
print("Em quantos meses cada mercado aparece:")
print(meses_por_mercado.sort_values())

print("\nResumo dos preços por kg (PPK):")
print(df["PPK"].describe())    # mínimo, máximo, média, quartis

print("\nValores faltando em cada coluna:")
print(df.isna().sum())