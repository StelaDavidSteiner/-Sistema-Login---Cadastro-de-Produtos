from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "sistema_login"


# Função para criar o banco
def criar_banco():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            usuario_id INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


# Rotas
@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for("login"))
        except:
            flash("Usuário já existe!", "danger")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["usuario_id"] = user[0]
            session["username"] = username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha incorretos!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, descricao FROM produtos WHERE usuario_id = ?", (session["usuario_id"],))
    produtos = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", produtos=produtos)


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, descricao, usuario_id) VALUES (?, ?, ?)",
                       (nome, descricao, session["usuario_id"]))
        conn.commit()
        conn.close()
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_product.html")


# Inicialização
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
