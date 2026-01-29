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
