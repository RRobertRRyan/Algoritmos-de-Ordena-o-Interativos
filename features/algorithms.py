"""
algorithms.py — Implementação dos 6 algoritmos de ordenação em Python
Cada função é um gerador que produz passos para animação
"""

from typing import Generator, List, Dict, Any

Step = Dict[str, Any]


# ── BUBBLE SORT ──────────────────────────────────────────────────────────────
def bubble_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    n = len(a)
    for i in range(n - 1):
        for j in range(n - i - 1):
            yield {"type": "compare", "i": j, "j": j + 1, "arr": [x.copy() for x in a],
                   "msg": f"Comparando [{j}] {a[j]['name']} ({a[j]['label']}) com [{j+1}] {a[j+1]['name']} ({a[j+1]['label']})", "line": 3}
            if a[j]["val"] > a[j + 1]["val"]:
                a[j], a[j + 1] = a[j + 1], a[j]
                yield {"type": "swap", "i": j, "j": j + 1, "arr": [x.copy() for x in a],
                       "msg": f"Trocando {a[j+1]['name']} ↔ {a[j]['name']}", "line": 4}
        yield {"type": "sorted", "indices": [n - i - 1], "arr": [x.copy() for x in a],
               "msg": f"Elemento {a[n-i-1]['name']} está na posição final", "line": 5}
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Ordenação completa! ✓", "line": 6}


# ── SELECTION SORT ───────────────────────────────────────────────────────────
def selection_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        yield {"type": "compare", "i": min_idx, "j": i, "arr": [x.copy() for x in a],
               "msg": f"Buscando mínimo a partir do índice {i}", "line": 3}
        for j in range(i + 1, n):
            yield {"type": "compare", "i": min_idx, "j": j, "arr": [x.copy() for x in a],
                   "msg": f"Comparando mínimo atual [{a[min_idx]['name']}] com [{a[j]['name']}]", "line": 4}
            if a[j]["val"] < a[min_idx]["val"]:
                min_idx = j
                yield {"type": "compare", "i": min_idx, "j": j, "arr": [x.copy() for x in a],
                       "msg": f"Novo mínimo: {a[min_idx]['name']} no índice {j}", "line": 5}
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            yield {"type": "swap", "i": i, "j": min_idx, "arr": [x.copy() for x in a],
                   "msg": f"Colocando mínimo {a[i]['name']} na posição {i}", "line": 6}
        yield {"type": "sorted", "indices": [i], "arr": [x.copy() for x in a],
               "msg": f"Índice {i} finalizado: {a[i]['name']}", "line": 7}
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Ordenação completa! ✓", "line": 8}


# ── INSERTION SORT ───────────────────────────────────────────────────────────
def insertion_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    n = len(a)
    yield {"type": "sorted", "indices": [0], "arr": [x.copy() for x in a],
           "msg": "Primeiro elemento considerado ordenado", "line": 2}
    for i in range(1, n):
        key = a[i].copy()
        j = i - 1
        yield {"type": "compare", "i": i, "j": j, "arr": [x.copy() for x in a],
               "msg": f"Inserindo {key['name']} — comparando com {a[j]['name']}", "line": 3}
        while j >= 0 and a[j]["val"] > key["val"]:
            a[j + 1] = a[j].copy()
            yield {"type": "swap", "i": j, "j": j + 1, "arr": [x.copy() for x in a],
                   "msg": f"Movendo {a[j]['name']} para a direita ({j}→{j+1})", "line": 4}
            j -= 1
            if j >= 0:
                yield {"type": "compare", "i": i, "j": j, "arr": [x.copy() for x in a],
                       "msg": f"Comparando chave {key['name']} com {a[j]['name']}", "line": 5}
        a[j + 1] = key
        yield {"type": "set", "i": j + 1, "arr": [x.copy() for x in a],
               "msg": f"Inserindo {key['name']} na posição {j+1}", "line": 6}
        yield {"type": "sorted", "indices": list(range(i + 1)), "arr": [x.copy() for x in a],
               "msg": f"Posições 0..{i} agora ordenadas", "line": 7}
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Ordenação completa! ✓", "line": 8}


# ── MERGE SORT ───────────────────────────────────────────────────────────────
def merge_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    yield from _merge_sort_helper(a, 0, len(a) - 1)
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Merge Sort completo! ✓", "line": 9}


