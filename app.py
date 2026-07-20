from flask import Flask, render_template, request, redirect
from database import conectar, criar_tabelas

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("/produtos")

@app.route("/produtos")
def listar_produtos():
    conexao = conectar()
    produtos = conexao.execute("SELECT * FROM produtos").fetchall()
    conexao.close()
    return render_template("produtos.html", produtos=produtos)

@app.route("/produtos/novo", methods=["POST"])
def criar_produto():
    nome = request.form["nome"]
    preco = request.form["preco"]
    quantidade = request.form["quantidade"]

    conexao = conectar()
    conexao.execute(
        "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
        (nome, preco, quantidade)
    )
    conexao.commit()
    conexao.close()
    return redirect("/produtos")

@app.route("/produtos/editar/<int:id>")
def editar_produto_form(id):
    conexao = conectar()
    produto = conexao.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    conexao.close()
    return render_template("editar_produto.html", produto=produto)

@app.route("/produtos/editar/<int:id>", methods=["POST"])
def editar_produto(id):
    nome = request.form["nome"]
    preco = request.form["preco"]
    quantidade = request.form["quantidade"]

    conexao = conectar()
    conexao.execute(
        "UPDATE produtos SET nome = ?, preco = ?, quantidade = ? WHERE id = ?",
        (nome, preco, quantidade, id)
    )
    conexao.commit()
    conexao.close()
    return redirect("/produtos")

@app.route("/produtos/excluir/<int:id>", methods=["POST"])
def excluir_produto(id):
    conexao = conectar()
    conexao.execute("DELETE FROM produtos WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return redirect("/produtos")

@app.route("/clientes")
def listar_clientes():
    conexao = conectar()
    clientes = conexao.execute("SELECT * FROM clientes").fetchall()
    conexao.close()
    return render_template("clientes.html", clientes=clientes)

@app.route("/clientes/novo", methods=["POST"])
def criar_cliente():
    nome = request.form["nome"]
    contato = request.form["contato"]

    conexao = conectar()
    conexao.execute(
        "INSERT INTO clientes (nome, contato) VALUES (?, ?)",
        (nome, contato)
    )
    conexao.commit()
    conexao.close()
    return redirect("/clientes")

@app.route("/clientes/editar/<int:id>")
def editar_cliente_form(id):
    conexao = conectar()
    cliente = conexao.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()
    conexao.close()
    return render_template("editar_cliente.html", cliente=cliente)

@app.route("/clientes/editar/<int:id>", methods=["POST"])
def editar_cliente(id):
    nome = request.form["nome"]
    contato = request.form["contato"]

    conexao = conectar()
    conexao.execute(
        "UPDATE clientes SET nome = ?, contato = ? WHERE id = ?",
        (nome, contato, id)
    )
    conexao.commit()
    conexao.close()
    return redirect("/clientes")

@app.route("/clientes/excluir/<int:id>", methods=["POST"])
def excluir_cliente(id):
    conexao = conectar()
    conexao.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return redirect("/clientes")

@app.route("/vendas")
def listar_vendas():
    conexao = conectar()
    vendas = conexao.execute("""
        SELECT vendas.id, produtos.nome AS produto, clientes.nome AS cliente,
               vendas.quantidade, vendas.data
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
        JOIN clientes ON vendas.cliente_id = clientes.id
        ORDER BY vendas.data DESC
    """).fetchall()
    produtos = conexao.execute("SELECT * FROM produtos").fetchall()
    clientes = conexao.execute("SELECT * FROM clientes").fetchall()
    conexao.close()
    return render_template("vendas.html", vendas=vendas, produtos=produtos, clientes=clientes)

@app.route("/vendas/nova", methods=["POST"])
def criar_venda():
    produto_id = request.form["produto_id"]
    cliente_id = request.form["cliente_id"]
    quantidade = int(request.form["quantidade"])

    conexao = conectar()

    produto = conexao.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()

    if produto["quantidade"] < quantidade:
        conexao.close()
        return "Estoque insuficiente para essa venda.", 400

    from datetime import date
    hoje = date.today().isoformat()

    conexao.execute(
        "INSERT INTO vendas (produto_id, cliente_id, quantidade, data) VALUES (?, ?, ?, ?)",
        (produto_id, cliente_id, quantidade, hoje)
    )

    conexao.execute(
        "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
        (quantidade, produto_id)
    )

    conexao.commit()
    conexao.close()
    return redirect("/vendas")

@app.route("/vendas/editar/<int:id>")
def editar_venda_form(id):
    conexao = conectar()
    venda = conexao.execute("SELECT * FROM vendas WHERE id = ?", (id,)).fetchone()
    produtos = conexao.execute("SELECT * FROM produtos").fetchall()
    clientes = conexao.execute("SELECT * FROM clientes").fetchall()
    conexao.close()
    return render_template("editar_venda.html", venda=venda, produtos=produtos, clientes=clientes)

@app.route("/vendas/editar/<int:id>", methods=["POST"])
def editar_venda(id):
    produto_id = request.form["produto_id"]
    cliente_id = request.form["cliente_id"]
    quantidade = int(request.form["quantidade"])

    conexao = conectar()
    conexao.execute(
        "UPDATE vendas SET produto_id = ?, cliente_id = ?, quantidade = ? WHERE id = ?",
        (produto_id, cliente_id, quantidade, id)
    )
    conexao.commit()
    conexao.close()
    return redirect("/vendas")

@app.route("/vendas/excluir/<int:id>", methods=["POST"])
def excluir_venda(id):
    conexao = conectar()
    conexao.execute("DELETE FROM vendas WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return redirect("/vendas")

@app.route("/relatorio")
def relatorio():
    conexao = conectar()

    total_vendido = conexao.execute("""
        SELECT SUM(vendas.quantidade * produtos.preco) AS total
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
    """).fetchone()["total"] or 0

    mais_vendidos = conexao.execute("""
        SELECT produtos.nome, SUM(vendas.quantidade) AS total_vendido
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
        GROUP BY produtos.nome
        ORDER BY total_vendido DESC
        LIMIT 5
    """).fetchall()

    conexao.close()
    return render_template("relatorio.html", total_vendido=total_vendido, mais_vendidos=mais_vendidos)

if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)
