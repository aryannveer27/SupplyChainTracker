import json
import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from blockchain import Blockchain
from roles import CREDENTIALS, ROLES
from utils import generate_qr_code
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'
bc = Blockchain()

# ─── User DB (JSON file-based) ───────────────────────────────────────────────
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ─── Auth helper ─────────────────────────────────────────────────────────────
def check_credentials(role, username, password):
    # 1. Check hardcoded credentials
    if role in CREDENTIALS:
        if username == CREDENTIALS[role]['username'] and password == CREDENTIALS[role]['password']:
            return True
    # 2. Check registered users
    users = load_users()
    key = f"{role}:{username}"
    if key in users and check_password_hash(users[key]['password'], password):
        return True
    return False

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role     = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]
        if check_credentials(role, username, password):
            session["role"]     = role
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please check your role, username and password.")
    return render_template("login.html", roles=ROLES)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role      = request.form["role"]
        username  = request.form["username"].strip()
        email     = request.form["email"].strip()
        password  = request.form["password"]
        confirm   = request.form["confirm_password"]

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.")
            return render_template("register.html", roles=ROLES)

        if password != confirm:
            flash("Passwords do not match.")
            return render_template("register.html", roles=ROLES)

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template("register.html", roles=ROLES)

        # Check if username already taken for this role
        users = load_users()
        key = f"{role}:{username}"

        # Also block overriding hardcoded accounts
        if role in CREDENTIALS and username == CREDENTIALS[role]['username']:
            flash("Username already exists for this role. Please choose another.")
            return render_template("register.html", roles=ROLES)

        if key in users:
            flash("Username already exists for this role. Please choose another.")
            return render_template("register.html", roles=ROLES)

        # Save new user
        users[key] = {
            "role":     role,
            "username": username,
            "email":    email,
            "password": generate_password_hash(password),
            "created":  datetime.now().isoformat()
        }
        save_users(users)

        flash(f"Account created successfully! Welcome, {username}. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html", roles=ROLES)


@app.route("/oauth-notice/<provider>")
def oauth_notice(provider):
    """Placeholder for OAuth — shows setup instructions."""
    return render_template("oauth_notice.html", provider=provider)


@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect(url_for("login"))
    
    # Calculate real blockchain metrics
    total_transactions = len(bc.chain) - 1 # exclude genesis
    
    # Count unique products
    products = set()
    for b in bc.chain:
        if "product_id" in b.data:
            products.add(b.data["product_id"])
    active_shipments = len(products)
    
    users = load_users()
    registered_nodes = len(users) + len(CREDENTIALS)
    
    # Get recent transactions (up to 5)
    recent_transactions = []
    for b in reversed(bc.chain):
        if b.index == 0:
            continue
        recent_transactions.append({
            "hash": b.hash[:8] + "..." + b.hash[-4:],
            "entity": b.data.get("by", "Unknown"),
            "status": "Verified",
            "timestamp": b.timestamp,
            "product_id": b.data.get("product_id")
        })
        if len(recent_transactions) >= 5:
            break

    return render_template(
        "dashboard.html", 
        role=session["role"],
        active_shipments=active_shipments,
        total_transactions=total_transactions,
        registered_nodes=registered_nodes,
        recent_transactions=recent_transactions
    )


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "role" not in session:
        return redirect(url_for("login"))

    role = session["role"]

    if request.method == "POST":
        product_id = request.form["product_id"]
        details    = request.form["description"]

        if role == "Manufacturer":
            description = f"Manufactured Product: {details}"
        elif role == "Distributor":
            description = f"Shipped from warehouse or in transit: {details}"
        elif role == "Retailer":
            description = f"Received and marked for sale: {details}"
        else:
            description = details

        bc.add_block({
            "product_id":  product_id,
            "description": description,
            "by":          role
        })

        flash(f"{role.title()} update recorded for Product ID {product_id}.")
        return redirect(url_for("dashboard"))

    return render_template("product_form.html", role=role)


@app.route("/track", methods=["GET", "POST"])
def track():
    if "role" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        pid     = request.form["product_id"]
        history = bc.get_product_history(pid)
        qr      = generate_qr_code(f"Product ID: {pid}")
        return render_template("view_history.html", history=history, pid=pid, qr=qr)

    return render_template("track_product.html")


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime(format)
    return value


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
