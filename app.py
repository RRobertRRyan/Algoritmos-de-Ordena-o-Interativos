"""
app.py — Servidor Flask principal
Expõe a API REST para o frontend e serve os arquivos estáticos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, send_from_directory
from features.algorithms import ALGORITHMS, run_algorithm_sync
from features.api import get_data, list_fields

# ── Configuração ──────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(__file__)
STATIC_DIR   = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "structure")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    template_folder=TEMPLATE_DIR,
)


# ── Rotas de arquivos estáticos ───────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(TEMPLATE_DIR, "index.html")

@app.route("/styles/<path:filename>")
def styles(filename):
    return send_from_directory(os.path.join(BASE_DIR, "styles"), filename)

@app.route("/features/<path:filename>")
def features_js(filename):
    return send_from_directory(os.path.join(BASE_DIR, "features"), filename)


# ── API REST ──────────────────────────────────────────────────────────────────

@app.route("/api/fields")
def api_fields():
    """Retorna a lista de campos disponíveis para ordenação."""
    return jsonify(list_fields())


@app.route("/api/data")
def api_data():
    """
    Busca dados do Banco Mundial.
    Query params:
      field       — chave do campo (gdp, lifeExp, population, gdpPerCapita)
      sample_size — número de países (padrão: 16)
    """
    field       = request.args.get("field", "gdp")
    sample_size = int(request.args.get("sample_size", 16))
    sample_size = max(5, min(sample_size, 100))   # limita entre 5 e 100
    try:
        data = get_data(field, sample_size)
        return jsonify({"ok": True, "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/steps")
def api_steps():
    """
    Executa um algoritmo e retorna TODOS os passos de uma vez.
    Query params:
      algorithm   — chave do algoritmo (bubble, selection, insertion, merge, quick, heap)
      field       — campo de dados
      sample_size — tamanho da amostra
    """
    algo_key    = request.args.get("algorithm", "selection")
    field       = request.args.get("field", "gdp")
    sample_size = int(request.args.get("sample_size", 16))

    if algo_key not in ALGORITHMS:
        return jsonify({"ok": False, "error": f"Algoritmo desconhecido: {algo_key}"}), 400

    try:
        data  = get_data(field, sample_size)
        algo  = ALGORITHMS[algo_key]
        steps = list(algo["fn"]([x.copy() for x in data]))

        # Remove o array completo de cada passo para economizar tamanho —
        # o frontend já mantém o estado localmente
        compact = []
        for s in steps:
            step = {k: v for k, v in s.items() if k != "arr"}
            # Inclui apenas o array nos passos de swap/set (para sincronizar)
            if s["type"] in ("swap", "set", "done", "sorted") and "arr" in s:
                step["arr"] = s["arr"]
            compact.append(step)

        return jsonify({
            "ok":         True,
            "algorithm":  algo["name"],
            "data":       data,
            "steps":      compact,
            "total":      len(compact),
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/compare")
def api_compare():
    """
    Roda todos os 6 algoritmos sobre o mesmo dataset e retorna métricas.
    Query params:
      field       — campo de dados
      sample_size — tamanho da amostra
    """
    field       = request.args.get("field", "gdp")
    sample_size = int(request.args.get("sample_size", 16))

    try:
        data    = get_data(field, sample_size)
        results = []
        for key in ALGORITHMS:
            metrics = run_algorithm_sync(key, data)
            results.append({"key": key, **metrics})
        return jsonify({"ok": True, "results": results, "count": len(data)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/algorithms")
def api_algorithms():
    """Retorna metadados dos algoritmos (pseudocódigo, complexidade, descrição)."""
    result = {}
    for key, algo in ALGORITHMS.items():
        result[key] = {
            "name":        algo["name"],
            "ds":          algo["ds"],
            "description": algo["description"],
            "pseudo":      algo["pseudo"],
            "complexity":  algo["complexity"],
        }
    return jsonify(result)


# ── Inicialização ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  🔢  Ordenação Interativos — The Sort Engine")
    print("  🌍  Dados: Banco Mundial / ONU")
    print("=" * 55)
    print("  Acesse: http://localhost:5000")
    print("  Para parar: Ctrl + C")
    print("=" * 55)
    app.run(debug=True, port=5000)
