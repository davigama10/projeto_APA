import copy

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

# GULOSO ========================================================================================================================
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

# VIZINHANÇA ===============================================================================================================

## Funções Auxiliares:
def calcular_custo_total(voos):
    """Calcula o custo total da solução atual"""
    custo = 0
    for voo in voos:
        if voo.horario_atribuido is not None:
            atraso = max(0, voo.horario_atribuido - voo.r)
            custo += atraso * voo.p
    return custo


def recalcular_horarios(voos, pistas, matriz_tempo, pistas_afetadas):
    """
    Recalcula os horários para todas as pistas afetadas.
    Retorna True se conseguiu uma alocação válida, False caso contrário.
    """
    for pista_id in pistas_afetadas:
        if pista_id is None:
            continue  # Ignora pistas não atribuídas

        # Pega todos os voos nesta pista, ordenados pelo horário atual
        voos_pista = [v for v in voos if v.pista_atribuida == pista_id]
        voos_pista.sort(key=lambda v: v.horario_atribuido if v.horario_atribuido is not None else float('inf'))
        
        # Limpa os horários da pista
        pistas[pista_id].ocupada_em = set()
        
        for i, voo in enumerate(voos_pista):
            tempo_minimo = voo.r
            
            # Respeita separação com voo anterior
            if i > 0:
                voo_anterior = voos_pista[i-1]
                tempo_final = voo_anterior.horario_atribuido + voo_anterior.c
                separacao = matriz_tempo[voo_anterior.id][voo.id]
                tempo_minimo = max(tempo_minimo, tempo_final + separacao)
            
            voo.horario_atribuido = tempo_minimo

            # Verifica separação com o próximo voo
            if i < len(voos_pista) - 1:
                voo_proximo = voos_pista[i+1]
                if voo_proximo.horario_atribuido is not None:
                    tempo_final = voo.horario_atribuido + voo.c
                    separacao = matriz_tempo[voo.id][voo_proximo.id]
                    if tempo_final + separacao > voo_proximo.horario_atribuido:
                        return False

            # Marca horários ocupados na pista
            for t in range(voo.horario_atribuido, voo.horario_atribuido + voo.c):
                pistas[pista_id].ocupada_em.add(t)

    return True


def recalcular_horarios_pista(voos_pista, pista, matriz_tempo):
    """
    Recalcula horários para uma única pista com uma nova ordem de voos
    Retorna True se conseguiu uma alocação válida, False caso contrário
    """
    pista.ocupada_em = set()

    for i, voo in enumerate(voos_pista):
        tempo_minimo = voo.r

        if i > 0:
            voo_anterior = voos_pista[i - 1]
            tempo_final = voo_anterior.horario_atribuido + voo_anterior.c
            separacao = matriz_tempo[voo_anterior.id][voo.id]
            tempo_minimo = max(tempo_minimo, tempo_final + separacao)

        voo.horario_atribuido = tempo_minimo

        for t in range(voo.horario_atribuido, voo.horario_atribuido + voo.c):
            pista.ocupada_em.add(t)

    return True


def movimento_swap(voos, pistas, matriz_tempo):
    """
    Tenta trocar dois voos de pista e horário. 
    Retorna (melhorou, nova_solucao_voos, novo_custo).
    """
    melhor_voos = copy.deepcopy(voos)
    melhor_pistas = copy.deepcopy(pistas)
    melhor_custo = calcular_custo_total(melhor_voos)
    melhorou = False

    for i in range(len(voos)):
        for j in range(i + 1, len(voos)):
            copia_voos = copy.deepcopy(voos)
            copia_pistas = copy.deepcopy(pistas)

            voo1 = copia_voos[i]
            voo2 = copia_voos[j]

            # Salva os originais
            pista1_original = voo1.pista_atribuida
            pista2_original = voo2.pista_atribuida
            horario1_original = voo1.horario_atribuido
            horario2_original = voo2.horario_atribuido

            # Realiza a troca
            voo1.pista_atribuida, voo2.pista_atribuida = pista2_original, pista1_original
            voo1.horario_atribuido, voo2.horario_atribuido = horario2_original, horario1_original

            pistas_afetadas = list({pista1_original, pista2_original})

            if recalcular_horarios(copia_voos, copia_pistas, matriz_tempo, pistas_afetadas):
                novo_custo = calcular_custo_total(copia_voos)
                if novo_custo < melhor_custo:
                    melhor_custo = novo_custo
                    melhor_voos = copia_voos
                    melhorou = True
                    print("SWAP --> CUSTO MELHORADO:", melhor_custo)

    return melhorou, melhor_voos, melhor_custo