def _merge_sort_helper(a, l, r):
    if l >= r:
        return
    mid = (l + r) // 2
    yield {"type": "compare", "i": l, "j": r, "arr": [x.copy() for x in a],
           "msg": f"Dividindo [{l}..{r}] em [{l}..{mid}] e [{mid+1}..{r}]", "line": 2}
    yield from _merge_sort_helper(a, l, mid)
    yield from _merge_sort_helper(a, mid + 1, r)
    yield from _merge(a, l, mid, r)


def _merge(a, l, mid, r):
    left  = [x.copy() for x in a[l:mid + 1]]
    right = [x.copy() for x in a[mid + 1:r + 1]]
    i = j = 0
    k = l
    while i < len(left) and j < len(right):
        yield {"type": "compare", "i": l + i, "j": mid + 1 + j, "arr": [x.copy() for x in a],
               "msg": f"Merge: comparando {left[i]['name']} com {right[j]['name']}", "line": 5}
        if left[i]["val"] <= right[j]["val"]:
            a[k] = left[i].copy(); i += 1
        else:
            a[k] = right[j].copy(); j += 1
        yield {"type": "set", "i": k, "arr": [x.copy() for x in a],
               "msg": f"Inserindo {a[k]['name']} na posição {k}", "line": 6}
        k += 1
    while i < len(left):
        a[k] = left[i].copy()
        yield {"type": "set", "i": k, "arr": [x.copy() for x in a],
               "msg": f"Copiando restante esquerda: {a[k]['name']}", "line": 7}
        i += 1; k += 1
    while j < len(right):
        a[k] = right[j].copy()
        yield {"type": "set", "i": k, "arr": [x.copy() for x in a],
               "msg": f"Copiando restante direita: {a[k]['name']}", "line": 8}
        j += 1; k += 1
    yield {"type": "sorted", "indices": list(range(l, r + 1)), "arr": [x.copy() for x in a],
           "msg": f"Subarray [{l}..{r}] mesclado e ordenado", "line": 9}


# ── QUICK SORT ───────────────────────────────────────────────────────────────
def quick_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    yield from _quick_sort_helper(a, 0, len(a) - 1)
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Quick Sort completo! ✓", "line": 10}


def _quick_sort_helper(a, low, high):
    if low < high:
        pivot_idx, steps = yield from _partition(a, low, high)
        yield {"type": "sorted", "indices": [pivot_idx], "arr": [x.copy() for x in a],
               "msg": f"Pivô {a[pivot_idx]['name']} está na posição final {pivot_idx}", "line": 8}
        yield from _quick_sort_helper(a, low, pivot_idx - 1)
        yield from _quick_sort_helper(a, pivot_idx + 1, high)
    elif low == high:
        yield {"type": "sorted", "indices": [low], "arr": [x.copy() for x in a],
               "msg": f"Elemento {a[low]['name']} em posição final", "line": 8}


def _partition(a, low, high):
    pivot = a[high]
    yield {"type": "pivot", "i": high, "arr": [x.copy() for x in a],
           "msg": f"Pivô escolhido: {pivot['name']} (índice {high})", "line": 3}
    i = low - 1
    for j in range(low, high):
        yield {"type": "compare", "i": j, "j": high, "arr": [x.copy() for x in a],
               "msg": f"Comparando {a[j]['name']} com pivô {pivot['name']}", "line": 5}
        if a[j]["val"] <= pivot["val"]:
            i += 1
            if i != j:
                a[i], a[j] = a[j], a[i]
                yield {"type": "swap", "i": i, "j": j, "arr": [x.copy() for x in a],
                       "msg": f"Trocando {a[i]['name']} com {a[j]['name']}", "line": 6}
    a[i + 1], a[high] = a[high], a[i + 1]
    yield {"type": "swap", "i": i + 1, "j": high, "arr": [x.copy() for x in a],
           "msg": f"Colocando pivô {a[i+1]['name']} na posição {i+1}", "line": 7}
    return i + 1, None


# ── HEAP SORT ────────────────────────────────────────────────────────────────
def heap_sort(arr: List[Dict]) -> Generator[Step, None, None]:
    a = [x.copy() for x in arr]
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        yield {"type": "heap", "arr": [x.copy() for x in a],
               "msg": f"Construindo max-heap: heapify no índice {i}", "line": 2}
        yield from _heapify(a, n, i)
    yield {"type": "heap", "arr": [x.copy() for x in a], "msg": "Max-heap construído!", "line": 3}
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        yield {"type": "swap", "i": 0, "j": i, "arr": [x.copy() for x in a],
               "msg": f"Raiz {a[i]['name']} movida para posição {i}", "line": 5}
        yield {"type": "sorted", "indices": list(range(i, n)), "arr": [x.copy() for x in a],
               "msg": f"Posição {i} finalizada", "line": 6}
        yield from _heapify(a, i, 0)
    yield {"type": "done", "arr": [x.copy() for x in a], "msg": "Heap Sort completo! ✓", "line": 8}


