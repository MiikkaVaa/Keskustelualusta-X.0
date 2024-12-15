from app import app
from flask import redirect, render_template, request, session
import users
import messages
import secrets

@app.route("/")
def index():
    user_id = session.get("id")
    if user_id:
        forums = messages.get_forums(user_id)
        return render_template("index.html", forums = forums)
    else:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form["username"]
    password = request.form["password"]
    user = users.login(username, password)

    if not user:
        return render_template("wrong.html", message = "Väärä käyttäjätunnus tai salasana")
    
    session["id"] = user[0]
    session["username"] = user[1]
    session["is_admin"] = user[3]
    session["csrf_token"] = secrets.token_hex(16)
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username =  request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    is_admin = "is_admin" in request.form
    message = users.register(username, password1, password2, is_admin)
    
    if message:
        return render_template("wrong.html", message = message)
    
    return redirect("/login")


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/forum/<int:forum_id>")
def forum(forum_id):
    user_id = session.get("id")
    if user_id:
        if not messages.view_forum(forum_id, user_id):
            return render_template("wrong.html", message = "Sinulla ei ole oikeutta katsoa tätä foorumia")
        
        forum = messages.get_forum(forum_id)
        threads = messages.get_threads(forum_id)
        return render_template("forum.html", forum = forum, threads = threads)

    else:
        return redirect("/login")



@app.route("/forum/<int:forum_id>/thread/<int:thread_id>")
def thread(forum_id, thread_id):
    user_id = session.get("id")
    if user_id:

        if not messages.view_forum(forum_id, user_id):
            return render_template("wrong.html", message = "Sinulla ei ole oikeutta katsoa tätä viestiketjua")

        forum = messages.get_forum(forum_id)
        thread = messages.get_thread(thread_id)

        if not thread:
            return render_template("wrong.html", message = "Viestiketjua ei löytynyt")

        messages_list = messages.get_messages(thread_id)
        return render_template("thread.html", forum = forum, thread = thread, messages = messages_list)

    else:
        return redirect("/login")



@app.route("/new_forum", methods=["POST"])
def new_forum():
    if session.get("csrf_token") != request.form["csrf_token"]:
        return render_template("wrong.html", message = "Odottamaton virhe")

    user_id = session.get("id")
    if not user_id or not users.is_admin(user_id):
        return render_template("wrong.html", message = "Sinulla ei ole oikeuksia luoda uutta foorumia")

    name = request.form["name"]
    private = "private" in request.form
    wrong = messages.create_forum(name, user_id, private)

    if wrong:
        return render_template("wrong.html", message = wrong)
    return redirect("/")


@app.route("/new_thread", methods=["POST"])
def new_thread():
    if session.get("csrf_token") != request.form["csrf_token"]:
        return render_template("wrong.html", message = "Odottamaton virhe")

    user_id = session.get("id")
    if user_id:
        forum_id = request.form["forum_id"]
        message = request.form["message"]
        
        wrong = messages.create_thread(forum_id, message, user_id)
        if wrong:
            return render_template("wrong.html", message = wrong)
        
        return redirect(f"/forum/{forum_id}")

    else:
        return redirect("/login")


@app.route("/new_message", methods=["POST"])
def new_message():
    if session.get("csrf_token") != request.form["csrf_token"]:
        return render_template("wrong.html", message = "Odottamaton virhe")

    user_id = session.get("id")
    if user_id:
        forum_id = request.form["forum_id"]
        thread_id = request.form["thread_id"]
        message = request.form["message"]
        wrong = messages.create_message(thread_id, message, user_id)
        if wrong:
            return render_template("wrong.html", message = wrong)
        
        return redirect(f"/forum/{forum_id}/thread/{thread_id}")

    else:
        return redirect("/login")
    

@app.route("/search_threads")
def search_threads():
    user_id = session.get("id")
    if user_id:
        forum_id = int(request.args["forum_id"])
        forum = messages.get_forum(forum_id)
        query = request.args["query"]

        if not forum_id or not query:
            return redirect(f"/forum/{forum_id}")
        
        found_threads = messages.search_threads(query)
        forum_threads = [thread for thread in found_threads if thread[1] == forum_id]
        return render_template("forum.html", forum = forum, threads = forum_threads, query = query)
    
    else:
        return redirect("/login")
    

@app.route("/search_messages")
def search_messages():
    user_id = session.get("id")
    if user_id:
        forum_id = int(request.args["forum_id"])
        thread_id = int(request.args["thread_id"])
        forum = messages.get_forum(forum_id)
        thread = messages.get_thread(thread_id)
        query = request.args["query"]

        if not thread_id or not query:
            return redirect(f"/forum/{forum_id}/thread/{thread_id}")
        
        found_messages = messages.search_messages(query)
        thread_messages = [message for message in found_messages if message[1] == thread_id]
        return render_template("thread.html", forum = forum, thread = thread, messages = thread_messages, query = query)
    else:
        return redirect("/login")
    

@app.route("/delete", methods=["POST"])
def delete():
    user_id = session.get("id")
    if user_id:
        type = request.form["type"]
        id = request.form["id"]
        
        try:
            if type == "forum":
                if users.is_admin(user_id):
                    messages.delete_forum(id)
            
            elif type == "thread":
                messages.delete_thread(id, user_id)
            
            elif type == "message":
                messages.delete_message(id, user_id)
            
            return redirect("/")
        
        except:
            return render_template("wrong.html", message = "Ei voitu poistaa")

    else:
        return redirect("/login")
    

@app.route("/forum/<int:forum_id>/add_permission", methods=["POST"])
def add_permission(forum_id):
    if session.get("csrf_token") != request.form["csrf_token"]:
        return render_template("wrong.html", message = "Odottamaton virhe")

    user_id = session.get("id")
    if user_id:
        target_username = request.form["username"]
        target_id = users.id_by_username(target_username)
        forum = messages.get_forum(forum_id)
        forum_user_id = forum[2]
        
        if not forum:
            return render_template("wrong.html", message = "Sivua ei löytynyt")
        
        if not target_id:
            return render_template("wrong.html", message = "Käyttäjää ei löytynyt")

        if forum_user_id != user_id:
            return render_template("wrong.html", message = "Sinulla ei ole oikeutta lisätä oikeuksia")
        
        users.add_permission(forum_id, target_id)
        return redirect(f"/forum/{forum_id}")
    
    else:
        return redirect("/login")
    
