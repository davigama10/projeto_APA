import os
import numpy as np
import pandas as pd
import time
from main import inicializar_instancia, heuristica_gulosa, calcular_custo_total, VND, grasp

# Caminho para a pasta com os arquivos de entrada
pasta_instancias = 'instancias_teste3'
arquivos = sorted([f for f in os.listdir(pasta_instancias) if f.endswith('.txt')])

# Lista para armazenar os resultados
resultados = []

for arquivo in arquivos:
    caminho = os.path.join(pasta_instancias, arquivo)
    print(f"\n📂 Lendo instância: {arquivo}")

    # Inicializa dados da instância
    with open(caminho, 'r') as f:
        linhas = f.readlines()
        numero_de_voos = int(linhas[0].strip())
        numero_de_pistas = int(linhas[1].strip())
        r = list(map(int, linhas[3].split()))
        c = list(map(int, linhas[4].split()))
        p = list(map(int, linhas[5].split()))
        t = [list(map(int, linha.split())) for linha in linhas[7:]]

    # Gera solução inicial
    voos, pistas, matriz_tempo = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
    voos_g, pistas_g, matriz_tempo_g = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
    heuristica_gulosa(voos, pistas, matriz_tempo)
    custo_guloso = calcular_custo_total(voos)

    # Aplica VND
    custo_final = VND(voos, pistas, matriz_tempo)
    
    resultado_grasp, solucoes_grasp = grasp(voos_g, pistas_g, matriz_tempo_g, max_iteracoes=15, alpha=0.3)

    print(type(resultado_grasp))
    
    # Pega o valor otimo
    pd_otimos = pd.read_csv('instancias_opt.csv', sep=',').drop(columns=['Unnamed: 0'])
    valor_otimo = int(pd_otimos.loc[pd_otimos['instancias'] == arquivo, 'valor_otimo'])
    
    # Armazena resultado
    resultados.append((arquivo, valor_otimo, custo_guloso, custo_final, resultado_grasp, np.mean(solucoes_grasp)))

    
    
# Exibe resultados
print("\n📊 RESULTADOS:")
print(f"{'Instância':<15} {'OTIMO':<10} {'GULOSO':<10} {'VND':<10} {'GRASP':<10} {'M_GRASP':<10}")
print("-" * 80)
for nome, valor_otimo, c_guloso, c_vnd, c_grasp, mean_grasp in resultados:
    print(f"{nome:<15} {valor_otimo:<10} {c_guloso:<10} {c_vnd:<10} {c_grasp:<10} {mean_grasp:<10.2f}")
