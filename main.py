with open('entrada.txt', 'r') as f:
    linhas = [linha.strip() for linha in f if linha.strip()]


numero_de_voos = int(linhas[0])
numero_de_pistas = int(linhas[1])


r = list(map(int, linhas[2].split()))
c = list(map(int, linhas[3].split()))
p = list(map(int, linhas[4].split()))

# matriz t
t = []
for i in range(5, 5 + numero_de_voos):
    t.append(list(map(int, linhas[i].split())))


# Representação de um voo
class Voo:
    def __init__(self, id_voo, r, c, p):
        self.id = id_voo
        self.r = r  # horário de chegada
        self.c = c  # horário mais cedo de pouso
        self.p = p  # penalidade por minuto de espera
        self.horario_atribuido = None  # será preenchido na solução
        self.pista_atribuida = None    # idem

# Representação de uma pista
class Pista:
    def __init__(self, id_pista):
        self.id = id_pista
        self.ocupada_em = set()  # horários em que essa pista já está ocupada

# Função que inicializa as estruturas
def inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t):
    voos = [Voo(i, r[i], c[i], p[i]) for i in range(numero_de_voos)]
    pistas = [Pista(i) for i in range(numero_de_pistas)]
    matriz_tempo = t  # matriz t[i][j] = tempo de separação entre voo i e j na mesma pista
    return voos, pistas, matriz_tempo


def printar_instancia(voos, pistas, matriz_tempo):
    print("📦 VOOS:")
    for voo in voos:
        print(
            f"Voo {voo.id}: r = {voo.r}, c = {voo.c}, p = {voo.p}, "
            f"horário atribuído = {voo.horario_atribuido}, pista = {voo.pista_atribuida}"
        )

    print("\n🛬 PISTAS:")
    for pista in pistas:
        print(f"Pista {pista.id}, horários ocupados: {sorted(pista.ocupada_em)}")

    print("\n⏱ MATRIZ DE SEPARAÇÃO (t):")
    for i, linha in enumerate(matriz_tempo):
        print(f"Voo {i}: {linha}")


def heuristica_gulosa(voos, pistas, matriz_tempo):
    custo_total = 0

    # Ordena os voos pelo tempo de liberação
    voos_ordenados = sorted(voos, key=lambda v: v.r)

    for voo in voos_ordenados:
        melhor_inicio = float('inf')
        melhor_pista = None

        for pista in pistas:
            # Tenta alocar o voo no tempo mais cedo possível respeitando separação
            tempo_minimo = voo.r

            for outro_voo in voos:
                if outro_voo.pista_atribuida == pista.id and outro_voo.horario_atribuido is not None:
                    tempo_final = outro_voo.horario_atribuido + outro_voo.c
                    separacao = matriz_tempo[outro_voo.id][voo.id]
                    tempo_minimo = max(tempo_minimo, tempo_final + separacao)

            # Verifica se essa pista é melhor que a anterior
            if tempo_minimo < melhor_inicio:
                melhor_inicio = tempo_minimo
                melhor_pista = pista

        # Atribui voo à pista escolhida
        voo.horario_atribuido = melhor_inicio
        voo.pista_atribuida = melhor_pista.id

        # Marca os horários ocupados
        for t in range(voo.horario_atribuido, voo.horario_atribuido + voo.c):
            melhor_pista.ocupada_em.add(t)

        # Calcula custo de penalidade
        atraso = max(0, voo.horario_atribuido - voo.r)
        penalidade = atraso * voo.p
        custo_total += penalidade

    print(f"\n💸 Custo total de penalidade: {custo_total}")







voos, pistas, matriz_tempo = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
heuristica_gulosa(voos, pistas, matriz_tempo)
printar_instancia(voos, pistas, matriz_tempo)

