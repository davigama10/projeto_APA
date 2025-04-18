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
        self.c = c  # tempo necessário pra decolar/pousar
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


def movimento_trocar_pistas(voos, pistas, matriz_tempo):
    import copy
    nova_solucao = copy.deepcopy(voos)

    for i in range(len(nova_solucao)):
        for j in range(i + 1, len(nova_solucao)):
            voo1 = nova_solucao[i]
            voo2 = nova_solucao[j]

            if voo1.pista_atribuida != voo2.pista_atribuida:
                # Tenta trocar
                pista1, pista2 = voo1.pista_atribuida, voo2.pista_atribuida

                # Troca as pistas
                voo1.pista_atribuida, voo2.pista_atribuida = pista2, pista1

                # Tenta recalcular horários
                sucesso = tentar_recalcular_horario(voo1, nova_solucao, matriz_tempo) and \
                          tentar_recalcular_horario(voo2, nova_solucao, matriz_tempo)

                if sucesso:
                    return nova_solucao  # vizinho viável encontrado

                # Reverte
                voo1.pista_atribuida, voo2.pista_atribuida = pista1, pista2
    return None  # nenhum vizinho viável


def movimento_ajustar_horario(voos, matriz_tempo):
    import copy
    nova_solucao = copy.deepcopy(voos)

    for voo in nova_solucao:
        for delta in [-5, 5]:
            novo_horario = voo.horario_atribuido + delta
            if novo_horario < voo.r:
                continue  # não pode antes do release

            # testa viabilidade
            pista_voos = [v for v in nova_solucao if v.pista_atribuida == voo.pista_atribuida and v.id != voo.id]

            if eh_horario_valido(voo, novo_horario, pista_voos, matriz_tempo):
                voo.horario_atribuido = novo_horario
                return nova_solucao

    return None


def movimento_trocar_ordem_pista(voos, matriz_tempo):
    import copy
    nova_solucao = copy.deepcopy(voos)

    pistas_ids = list(set(v.pista_atribuida for v in voos))
    for pista_id in pistas_ids:
        voos_na_pista = sorted([v for v in nova_solucao if v.pista_atribuida == pista_id], key=lambda x: x.horario_atribuido)
        for i in range(len(voos_na_pista) - 1):
            v1, v2 = voos_na_pista[i], voos_na_pista[i + 1]
            v1_idx, v2_idx = v1.id, v2.id

            # troca ordem
            v1.horario_atribuido, v2.horario_atribuido = None, None

            # troca ids na lista
            voos_na_pista[i], voos_na_pista[i + 1] = v2, v1

            # tenta reatribuir horários
            tempo_atual = 0
            viavel = True
            for v in voos_na_pista:
                inicio = max(v.r, tempo_atual)
                if not eh_horario_valido(v, inicio, voos_na_pista, matriz_tempo):
                    viavel = False
                    break
                v.horario_atribuido = inicio
                tempo_atual = inicio + v.c + matriz_tempo[v.id][v.id]  # separação entre ele mesmo e o próximo

            if viavel:
                return nova_solucao

    return None


def eh_horario_valido(voo, novo_horario, outros_voos, matriz_tempo):
    fim_novo = novo_horario + voo.c
    for outro in outros_voos:
        if outro.horario_atribuido is None:
            continue
        fim_outro = outro.horario_atribuido + outro.c
        if voo.id == outro.id:
            continue

        # Respeita separação entre voos
        if voo.pista_atribuida == outro.pista_atribuida:
            sep = matriz_tempo[outro.id][voo.id]
            if not (novo_horario >= fim_outro + sep or fim_novo + matriz_tempo[voo.id][outro.id] <= outro.horario_atribuido):
                return False
    return True

def tentar_recalcular_horario(voo, todos_voos, matriz_tempo):
    pista_voos = [v for v in todos_voos if v.pista_atribuida == voo.pista_atribuida and v.id != voo.id]

    t = voo.r
    while t < 200:  # limite arbitrário
        if eh_horario_valido(voo, t, pista_voos, matriz_tempo):
            voo.horario_atribuido = t
            return True
        t += 1
    return False


def calcular_custo_total(voos):
    return sum(max(0, v.horario_atribuido - v.r) * v.p for v in voos)


def VND(voos_iniciais, pistas_iniciais, matriz_tempo):
    import copy
    voos_atual = copy.deepcopy(voos_iniciais)
    pistas_atual = pistas_iniciais
    custo_atual = calcular_custo_total(voos_atual)

    movimentos = [
        movimento_trocar_pistas,
        movimento_ajustar_horario,
        movimento_trocar_ordem_pista
    ]

    k = 0
    while k < len(movimentos):
        movimento = movimentos[k]

        # 🔧 Corrigido aqui
        if movimento == movimento_trocar_pistas:
            nova_solucao = movimento(voos_atual, pistas_atual, matriz_tempo)
        else:
            nova_solucao = movimento(voos_atual, matriz_tempo)

        if nova_solucao:
            novo_custo = calcular_custo_total(nova_solucao)
            if novo_custo < custo_atual:
                print(f"\n✅ Movimento {k+1} melhorou a solução: {custo_atual} → {novo_custo}")
                voos_atual = nova_solucao
                custo_atual = novo_custo
                k = 0  # reinicia
                continue

        k += 1

    return voos_atual, custo_atual





import time

# Gera solução inicial com heurística gulosa
voos, pistas, matriz_tempo = inicializar_instancia(numero_de_voos, numero_de_pistas, r, c, p, t)
printar_instancia(voos, pistas, matriz_tempo)
print('\n\n ===============================')
heuristica_gulosa(voos, pistas, matriz_tempo)



custo_inicial = calcular_custo_total(voos)
print(f"\n💡 Custo inicial da solução gulosa: {custo_inicial}")
'''
# Executa VND
inicio = time.time()
solucao_final, custo_final = VND(voos, pistas, matriz_tempo)
fim = time.time()

print("\n🎯 RESULTADO FINAL APÓS VND")
print(f"🔸 Melhor custo encontrado: {custo_final}")
print(f"⏱ Tempo de execução: {fim - inicio:.4f} segundos")

# Se quiser mostrar a solução final detalhada:
print("\n📦 Atribuições finais dos voos:")
for voo in sorted(solucao_final, key=lambda v: v.horario_atribuido):
    atraso = max(0, voo.horario_atribuido - voo.r)
    custo = atraso * voo.p
    print(f"Voo {voo.id} → Pista {voo.pista_atribuida} | Início: {voo.horario_atribuido} | Duração: {voo.c} | Atraso: {atraso} | Penalidade: {custo}")
'''