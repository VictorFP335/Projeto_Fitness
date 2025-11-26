import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
DB_PATH = "calorifit.db"

# Inicialização do banco SQLite
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refeicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        calorias REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        calorias REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Harris-Benedict
def harris_benedict(peso, altura, idade, sexo):
    if sexo == "masculino":
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * idade)
    else:
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * idade)
    return round(tmb, 2)

def calcular_tdee(tmb, fator_atividade):
    return round(tmb * fator_atividade, 2)

# Gerar gráfico interativo simples
def gerar_grafico_interativo(tdee=0):
    conn = sqlite3.connect(DB_PATH)
    df_refeicoes = pd.read_sql("SELECT * FROM refeicoes", conn)
    df_exercicios = pd.read_sql("SELECT * FROM exercicios", conn)
    conn.close()

    total_refeicoes = df_refeicoes["calorias"].sum() if not df_refeicoes.empty else 0
    total_exercicios = df_exercicios["calorias"].sum() if not df_exercicios.empty else 0

    # Cores indicam se calorias ingeridas excedem a meta
    cor_refeicoes = "#e76f51" if total_refeicoes > tdee else "#2a9d8f"
    cor_exercicios = "#f4a261"
    cor_meta = "#264653"

    labels = ["Calorias Ingeridas", "Calorias Gastas", "Meta TDEE"]
    values = [total_refeicoes, total_exercicios, tdee]
    colors = [cor_refeicoes, cor_exercicios, cor_meta]

    plt.figure(figsize=(6,4))
    bars = plt.bar(labels, values, color=colors)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, f'{yval:.0f}', ha='center', va='bottom')

    plt.ylabel("Calorias")
    plt.title("Resumo Diário")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return f"data:image/png;base64,{img_base64}"

# Home
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

# Metas
@app.route("/metas", methods=["GET", "POST"])
def metas():
    resultado = None
    tdee = 0
    if request.method == "POST":
        try:
            peso = float(request.form.get("peso", 0))
            altura = float(request.form.get("altura", 0))
            idade = int(request.form.get("idade", 0))
            sexo = request.form.get("sexo", "masculino")
            fator_atividade = float(request.form.get("atividade", 1.2))

            tmb = harris_benedict(peso, altura, idade, sexo)
            tdee = calcular_tdee(tmb, fator_atividade)
            resultado = {"tmb": tmb, "tdee": tdee}
        except ValueError:
            resultado = {"tmb": 0, "tdee": 0}

    graph = gerar_grafico_interativo(tdee)
    return render_template("metas.html", resultado=resultado, graph=graph)

# Refeicoes
@app.route("/refeicoes", methods=["GET", "POST"])
def refeicoes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if request.method == "POST":
        descricao = request.form.get("descricao")
        calorias = float(request.form.get("calorias", 0))
        cursor.execute("INSERT INTO refeicoes (descricao, calorias) VALUES (?, ?)", (descricao, calorias))
        conn.commit()
    df = pd.read_sql("SELECT * FROM refeicoes", conn)
    conn.close()
    return render_template("refeicoes.html", refeicoes=df.to_dict(orient="records"))

# Exercicios
@app.route("/exercicios", methods=["GET", "POST"])
def exercicios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if request.method == "POST":
        descricao = request.form.get("descricao")
        calorias = float(request.form.get("calorias", 0))
        cursor.execute("INSERT INTO exercicios (descricao, calorias) VALUES (?, ?)", (descricao, calorias))
        conn.commit()
    df = pd.read_sql("SELECT * FROM exercicios", conn)
    conn.close()
    return render_template("exercicios.html", exercicios=df.to_dict(orient="records"))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

