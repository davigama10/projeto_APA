import os
import numpy as np
import pandas as pd
import time
from main import inicializar_instancia, heuristica_gulosa, calcular_custo_total, VND, grasp

# Caminho para a pasta com os arquivos de entrada
pasta_instancias = 'instancias_teste3'
arquivos = sorted([f for f in os.listdir(pasta_instancias) if f.endswith('.txt')])

# Lê os valores ótimos
pd_otimos = pd.read_csv('instancias_opt.csv', sep=',').drop(columns=['Unnamed: 0'])

# Lista para armazenar os resultados
tabela_resultados = []

for arquivo in arquivos:
    print(f"\n📂 Executando instância: {arquivo}")
    caminho = os.path.join(pasta_instancias, arquivo)

    with open(caminho, 'r') as f:
        linhas = f.readlines()
        numero_de_voos = int(linhas[0].strip())
        numero_de_pistas = int(linhas[1].strip())
        r = list(map(int, linhas[3].split()))
        c = list(map(int, linhas[4].split()))
        p = list(map(int, linhas[5].split()))
        t = [list(map(int, linha.split())) for linha in linhas[7:]]

    valor_otimo = int(pd_otimos.loc[pd_otimos['instancias'] == arquivo, 'valor_otimo'])

    # Execuções múltiplas para cada heurística
    tempos_g, solucoes_g = [], []
    tempos_vnd, solucoes_vnd = [], []
    tempos_grasp, solucoes_grasp = [], []

    # GULOSA
    voos_g, pistas_g, matriz_tempo_g = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
    start = time.time()
    heuristica_gulosa(voos_g, pistas_g, matriz_tempo_g)
    end = time.time()
    custo_g = calcular_custo_total(voos_g)
    solucoes_g.append(custo_g)
    tempos_g.append(end - start)

    # VND
    voos_v, pistas_v, matriz_tempo_v = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
    heuristica_gulosa(voos_v, pistas_v, matriz_tempo_v)
    start = time.time()
    custo_vnd = VND(voos_v, pistas_v, matriz_tempo_v)
    end = time.time()
    solucoes_vnd.append(custo_vnd)
    tempos_vnd.append(end - start)

    # GRASP
    voos_gr, pistas_gr, matriz_tempo_gr = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
    start = time.time()
    melhor_grasp, historico = grasp(voos_gr, pistas_gr, matriz_tempo_gr, max_iteracoes=10, alpha=0.3)
    end = time.time()
    solucoes_grasp.append(melhor_grasp)
    tempos_grasp.append(end - start)


    def calc_gap(media, otimo):
        return ((media - otimo) / otimo) * 100

    linha = {
        'Instância': arquivo,
        'Otimo': valor_otimo,
        'Melhor_Gulosa': min(solucoes_g),
        'Média_Gulosa': np.mean(solucoes_g),
        'Tempo_Gulosa': np.mean(tempos_g),
        'GAP_Gulosa': calc_gap(np.mean(solucoes_g), valor_otimo),

        'Melhor_VND': min(solucoes_vnd),
        'Média_VND': np.mean(solucoes_vnd),
        'Tempo_VND': np.mean(tempos_vnd),
        'GAP_VND': calc_gap(np.mean(solucoes_vnd), valor_otimo),

        'Melhor_GRASP': min(solucoes_grasp),
        'Média_GRASP': np.mean(historico),
        'Tempo_GRASP': np.mean(tempos_grasp),
        'GAP_GRASP': calc_gap(np.mean(solucoes_grasp), valor_otimo)
    }

    tabela_resultados.append(linha)

# Salva CSV
df_resultados = pd.DataFrame(tabela_resultados)
df_resultados.to_csv("resultados.csv", index=False)

print("\n✅ Resultados salvos no arquivo resultados.csv")
