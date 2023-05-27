from flask import Flask, render_template, redirect, request, session
from flask_session import Session

from functools import wraps

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from cs50 import SQL


app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "#notaking"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


# functions later to another file
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper


def date_time():
    """return a list of two index [date, time]"""
    return datetime.now().strftime("%Y-%m-%d %H:%M").split(" ")


def update_archive(which, text):
    """basically it adds the counts to the notes_archive database by default, if which is edit the e_count is one, if delete deduct the counts from the database"""
    Archive = db.execute("SELECT * FROM notes_archive WHERE user_id = ?", session["user_id"])[0]

    letter_count, d_count, e_count = 0, 0, 0
    words_count, n_count = 1, 1

    for char in text:
        if char.isalpha():
            letter_count += 1
        elif char.isspace():
            words_count += 1

    if which == "edit":
        e_count += 1
    elif which == "delete":
        letter_count *= -1
        words_count *= -1
        n_count *= -1
        d_count += 1

    l = Archive['letters_count'] + letter_count
    w = Archive['words_count'] + words_count
    n = Archive['notes_count'] + n_count
    d = Archive['deleted_notes'] + d_count
    e = Archive['edited_notes'] + e_count

    db.execute("UPDATE notes_archive SET notes_count = ?, words_count = ?, letters_count = ?, deleted_notes = ?, edited_notes = ? WHERE user_id = ?", n, w, l, d, e, session["user_id"])



@app.route("/")
def starting_page():
    if "user_id" in session:
        return redirect("/home")

    return render_template("starting-page.html")



@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect("/home")

    if request.method == "POST":

        email = request.form.get("email").lower()
        password = request.form.get("password")

        if not email or not password:
            return redirect("/login")

        User = db.execute("SELECT * FROM users WHERE user_email = ?", email)

        if len(User) != 1 or not check_password_hash(User[0]["user_password"], password):
            return render_template("login-page.html", error_message="block")

        session["user_id"] = User[0]["id"]
        session["name"] = User[0]["user_name"]

        return redirect("/home")

    else:
        return render_template("login-page.html", error_message="none")