def _heapify(a, n, i):
    largest = i
    l, r = 2 * i + 1, 2 * i + 2
    if l < n:
        yield {"type": "compare", "i": l, "j": largest, "arr": [x.copy() for x in a],
               "msg": f"Heapify: filho esq [{a[l]['name']}] vs [{a[largest]['name']}]", "line": 2}
        if a[l]["val"] > a[largest]["val"]:
            largest = l
    if r < n:
        yield {"type": "compare", "i": r, "j": largest, "arr": [x.copy() for x in a],
               "msg": f"Heapify: filho dir [{a[r]['name']}] vs [{a[largest]['name']}]", "line": 3}
        if a[r]["val"] > a[largest]["val"]:
            largest = r
    if largest != i:
        a[i], a[largest] = a[largest], a[i]
        yield {"type": "heap", "i": i, "j": largest, "arr": [x.copy() for x in a],
               "msg": f"Heapify: subindo {a[i]['name']} (índice {largest}→{i})", "line": 4}
        yield from _heapify(a, n, largest)


# ── METADATA ─────────────────────────────────────────────────────────────────
ALGORITHMS = {
    "bubble": {
        "name": "Bubble Sort", "fn": bubble_sort,
        "ds": "Array (in-place)",
        "description": "O Bubble Sort percorre o array repetidamente, comparando pares adjacentes e trocando-os quando na ordem errada. A cada passagem, o maior elemento 'borbulha' até sua posição final.\n\nEmbora simples, realiza muitas comparações — mesmo quando o array está quase ordenado. É O(n²) na maioria dos casos.\n\nUsa um simples array, sem memória auxiliar.",
        "pseudo": ["procedure bubbleSort(A):", "  for i = 0 to n-2:", "    for j = 0 to n-i-2:", "      if A[j] > A[j+1]:", "        swap(A[j], A[j+1])", "  mark A as sorted", "  return A"],
        "complexity": {"best": {"val": "O(n)", "why": "Array já ordenado"}, "avg": {"val": "O(n²)", "why": "n(n-1)/2 comparações"}, "worst": {"val": "O(n²)", "why": "Array invertido"}, "space": {"val": "O(1)", "why": "Apenas variáveis temporárias"}}
    },
    "selection": {
        "name": "Selection Sort", "fn": selection_sort,
        "ds": "Array (in-place)",
        "description": "O Selection Sort divide o array em parte ordenada (esquerda) e não-ordenada (direita). A cada iteração, encontra o menor elemento da parte não-ordenada e o coloca na próxima posição.\n\nFaz poucas trocas (máximo n-1), mas sempre n² comparações independente da entrada.\n\nUsa um único array sem estrutura auxiliar.",
        "pseudo": ["procedure selectionSort(A):", "  for i = 0 to n-1:", "    min = i", "    for j = i+1 to n-1:", "      if A[j] < A[min]: min = j", "    swap(A[i], A[min])", "    mark A[i] as sorted", "  return A"],
        "complexity": {"best": {"val": "O(n²)", "why": "Sempre percorre o subarray todo"}, "avg": {"val": "O(n²)", "why": "n(n-1)/2 comparações sempre"}, "worst": {"val": "O(n²)", "why": "Sem melhoria possível"}, "space": {"val": "O(1)", "why": "In-place, sem array auxiliar"}}
    },
    "insertion": {
        "name": "Insertion Sort", "fn": insertion_sort,
        "ds": "Array (in-place)",
        "description": "O Insertion Sort constrói a parte ordenada um elemento por vez — como ordenar cartas na mão. Pega cada elemento e o insere na posição correta, deslocando os maiores para a direita.\n\nMuito eficiente para arrays pequenos ou quase ordenados (O(n) no melhor caso). Base do Timsort do Python.\n\nOpera diretamente no array, sem estrutura auxiliar.",
        "pseudo": ["procedure insertionSort(A):", "  mark A[0] as sorted", "  for i = 1 to n-1:", "    key = A[i]; j = i-1", "    while j >= 0 and A[j] > key:", "      A[j+1] = A[j]; j--", "    A[j+1] = key", "  return A"],
        "complexity": {"best": {"val": "O(n)", "why": "Array já ordenado — 0 deslocamentos"}, "avg": {"val": "O(n²)", "why": "Média de n²/4 comparações"}, "worst": {"val": "O(n²)", "why": "Array invertido — máximo de deslocamentos"}, "space": {"val": "O(1)", "why": "In-place, apenas variável key"}}
    },
    "merge": {
        "name": "Merge Sort", "fn": merge_sort,
        "ds": "Arrays auxiliares (divisão e conquista)",
        "description": "O Merge Sort usa divisão e conquista: divide o array ao meio recursivamente até subarrays de 1 elemento, depois os mescla ordenadamente comparando elemento a elemento.\n\nGarantidamente O(n log n) — divide log n vezes e mescla n elementos em cada nível. Estável e previsível.\n\nRequer O(n) de memória auxiliar para os subarrays temporários durante a mesclagem.",
        "pseudo": ["procedure mergeSort(A, l, r):", "  if l >= r: return", "  mid = (l + r) / 2", "  mergeSort(A, l, mid)", "  mergeSort(A, mid+1, r)", "  merge(A, l, mid, r):", "    comparar e mesclar subarrays", "    copiar de volta ao array", "  return A"],
        "complexity": {"best": {"val": "O(n log n)", "why": "log n divisões × n mesclagens"}, "avg": {"val": "O(n log n)", "why": "Sempre divide simetricamente"}, "worst": {"val": "O(n log n)", "why": "Garantido — sem pior caso"}, "space": {"val": "O(n)", "why": "Arrays auxiliares para merge"}}
    },
    "quick": {
        "name": "Quick Sort", "fn": quick_sort,
        "ds": "Array (in-place) + pilha de recursão",
        "description": "O Quick Sort escolhe um 'pivô' e reorganiza o array: menores à esquerda, maiores à direita. Aplica-se recursivamente em cada grupo.\n\nNa prática muito rápido — O(n log n) médio com boa localidade de cache. A escolha do pivô é crítica: pivô ruim degrada para O(n²).\n\nFunciona in-place mas usa a pilha de chamadas — O(log n) em média.",
        "pseudo": ["procedure quickSort(A, low, high):", "  if low < high:", "    pivot = A[high]", "    i = low - 1", "    for j = low to high-1:", "      if A[j] <= pivot: i++; swap(A[i], A[j])", "    swap(A[i+1], A[high])", "    pivotIdx = i + 1", "    quickSort(A, low, pivotIdx-1)", "    quickSort(A, pivotIdx+1, high)"],
        "complexity": {"best": {"val": "O(n log n)", "why": "Pivô sempre no meio"}, "avg": {"val": "O(n log n)", "why": "Pivô aleatório → partições equilibradas"}, "worst": {"val": "O(n²)", "why": "Pivô sempre mínimo/máximo"}, "space": {"val": "O(log n)", "why": "Pilha de recursão"}}
    },
    "heap": {
        "name": "Heap Sort", "fn": heap_sort,
        "ds": "Heap binário (árvore) sobre array",
        "description": "O Heap Sort transforma o array em um max-heap — árvore binária onde o pai é sempre maior que os filhos. A raiz (índice 0) é sempre o maior elemento.\n\nExtrai repetidamente a raiz, coloca-a no final e restaura o heap (heapify). Garante O(n log n) em todos os casos.\n\nA estrutura de heap é implícita no array: filho esquerdo de i em 2i+1, direito em 2i+2.",
        "pseudo": ["procedure heapSort(A):", "  buildMaxHeap(A)", "  mark heap construído", "  for i = n-1 to 1:", "    swap(A[0], A[i])", "    mark A[i] como sorted", "    heapify(A, i, 0)", "  return A"],
        "complexity": {"best": {"val": "O(n log n)", "why": "heapify custa O(log n)"}, "avg": {"val": "O(n log n)", "why": "n extrações × O(log n)"}, "worst": {"val": "O(n log n)", "why": "Garantido — sem caso degenerado"}, "space": {"val": "O(1)", "why": "In-place — heap sobre o próprio array"}}
    },
}


def run_algorithm_sync(algo_key: str, data: List[Dict]) -> Dict:
    """Executa um algoritmo sincronamente e retorna métricas para comparação."""
    import time
    algo = ALGORITHMS[algo_key]
    arr  = [x.copy() for x in data]
    comparisons = swaps = 0
    start = time.perf_counter()
    for step in algo["fn"](arr):
        if step["type"] == "compare":
            comparisons += 1
        elif step["type"] in ("swap", "set"):
            swaps += 1
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "name":        algo["name"],
        "comparisons": comparisons,
        "swaps":       swaps,
        "time_ms":     round(elapsed_ms, 3),
        "complexity":  algo["complexity"],
    }
