import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration (PostgreSQL container connection)
# Default localhost:5432 host machine se connect karne ke liye, 
# Docker network me DATABASE_URL env var ke through host "db" ban jayega.
DEFAULT_DB_URL = "postgresql://taskuser:taskpassword@localhost:5432/taskdb"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database Model (Table Definition)
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Pending")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status
        }

#  Table creation on startup
    with app.app_context():
        db.create_all()

APP_VERSION = "v1.0.0-postgres"

@app.route("/")
def home():
    return render_template("index.html", version=APP_VERSION)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "mode": "postgresql"}), 200

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    # Database se saare tasks fetch karna
    all_tasks = Task.query.order_by(Task.id.desc()).all()
    return jsonify([task.to_dict() for task in all_tasks]), 200

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    # PostgreSQL table me record insert karna
    new_task = Task(title=title, status="Pending")
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created", "id": new_task.id}), 201

@app.route("/crash", methods=["POST"])
def crash():
    sys.exit(1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
