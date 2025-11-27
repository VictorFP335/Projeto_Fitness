# app.py
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "calorifit_secret"

DB_PATH = os.path.join(os.path.dirname(__file__), "calorifit.db")

def conectar():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS refeicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        calorias INTEGER NOT NULL,
        data_registro TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        calorias_gastas INTEGER NOT NULL,
        data_registro TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

criar_tabelas()

# ---------- Dashboard ----------
@app.route("/")
def index():
    conn = conectar()
    cur = conn.cursor()
    hoje = date.today().isoformat()

    cur.execute("SELECT COALESCE(SUM(calorias),0) FROM refeicoes WHERE data_registro = ?", (hoje,))
    ingeridas = cur.fetchone()[0] or 0

    cur.execute("SELECT COALESCE(SUM(calorias_gastas),0) FROM exercicios WHERE data_registro = ?", (hoje,))
    gastas = cur.fetchone()[0] or 0

    saldo = ingeridas - gastas
    conn.close()
    return render_template("index.html", ingeridas=ingeridas, gastas=gastas, saldo=saldo)

# API para Chart.js
@app.route("/grafico-data")
def grafico_data():
    conn = conectar()
    cur = conn.cursor()
    hoje = date.today().isoformat()

    cur.execute("SELECT COALESCE(SUM(calorias),0) FROM refeicoes WHERE data_registro = ?", (hoje,))
    ingeridas = cur.fetchone()[0] or 0

    cur.execute("SELECT COALESCE(SUM(calorias_gastas),0) FROM exercicios WHERE data_registro = ?", (hoje,))
    gastas = cur.fetchone()[0] or 0

    conn.close()
    return jsonify({"ingeridas": ingeridas, "gastas": gastas})

# ---------- Refeições ----------
@app.route("/calorias")
def calorias():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, calorias, data_registro FROM refeicoes ORDER BY id DESC")
    dados = cur.fetchall()
    conn.close()
    return render_template("calorias.html", refeicoes=dados)

@app.route("/add_calorias", methods=["POST"])
def add_calorias():
    nome = request.form.get("nome")
    calorias = int(request.form.get("calorias"))
    hoje = date.today().isoformat()

    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO refeicoes (nome, calorias, data_registro) VALUES (?, ?, ?)", (nome, calorias, hoje))
    conn.commit()
    conn.close()
    return redirect("/calorias")

# ---------- Exercícios ----------
@app.route("/exercicios")
def exercicios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, calorias_gastas, data_registro FROM exercicios ORDER BY id DESC")
    dados = cur.fetchall()
    conn.close()
    return render_template("exercicios.html", exercicios=dados)

@app.route("/add_exercicio", methods=["POST"])
def add_exercicio():
    nome = request.form.get("nome")
    gasto = int(request.form.get("calorias"))
    hoje = date.today().isoformat()

    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO exercicios (nome, calorias_gastas, data_registro) VALUES (?, ?, ?)", (nome, gasto, hoje))
    conn.commit()
    conn.close()
    return redirect("/exercicios")

# ---------- Run ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
