from db import db
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

# Käyttäjän kirjautuminen
def login(username, password):
    sql = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if user:
        password_hash = user[2]
        if check_password_hash(password_hash, password):
            return user

    return False


# Käyttäjän rekisteröinti
def register(username, password1, password2, is_admin = False):
    sql = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if user:
        message = "Käyttäjätunnus on jo käytössä"
        return message
    
    if password1 != password2:
        message = "Salasanat menivät väärin"
        return message
    
    password_hash = generate_password_hash(password1)
    sql = text("INSERT INTO users ( username, password, is_admin) VALUES (:username, :password_hash, :is_admin)")
    db.session.execute(sql, {"username": username, "password_hash": password_hash, "is_admin": is_admin})
    db.session.commit()
    

# Käyttäjän uloskirjautuminen 
def logout():
    del session["id"]
    del session["username"]
    del session["is_admin"]


# Onko admini
def is_admin(user_id):
    sql = text("SELECT is_admin FROM users WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id})
    user = result.fetchone()
    if user is not None:
        return user[0]
    return False


# Lisää valuudet foorumiin
def add_permission(forum_id, user_id):
    try:
        sql = text("INSERT INTO permissions (forum_id, user_id) VALUES (:forum_id, :user_id)")
        db.session.execute(sql, {"forum_id": forum_id, "user_id": user_id})
        db.session.commit()
    except:
        return False