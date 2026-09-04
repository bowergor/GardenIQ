#!/usr/bin/env python3
"""
Dashboard web do jardim automatizado.
Roda no Raspberry Pi (porta 5000). Acesse do notebook via:
    http://<IP_DO_RASPBERRY>:5000
(ambos precisam estar na mesma rede Wi-Fi)

Permite mudar cultura, limites de umidade e temperatura em tempo real:
o irrigacao.py le esses valores de config.json a cada ciclo.
"""

import json
import csv
import os
from flask import Flask, render_template, request, jsonify

from presets import PRESETS_CULTURA

app = Flask(__name__)

CONFIG_PATH = "config.json"
LOG_PATH = "historico_irrigacao.csv"


def carregar_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def salvar_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


@app.route("/")
def index():
    cfg = carregar_config()
    return render_template("index.html", config=cfg, culturas=list(PRESETS_CULTURA.keys()))


@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(carregar_config())


@app.route("/api/config", methods=["POST"])
def api_set_config():
    dados = request.get_json()
    cfg = carregar_config()

    # Se a cultura mudou e existe preset, aplica os valores do preset
    nova_cultura = dados.get("cultura")
    if nova_cultura and nova_cultura in PRESETS_CULTURA and nova_cultura != cfg.get("cultura"):
        preset = PRESETS_CULTURA[nova_cultura]
        cfg.update(preset)

    # Sobrescreve com o que veio explicitamente do formulario
    campos_validos = [
        "cultura", "umidade_minima", "umidade_maxima", "temp_maxima_cooler",
        "tempo_bomba_segundos", "intervalo_leitura_segundos", "intervalo_minimo_rega_segundos"
    ]
    for campo in campos_validos:
        if campo in dados:
            cfg[campo] = dados[campo]

    salvar_config(cfg)
    return jsonify({"status": "ok", "config": cfg})


@app.route("/api/presets/<cultura>")
def api_get_preset(cultura):
    preset = PRESETS_CULTURA.get(cultura, {})
    return jsonify(preset)


@app.route("/api/historico")
def api_historico():
    """Retorna as ultimas N leituras do CSV para plotar no dashboard."""
    limite = int(request.args.get("limite", 100))
    if not os.path.exists(LOG_PATH):
        return jsonify([])

    with open(LOG_PATH, "r") as f:
        leitor = csv.DictReader(f)
        linhas = list(leitor)

    return jsonify(linhas[-limite:])


if __name__ == "__main__":
    # host="0.0.0.0" permite acesso de outros dispositivos na rede (o notebook)
    app.run(host="0.0.0.0", port=5000, debug=False)
