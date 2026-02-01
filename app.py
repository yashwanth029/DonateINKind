import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "donateinkind_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---------------- DATABASE ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure instance folder exists
instance_path = os.path.join(BASE_DIR, "instance")
os.makedirs(instance_path, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    instance_path, "donateinkind.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- UPLOAD CONFIG ----------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # user / ngo


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    contact = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)

# ---------------- HELPERS ----------------
def logged_in():
    return "user_id" in session

# ---------------- ROUTES ----------------

# Login page
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Step 1: check if user exists
        user = User.query.filter_by(username=username).first()

        if not user:
            return render_template(
                "login.html",
                error="No account found with this username"
            )

        # Step 2: check password
        if user.password != password:
            return render_template(
                "login.html",
                error="Incorrect password"
            )

        # Step 3: success
        session["user_id"] = user.id
        session["role"] = user.role
        return redirect(url_for("home"))

    return render_template("login.html")



# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        user = User(username=username, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# Home page
@app.route("/home")
def home():
    if not logged_in():
        return redirect(url_for("login"))

    query = request.args.get("q")

    if query:
        items = Item.query.filter(
            Item.name.ilike(f"%{query}%") |
            Item.item_type.ilike(f"%{query}%") |
            Item.description.ilike(f"%{query}%")
        ).all()
    else:
        items = Item.query.all()

    return render_template(
        "home.html",
        items=items,
        role=session["role"]
    )



# Donate page (USERS ONLY)
@app.route("/donate", methods=["GET", "POST"])
def donate():
    if not logged_in():
        return redirect(url_for("login"))

    if session["role"] != "user":
        return render_template(
        "home.html",
        items=Item.query.all(),
        role=session["role"],
        error="Please login as a donor user to donate items."
        )


    if request.method == "POST":
        name = request.form["item_name"]
        item_type = request.form["item_type"]
        description = request.form["description"]
        contact = request.form["contact"]
        address = request.form["address"]

        image_file = request.files.get("image")
        image_name = None

        if image_file and image_file.filename != "":
            image_name = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

        item = Item(
            name=name,
            item_type=item_type,
            description=description,
            image=image_name,
            contact=contact,
            address=address,
        )

        db.session.add(item)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("donate.html")


# Remove item (NGO ONLY)
@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    if not logged_in() or session["role"] != "ngo":
        return redirect(url_for("home"))

    item = Item.query.get_or_404(item_id)

    if item.image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], item.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("home"))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- DB INIT ----------------
with app.app_context():
    db.create_all()


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

