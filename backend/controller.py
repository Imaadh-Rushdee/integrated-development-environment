from flask import Blueprint, request, jsonify
from db import get_db

api = Blueprint("api", __name__)

# ---------------------------
# 🌲 Get full directory tree
# ---------------------------
@api.route("/tree", methods=["GET"])
def tree():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, type, parent_id
        FROM nodes
        ORDER BY type DESC, name ASC
    """)

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(rows)


# ---------------------------
# 📄 Get file content
# ---------------------------
@api.route("/file/<int:id>", methods=["GET"])
def get_file(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, content FROM nodes WHERE id=? AND type='file'",
        (id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "File not found"}), 404

    return jsonify(dict(row))


# ---------------------------
# 💾 Save file content
# ---------------------------
@api.route("/file/<int:id>", methods=["PUT"])
def save_file(id):
    data = request.json
    content = data.get("content", "")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE nodes SET content=? WHERE id=? AND type='file'",
        (content, id)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})


# ---------------------------
# ➕ Create new file
# ---------------------------
@api.route("/file", methods=["POST"])
def create_file():
    data = request.json

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO nodes (name, type, parent_id, content)
        VALUES (?, 'file', ?, '')
        """,
        (data["name"], data.get("parent_id"))
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "file_created"})


# ---------------------------
# ➕ Create new folder
# ---------------------------
@api.route("/folder", methods=["POST"])
def create_folder():
    data = request.json

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO nodes (name, type, parent_id)
        VALUES (?, 'folder', ?)
        """,
        (data["name"], data.get("parent_id"))
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "folder_created"})


# ---------------------------
# 🗑️ Delete file or folder
# ---------------------------
@api.route("/node/<int:id>", methods=["DELETE"])
def delete_node(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM nodes WHERE parent_id=?", (id,))
    cur.execute("DELETE FROM nodes WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})

import subprocess
import tempfile
import os

# ---------------------------
# 💻 Terminal Execute
# ---------------------------
@api.route("/terminal/execute", methods=["POST"])
def terminal_execute():
    command = request.json.get("command", "").strip()

    if command == "ls":
        return list_files()

    if command.startswith("cat "):
        return cat_file(command[4:])

    if command.startswith("run "):
        return run_file(command[4:])

    return jsonify({"output": "Unknown command"})


def list_files():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name FROM nodes WHERE type='file'")
    files = [row["name"] for row in cur.fetchall()]
    conn.close()

    return jsonify({"output": "\n".join(files)})


def cat_file(filename):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT content FROM nodes WHERE name=? AND type='file'",
        (filename,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"output": "File not found"})

    return jsonify({"output": row["content"]})


def run_file(filename):
    ext = filename.split(".")[-1]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT content FROM nodes WHERE name=? AND type='file'",
        (filename,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"output": "File not found"})

    code = row["content"]

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + ext) as f:
        f.write(code.encode())
        filepath = f.name

    try:
        if ext == "py":
            result = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            return jsonify({"output": f"No runner for .{ext} yet"})

        output = result.stdout + result.stderr
    finally:
        os.remove(filepath)

    return jsonify({"output": output or "No output"})
