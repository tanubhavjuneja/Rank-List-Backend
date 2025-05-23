from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import pymysql
import os
load_dotenv()
app = Flask(__name__)
CORS(app)
timeout = 10  
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        db=os.environ.get("DB_NAME"),
        port=int(os.environ.get("PORT", 3306)),
        charset="utf8mb4",
        connect_timeout=timeout,
        read_timeout=timeout,
        write_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor
    )
@app.route('/mark-preference', methods=['POST'])
def mark_preference():
    data = request.get_json()
    application_number = data.get('application_number')
    name = data.get('name')
    category = data.get('category')
    college_preference = data.get('college_preference')
    marks = data.get('marks')
    if not all([application_number, name, category, college_preference]) or marks is None:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT application_number FROM users WHERE application_number = %s", (application_number,))
            result = cursor.fetchone()
            if result is None:
                cursor.execute(
                    "INSERT INTO users (application_number, name, category, uni_code, marks) VALUES (%s, %s, %s, %s, %s)",
                    (application_number, name, category, college_preference, marks)
                )
            else:
                cursor.execute(
                    "UPDATE users SET category = %s, uni_code = %s, marks = %s WHERE application_number = %s",
                    (category, college_preference, marks, application_number)
                )
            conn.commit()
        conn.close()
        return jsonify({"message": "Preference submitted successfully"})
    except Exception as e:
        print("DB error:", e)
        return jsonify({"error": "Database error"}), 500
@app.route('/ranks', methods=['GET'])
def get_ranks():
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT s.name, s.marks, u.uni_code, u.category
                FROM students s
                LEFT JOIN users u ON s.application_number = u.application_number
                ORDER BY s.marks DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        print("DB error:", e)
        return jsonify({"error": "Database error"}), 500
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
