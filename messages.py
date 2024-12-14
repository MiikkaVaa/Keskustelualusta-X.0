from db import db
import users
from sqlalchemy.sql import text

# Uusi foorumi
def create_forum(name, user_id, private=False):
    if len(name) > 20:
        return "Foorumin nimi pitää olla alle 20 merkkiä pitkä"

    if users.is_admin(user_id):
        sql = text("INSERT INTO forums (name, user_id, private) VALUES (:name, :user_id, :private) RETURNING id")
        result = db.session.execute(sql, {"name": name, "user_id": user_id, "private": private})
        forum_id = result.fetchone()[0]

        if private:
            users.add_permission(forum_id, user_id)
        db.session.commit()
        return None
    return False

# Uusi ketju foorumille
def create_thread(forum_id, message, user_id):

    if len(message) > 200:
        message = "Viestiketjun pitää olla alle 100 merkkiä pitkä"
        return message

    sql = text("INSERT INTO threads (forum_id, message, user_created) VALUES (:forum_id, :message, :user_id)")
    db.session.execute(sql, {"forum_id": forum_id, "message": message, "user_id": user_id})
    db.session.commit()
    return None


# Uusi viesti ketjuun
def create_message(thread_id, message, user_id):
    if len(message) > 200:
        return "Viestin tulee olla alle 100 merkkiä pitkä"
    
    sql = text("INSERT INTO messages (thread_id, message, user_created) VALUES (:thread_id, :message, :user_id)")
    db.session.execute(sql, {"thread_id": thread_id, "message": message, "user_id": user_id})
    db.session.commit()


# Lista foorumeista
def get_forums(user_id):
    sql = text("SELECT id, name, private FROM forums WHERE private = FALSE OR id IN (SELECT forum_id FROM permissions WHERE user_id = :user_id)")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchall()


# Lista viestiketjuista
def get_threads(forum_id):
    sql = text("SELECT id, message, user_created, time FROM threads WHERE forum_id = :forum_id")
    result = db.session.execute(sql, {"forum_id": forum_id})
    return result.fetchall()


# Lista viesteistä ketjussa
def get_messages(thread_id):
    sql = text("SELECT id, message, user_created, time FROM messages WHERE thread_id = :thread_id")
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchall()

# Hae foorumi
def get_forum(forum_id):
    sql = text("SELECT * FROM forums WHERE id = :forum_id")
    result = db.session.execute(sql, {"forum_id": forum_id})
    return result.fetchone()

# Hae Viestiketju
def get_thread(thread_id):
    sql = text("SELECT * FROM threads WHERE id = :thread_id")
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchone()


# Foorumin poisto
def delete_forum(forum_id):
    
    sql = text("DELETE FROM forums WHERE id = :forum_id")
    db.session.execute(sql, {"forum_id": forum_id})
    db.session.commit()


# Viestiketjun poisto
def delete_thread(thread_id, user_id):
    if users.is_admin(user_id):
        sql = text("DELETE FROM threads WHERE id = :thread_id")
        db.session.execute(sql, {"thread_id": thread_id})
    else:
        sql = text("DELETE FROM threads WHERE id = :thread_id AND user_created = :user_id")
        db.session.execute(sql, {"thread_id": thread_id, "user_id": user_id})
    db.session.commit()


# Viestien poisto
def delete_message(message_id, user_id):
    if users.is_admin(user_id):
        sql = text("DELETE FROM messages WHERE id = :message_id")
        db.session.execute(sql, {"message_id": message_id})
    else:
        sql = text("DELETE FROM messages WHERE id = :message_id AND user_created = :user_id")
        db.session.execute(sql, {"message_id": message_id, "user_id": user_id})
    db.session.commit()


# Viestiketjujen haku
def search_threads(query):
    sql = text("SELECT * FROM threads WHERE message LIKE :query")
    result = db.session.execute(sql, {"query": "%"+query+"%"})
    return result.fetchall()


# Viestien haku
def search_messages(query):
    sql = text("SELECT * FROM messages WHERE message LIKE :query")
    result = db.session.execute(sql, {"query": "%"+query+"%"})
    return result.fetchall()

# Voiko nähdä forumin sisällön
def view_forum(forum_id, user_id):
    sql = text("SELECT * FROM forums WHERE id = :forum_id")
    result = db.session.execute(sql, {"forum_id": forum_id})
    forum = result.fetchone()

    if forum is None:
        return False
    if not forum[3]:
        return True
    
    sql = text("SELECT id FROM permissions WHERE forum_id = :forum_id AND user_id = :user_id")
    result = db.session.execute(sql, {"forum_id": forum_id, "user_id": user_id})
    permission = result.fetchone()

    if permission is not None:
        return True