def movimento_retirar_inserir(voos, pistas, matriz_tempo):
    """
    Remove um voo de sua pista atual e tenta inseri-lo em outra pista (trabalhando sobre cópias).
    Retorna (melhorou, nova_solucao) — a nova solução só é retornada se houver melhoria.
    """
    melhor_custo = calcular_custo_total(voos)
    melhorou = False
    melhor_voos = copy.deepcopy(voos)  # Inicializa com a solução atual

    for idx, voo in enumerate(voos):
        for pista in pistas:
            if pista.id != voo.pista_atribuida:
                # Cria cópia da solução para testar essa modificação
                voos_copia = copy.deepcopy(voos)
                pistas_copia = copy.deepcopy(pistas)

                voo_copia = voos_copia[idx]

                # Remove da pista original
                voo_copia.pista_atribuida = None
                voo_copia.horario_atribuido = None

                # Adiciona à nova pista
                nova_pista = next(p for p in pistas_copia if p.id == pista.id)
                voos_pista = [v for v in voos_copia if v.pista_atribuida == nova_pista.id]
                voos_pista.append(voo_copia)
                voos_pista.sort(key=lambda v: v.horario_atribuido if v.horario_atribuido is not None else float('inf'))

                # Tenta recalcular horários nessa nova pista
                if recalcular_horarios_pista(voos_pista, nova_pista, matriz_tempo):
                    novo_custo = calcular_custo_total(voos_copia)
                    if novo_custo < melhor_custo:
                        melhor_custo = novo_custo
                        melhor_voos = voos_copia
                        melhorou = True
                        print("RETIRAR E INSERIR --> CUSTO MELHORADO:", melhor_custo)
                        break  # sai do loop de pistas

        # Se já melhorou, não precisa mais testar esse voo
        if melhorou:
            break

    return melhorou, melhor_voos, melhor_custo


def movimento_ajuste_horario(voos, pistas, matriz_tempo):
    """
    Tenta ajustar os horários dos voos dentro de suas pistas atuais para reduzir atrasos.
    Retorna: (melhorou, nova_solucao_voos, novo_custo)
    """
    melhor_voos = copy.deepcopy(voos)
    melhor_pistas = copy.deepcopy(pistas)
    melhor_custo = calcular_custo_total(melhor_voos)
    melhorou = False

    # Ordena voos por penalidade atual (maiores primeiro), filtrando voos sem pista atribuída
    voos_ordenados = sorted(
        [v for v in voos if v.pista_atribuida is not None],
        key=lambda v: -v.p * max(0, v.horario_atribuido - v.r)
    )

    for voo in voos_ordenados:
        # Cria cópia para testar modificação
        voos_copia = copy.deepcopy(melhor_voos)
        pistas_copia = copy.deepcopy(melhor_pistas)
        
        # Encontra o voo correspondente na cópia
        voo_copia = next(v for v in voos_copia if v.id == voo.id)
        
        # Verifica se o voo ainda está alocado em uma pista válida
        if voo_copia.pista_atribuida is None:
            continue
            
        pista_copia = pistas_copia[voo_copia.pista_atribuida]
        
        # Pega todos os voos da pista (ordenados por horário)
        voos_pista = [v for v in voos_copia if v.pista_atribuida == pista_copia.id]
        voos_pista.sort(key=lambda v: v.horario_atribuido)
        
        try:
            idx = voos_pista.index(voo_copia)
        except ValueError:
            continue  # Voo não está na pista (não deveria acontecer)
        
        # Calcula o novo horário mínimo possível
        novo_horario = voo_copia.r
        
        # Respeita voo anterior (se existir)
        if idx > 0:
            voo_anterior = voos_pista[idx-1]
            novo_horario = max(novo_horario, 
                             voo_anterior.horario_atribuido + voo_anterior.c + 
                             matriz_tempo[voo_anterior.id][voo_copia.id])
        
        # Só faz ajuste se for antecipar o voo
        if novo_horario < voo_copia.horario_atribuido:
            # Atualiza horário
            voo_copia.horario_atribuido = novo_horario
            
            # Recalcula todos os voos subsequentes na pista
            for i in range(idx+1, len(voos_pista)):
                voo_atual = voos_pista[i]
                voo_anterior = voos_pista[i-1]
                
                novo_horario = max(voo_atual.r,
                                 voo_anterior.horario_atribuido + voo_anterior.c +
                                 matriz_tempo[voo_anterior.id][voo_atual.id])
                
                if novo_horario >= voo_atual.horario_atribuido:
                    break  # Não adianta continuar
                    
                voo_atual.horario_atribuido = novo_horario
            
            # Atualiza slots ocupados na pista
            pista_copia.ocupada_em = set()
            for v in voos_pista:
                if v.horario_atribuido is not None:  # Verificação adicional
                    for t in range(v.horario_atribuido, v.horario_atribuido + v.c):
                        pista_copia.ocupada_em.add(t)
            
            # Verifica se melhorou o custo total
            novo_custo = calcular_custo_total(voos_copia)
            if novo_custo < melhor_custo:
                melhor_custo = novo_custo
                melhor_voos = voos_copia
                melhor_pistas = pistas_copia
                melhorou = True
                print("AJUSTE DE HORÁRIO --> CUSTO MELHORADO:", melhor_custo)

    return melhorou, melhor_voos, melhor_custo


def VND(voos, pistas, matriz_tempo):
    """
    Algoritmo VND que aplica os movimentos de vizinhança em ordem
    até não encontrar mais melhorias
    """
    melhor_custo = calcular_custo_total(voos)
    print(f"Custo inicial: {melhor_custo}")
    
    # Ordem dos movimentos de vizinhança (do menos para o mais disruptivo)
    movimentos = [
        movimento_swap,
        movimento_ajuste_horario,
        movimento_retirar_inserir,
        ]
    
    k = 0
    while k < len(movimentos):
        movimento = movimentos[k]
        melhorou, nova_solucao, custo_pos_movimento = movimento(voos, pistas, matriz_tempo)
        voos = nova_solucao
        if melhorou:
            novo_custo = calcular_custo_total(nova_solucao)
            print(f"Movimento {k+1} melhorou para: {novo_custo}")
            melhor_custo = novo_custo
            k = 0  # Volta ao primeiro movimento
        else:
            k += 1  # Passa para o próximo movimento
            
    print(f"Melhor custo encontrado: {melhor_custo}")
    return melhor_custo