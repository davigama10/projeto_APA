import os
from main_2 import inicializar_instancia, heuristica_gulosa, calcular_custo_total, VND, printar_instancia

# Caminho para a pasta com os arquivos de entrada
pasta_instancias = 'instancias_teste'
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
    heuristica_gulosa(voos, pistas, matriz_tempo)
    custo_guloso = calcular_custo_total(voos)

    # Aplica VND
    custo_final = VND(voos, pistas, matriz_tempo)

    # Armazena resultado
    resultados.append((arquivo, custo_guloso, custo_final))

# Exibe resultados
print("\n📊 RESULTADOS:")
print(f"{'Instância':<15} {'Guloso':<10} {'VND':<10}")
print("-" * 35)
for nome, c_guloso, c_vnd in resultados:
    print(f"{nome:<15} {c_guloso:<10} {c_vnd:<10}")