@app.route("/register", methods=["GET", "POST"])
def register_page():
    if "user_id" in session:
        return redirect("/home")

    if request.method == "POST":

        name = request.form.get("name").upper()
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not name or not email or not password or not confirm_password or len(password) < 9:
            return redirect("/register")

        is_email_exist = db.execute("SELECT user_email FROM users WHERE user_email = ?", email)
        is_name_exist = db.execute("SELECT user_name FROM users WHERE user_email = ?", name)

        if is_email_exist:
            return render_template("register-page.html", error_message="block", error_password="none", error_name="none")
        elif is_name_exist:
            return render_template("register-page.html", error_message="none", error_password="none", error_name="block")
        elif password != confirm_password:
            return render_template("register-page.html", error_message="none", error_password="block", error_name="none")

        hash_password = generate_password_hash(password)  # encypt the password

        join_date, time = date_time()  # only need the date

        db.execute("INSERT INTO users (user_name, user_email, user_password, join_date) VALUES (?, ?, ?, ?)", name, email, hash_password, join_date)

        User = db.execute("SELECT * FROM users WHERE user_email = ?", email)

        session["user_id"] = User[0]["id"]
        session["name"] = User[0]["user_name"]

        db.execute("INSERT INTO notes_archive (user_id, notes_count, words_count, letters_count, deleted_notes, edited_notes) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], 0, 0, 0, 0, 0)

        return redirect("/home")

    else:
        return render_template("register-page.html", error_message="none", error_password="none", error_name="none")



@app.route("/home", methods=["GET", "POST"])
@login_required
def home_page():
    if request.method == "POST":
        fields = ['field1', 'field2', 'field3']  # the name of the inputs
        Fields_value = []  # the value of the inputs will append to this

        for field in fields:
            Fields_value.append(request.form.get(field).lstrip())

        for note in Fields_value:
            if note != '':
                if note == "update_user_note":  # for security reason
                    note = note.replace("_", "-")

                date, time = date_time()

                db.execute("INSERT INTO user_notes (user_id, note, date, time) VALUES (?, ?, ?, ?)", session["user_id"], note, date, time)

                update_archive("", note)

        return redirect("/home")

    else:
        Notes = db.execute("SELECT note FROM user_notes WHERE user_id = ? ORDER BY date DESC, time DESC LIMIT 3", session["user_id"])
        return render_template("home-page.html", name=session["name"].title(), Data=Notes)



@app.route("/my_notes", methods=["GET", "POST"])
@login_required
def mynotes_page():

    Notes = db.execute("SELECT * FROM user_notes WHERE user_id = ? ORDER BY date DESC, time DESC", session["user_id"])

    if request.method == "POST":
        if request.form["submit_button"] == "update_user_note":
            try:
                new_note = request.form.get("new_note").lstrip()
                old_note = request.form.get("old_note").lstrip()
            except TypeError:
                return redirect("/my_note")

            if not new_note or not old_note or new_note == "" or old_note == "":
                return redirect("/my_notes")
            elif new_note == "update_user_note":
                new_note = new_note.replace("_", "-")

            for data in Notes:
                if data['note'] == old_note:
                    update_archive("delete", old_note)
                    date, time = date_time()
                    db.execute("UPDATE user_notes SET note = ?, date = ?, time = ? WHERE user_id = ? AND note = ?", new_note, date, time, session["user_id"], old_note)
                    update_archive("edit", new_note)
                    break

            return redirect("/my_notes")

        else:
            delete_note = request.form.get("submit_button")

            if delete_note:
                for data in Notes:
                    if data['note'] == delete_note:
                        db.execute("DELETE FROM user_notes WHERE user_id = ? AND note = ?", session["user_id"], delete_note)
                        update_archive("delete", delete_note)
                        break

            return redirect("/my_notes")

    else:
        return render_template("mynotes-page.html", name=session["name"].title(), notes=Notes)




@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    Archive = db.execute("SELECT * FROM notes_archive WHERE user_id = ?", session["user_id"])

    if request.method == "POST":
        if request.form["submit_button"] == "change_password":

            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not current_password or not new_password or not confirm_password or len(new_password) < 9:
                return redirect("/profile")
            elif not check_password_hash(User[0]["user_password"], current_password):
                return render_template("user-page.html", error=True, msg="Incorrect Password!!", archive=Archive[0], user=User[0])
            elif new_password != confirm_password:
                return render_template("user-page.html", error=True, msg="Passwords Don't Match!!", archive=Archive[0], user=User[0])

            hash_password = generate_password_hash(new_password)

            db.execute("UPDATE users SET user_password = ? WHERE id = ?", hash_password, session["user_id"])

            return render_template("user-page.html", error=True, msg="password successfully changed :)", archive=Archive[0], user=User[0])

        elif request.form["submit_button"] == "deactivate_account":

            password = request.form.get("password")
            confirm_password = request.form.get("confirm_to_delete")

            if not password or not confirm_password or len(password) < 9:
                return redirect("/profile")
            elif not check_password_hash(User[0]["user_password"], password):
                return render_template("user-page.html", error=True, msg="Unable To Deactivate Incorrect Password!!", archive=Archive[0], user=User[0])
            elif password != confirm_password:
                return render_template("user-page.html", error=True, msg="Passwords Don't Match", archive=Archive[0], user=User[0])

            db.execute("DELETE FROM notes_archive WHERE user_id = ?", session["user_id"])
            db.execute("DELETE FROM user_notes WHERE user_id = ?", session["user_id"])
            db.execute("DELETE FROM users WHERE id = ?", session["user_id"])

            return redirect("/logout")

    else:
        return render_template("user-page.html", error=False, msg="", archive=Archive[0], user=User[0])




@app.route("/logout")
def logout():
    """clears the sessions and redirect the user to the starting-page"""
    session.clear()

    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)