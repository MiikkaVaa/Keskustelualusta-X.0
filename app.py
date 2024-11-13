from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db = SQLAlchemy(app)

@app.route("/")
def index():
    if not session.get("username"):
        return redirect("/login")
    
    sql = text("SELECT id, name FROM forums")
    result = db.session.execute(sql)
    forums = result.fetchall()
    return render_template("index.html",forums=forums)



@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    
    if password1 != password2:
        return render_template("wrong.html", message="Salasanat eivät täsmää")
    sql = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if user:
        return render_template("wrong.html", message="Käyttäjätunnus on jo olemassa")
    password_hash = generate_password_hash(password1)
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password_hash)")
    result = db.session.execute(sql, {"username": username, "password_hash": password_hash})
    db.session.commit()
    return redirect("/login")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    
    sql = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if user:
        password_hash = user[2]
        if check_password_hash(password_hash, password):
            session["username"] = username
            session["id"] = user[0]
            session["is_admin"] = user[3]
            return redirect("/")

    return render_template("wrong.html", message="Väärä käyttäjätunnus tai salasana")
    



@app.route("/logout")
def logout():
    del session["username"]
    del session["id"]
    del session["is_admin"]
    return redirect("/")


@app.route("/forum/<int:id>")
def forum(id):
    if not session.get("username"):
        return redirect("/login")
    sql = text("SELECT id, name FROM forums WHERE id = :id")
    result = db.session.execute(sql, {"id": id})
    forum = result.fetchone()

    return render_template("forum.html", forum=forum)


@app.route("/new_forum", methods=["GET", "POST"])
def new_forum():
    if not session.get("username"):
        return redirect("/login")
    
    if request.method == "POST":
        name = request.form["name"]
        user_id = session["id"]

        sql = text("INSERT INTO forums (name, user_id) VALUES (:name, :user_id)")
        db.session.execute(sql, {"name": name, "user_id": user_id})
        db.session.commit()
        return redirect("/")
    
    return render_template("new_forum.html")


if __name__=="__main__":
    app.run(debug=True)