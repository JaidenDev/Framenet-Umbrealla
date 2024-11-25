from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)

# Secret key for sessions (use a more secure key in production)
app.secret_key = 'your_secret_key'

# Hardcoded user credentials (you could use a database for real applications)
USERNAME = 'admin'
PASSWORD = 'admin'

# File path for block list
BLOCK_LIST_FILE = "block_list.config"

# Load the current block list from file
def load_block_list():
    try:
        with open(BLOCK_LIST_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save the updated block list to file
def save_block_list(block_list):
    with open(BLOCK_LIST_FILE, "w") as f:
        json.dump(block_list, f, indent=4)

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "Invalid credentials, please try again."

    return render_template("login.html")

# Home route to display the login and blocked domains page
@app.route("/", methods=["GET", "POST"])
def index():
    # Check if user is logged in
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    block_list = load_block_list()

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "Add":
            domain = request.form["domain"]
            reason = request.form["reason"]
            block_list[domain] = reason
            save_block_list(block_list)
        
        elif action == "Remove":
            domain = request.form["domain"]
            if domain in block_list:
                del block_list[domain]
                save_block_list(block_list)

        return redirect(url_for("index"))

    return render_template("index.html", block_list=block_list)

# Logout route to end session
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8800)
