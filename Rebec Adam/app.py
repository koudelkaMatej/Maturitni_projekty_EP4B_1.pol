import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "maturitni_projekt"  # Změň pro produkci

# oprava ukládání databáze mimo požadovanou složku
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, "instance")
os.makedirs(instance_dir, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    instance_dir, "pong.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# databázové modely
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Propojení s tabulkou skóre
    scores = db.relationship("Score", backref="player", lazy=True)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goals_left = db.Column(db.Integer, nullable=False)  # Skóre hráče
    goals_right = db.Column(db.Integer, nullable=False)  # Skóre bota
    difficulty = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# webové cesty
@app.route("/")
@login_required
def home():
    # všechna skóre přihlášeného uživatele
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    # 10 nejlepších her globálně podle rozdílu skóre
    best_scores = (
        Score.query.filter(Score.goals_left > Score.goals_right)
        .order_by((Score.goals_left - Score.goals_right).desc())
        .limit(10)
        .all()
    )
    return render_template(
        "webovka.html",
        email=current_user.email,
        scores=user_scores,
        best_scores=best_scores,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Tento email už existuje.")
            return redirect(url_for("register"))

        new_user = User(
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Špatný email nebo heslo.")

    best_scores = (
        Score.query.filter(Score.goals_left > Score.goals_right)
        .order_by((Score.goals_left - Score.goals_right).desc())
        .limit(10)
        .all()
    )

    # předání best_scores do šablony
    return render_template("login.html", best_scores=best_scores)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html")


#API
@app.route("/api/check_user", methods=["POST"])
def check_user():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"exists": False, "error": "Chybí email"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    return jsonify({"exists": bool(user)}), 200


@app.route("/api/save_score", methods=["POST"])
def save_score():
    data = request.get_json()

    # Hra musí poslat email hráče
    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "Uživatel nenalezen"}), 404

    new_score = Score(
        goals_left=data["score_left"],
        goals_right=data["score_right"],
        difficulty=data["difficulty"],
        user_id=user.id,
    )

    db.session.add(new_score)
    db.session.commit()

    return jsonify({"message": "Skóre úspěšně uloženo!"}), 201


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Vytvoří databázi při prvním spuštění
    app.run(debug=True)
