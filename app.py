from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/apiflask'

db = SQLAlchemy(app) #!Importar db para criar tabelas "from app import db" depois db.create_all()

class Livros(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    titulo = db.Column(db.String(50))
    preco = db.Column(db.Float)
    
    def to_Json(self):
        return{"id": self.id, "titulo": self.titulo, "preco": self.preco}
    def to_Json2(self):
        return{"titulo": self.titulo, "preco": self.preco}
#!Resetar id    
def reset_Id():
    db.session.execute("ALTER TABLE `apiflask`.`livros` DROP `id`")
    db.session.commit()
    db.session.execute("ALTER TABLE `apiflask`.`livros` ADD `id` INT(255) NOT NULL AUTO_INCREMENT FIRST, ADD PRIMARY KEY (`id`)")
    db.session.commit()
  
#!Obter todos os registros de livros 
@app.route("/Livros", methods=["GET"])
def select_Books():
    book_obj = Livros.query.all()
    book_json = [book.to_Json() for book in book_obj]
    print(type(book_json))
 
    return rtn_Response("200", "livros", book_json)

#!Obter o registro de um unico livro 
@app.route("/Livros/<id>", methods=["GET"])
def select_BookId(id):
    book_obj = Livros.query.filter_by(id=id).first()
    book_json = book_obj.to_Json()
    
    return rtn_Response(200, "livro", book_json)

#!Buscar Livros pelo preço fixo
@app.route("/Livros/Valor/<preco>", methods=["GET"])
def select_Book_Price(preco):
    book_obj = Livros.query.filter_by(preco=preco).all()
    if(len(book_obj) != 0):
        book_json = [book.to_Json() for book in book_obj]
        return rtn_Response(200, "livros", book_json)
    else:
        return rtn_Response(400, "livros", {}, "Nao existe livros com esse preco")  

#!Buscar todos os livros ate o preço(x) com ordem crescente e decrescente 
@app.route("/Livros/Valores/<ordem>/<preco>", methods=["GET"])
def select_Books_Prices(ordem,preco):
    book_obj = Livros.query.all()
    book_json = [book.to_Json2() for book in book_obj]
    books_att = [book for book in book_json if book['preco'] <= float(preco)]
    if(ordem == "C" or ordem == "c"):
        books_att_ordenado = sorted(books_att, key=lambda book: book['preco'])
        return rtn_Response(200, "livros", books_att_ordenado)
    elif(ordem == "D" or ordem == "d"):
        books_att_ordenado = sorted(books_att, key=lambda book: book['preco'], reverse=True)
        return rtn_Response(200, "livros", books_att_ordenado)
    else:
        return rtn_Response(400, "livros", {}, "Verifique os parametros de ordem e de preco algum esta errado")

#!Cadastrar Livros 
@app.route("/Livros", methods=["POST"])
def create_Book():
    body = request.get_json()
    print(body)
    
    book_obj = Livros.query.filter_by(titulo=body['titulo']).first()
    if(book_obj == None):
        try:
            book = Livros(titulo=body["titulo"], preco=body["preco"])
            db.session.add(book)
            db.session.commit()
            return rtn_Response(201, "livro", book.to_Json())
        except Exception as e:
            print("Erro", e)
            return rtn_Response(400, "livro", {}, "Erro ao cadastrar")
    else:
        return rtn_Response(400, "livros", book_obj.to_Json(), "Erro,Livro Ja Cadastrado")
    
#!Atualizar Cadastros 
@app.route("/Livros/<id>", methods=["PUT"])
def att_Book(id):
    book_obj = Livros.query.filter_by(id=id).first()
    body = request.get_json()
    
    try:
        if("titulo" in body):
            book_obj.titulo = body["titulo"]
        if("preco" in body):
            book_obj.preco = body["preco"]
            
        db.session.add(book_obj)
        db.session.commit()
        return rtn_Response(200, "livro", book_obj.to_Json(), "Atualizado com sucesso")
    except Exception as e:
        print("Erro", e)
        return rtn_Response(400, "livro", {}, "Erro ao atualizar")

#!Deletar livro por id 
@app.route("/Livros/<id>", methods=["DELETE"])
def delete_Book(id):
    book_obj = Livros.query.filter_by(id=id).first()
    
    try:
        db.session.delete(book_obj)
        db.session.commit()
        reset_Id()
        return rtn_Response(200, "livros", book_obj.to_Json(), "Deletado")
    except Exception as e:
        print("Erro", e)
        return rtn_Response(400, "livros", {}, "Erro ao deletar")

#!Response padrão para todas as requisições
def rtn_Response(status, context_Name, context, mensagem=False):
    body = {}
    body[context_Name] = context
    if(mensagem):
        body["mensagem"] = mensagem 
    
    return Response(json.dumps(body), status=status, mimetype="application/json")

app.run(debug=True)