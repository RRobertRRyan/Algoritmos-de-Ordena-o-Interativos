# 🔢 Ordenação Interativos — The Sort Engine

Visualizador interativo de algoritmos de ordenação com backend **100% Python** e dados reais do **Banco Mundial (ONU)**.

## Estrutura do Projeto

```
sort-engine-py/
│
├── app.py                    ← Servidor Flask (entry point)
├── requirements.txt          ← Dependências Python
│
├── features/                 ← Camada de funcionalidades (Python + JS)
│   ├── algorithms.py         ← 6 algoritmos em Python (geradores yield)
│   ├── api.py                ← Integração Banco Mundial
│   └── main.js               ← Frontend: consome a API Flask
│
├── structure/                ← Camada de estrutura (HTML)
│   └── index.html            ← Template principal
│
└── styles/                   ← Camada de estilização (CSS)
    ├── theme.css             ← Tokens de design: cores, tipografia
    └── layout.css            ← Componentes, animações, responsividade
```

## Como Rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor

```bash
python app.py
```

### 3. Acessar no navegador

```
http://localhost:5000
```

## API REST (Python/Flask)

| Endpoint           | Descrição                                      |
|--------------------|------------------------------------------------|
| `GET /`            | Interface web principal                        |
| `GET /api/data`    | Dados do Banco Mundial                         |
| `GET /api/steps`   | Passos do algoritmo (calculados em Python)     |
| `GET /api/compare` | Comparação de todos os 6 algoritmos            |
| `GET /api/algorithms` | Metadados: pseudocódigo, complexidade       |

### Parâmetros

- `field` — `gdp` | `lifeExp` | `population` | `gdpPerCapita`
- `algorithm` — `bubble` | `selection` | `insertion` | `merge` | `quick` | `heap`
- `sample_size` — número de países (5–100)

## Algoritmos Implementados (Python)

| Algoritmo      | Melhor     | Médio      | Pior       | Espaço   |
|----------------|------------|------------|------------|----------|
| Bubble Sort    | O(n)       | O(n²)      | O(n²)      | O(1)     |
| Selection Sort | O(n²)      | O(n²)      | O(n²)      | O(1)     |
| Insertion Sort | O(n)       | O(n²)      | O(n²)      | O(1)     |
| Merge Sort     | O(n log n) | O(n log n) | O(n log n) | O(n)     |
| Quick Sort     | O(n log n) | O(n log n) | O(n²)      | O(log n) |
| Heap Sort      | O(n log n) | O(n log n) | O(n log n) | O(1)     |

## Tecnologias

- **Backend**: Python 3.10+ com Flask
- **Algoritmos**: Implementados como geradores Python (`yield`)
- **Dados**: API do Banco Mundial (ONU) via `urllib`
- **Frontend**: HTML + CSS + JavaScript vanilla (consome a API Flask)
- **Fontes**: Playfair Display, JetBrains Mono, DM Sans (Google Fonts)
