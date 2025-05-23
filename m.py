import pdfplumber
import pandas as pd
import re
import mysql.connector  # Use this if MySQL, or switch to sqlite3 for SQLite

pdf_path = "List/1860CUET_MCA_2025.pdf"

data = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            lines = text.split("\n")
            for line in lines:
                if re.match(r"^\d+\s+\d{12}\s+[A-Z]{2}\d+", line):
                    tokens = line.split()
                    if len(tokens) >= 8:
                        u_rank = int(tokens[0])
                        appno = tokens[1]
                        roll = tokens[2]
                        cname = " ".join(tokens[3:-5])
                        fname = tokens[-5]
                        gender = tokens[-4]
                        marks = int(tokens[-3])
                        counselling_date = tokens[-1]
                        state = roll[:2]
                        data.append((appno, cname, marks, u_rank, roll, fname, gender, counselling_date, state))

# Connect to your MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="idkthepassword",
    database="university_app"
)
cursor = conn.cursor()

insert_query = """
INSERT INTO students (application_number, name, marks, u_rank, roll, fname, gender, counselling_date, state)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    name=VALUES(name),
    marks=VALUES(marks),
    u_rank=VALUES(u_rank),
    roll=VALUES(roll),
    fname=VALUES(fname),
    gender=VALUES(gender),
    counselling_date=VALUES(counselling_date),
    state=VALUES(state)
"""

for row in data:
    try:
        cursor.execute(insert_query, row)
    except Exception as e:
        print(f"Failed to insert {row[0]}: {e}")

conn.commit()
cursor.close()
conn.close()

print("✅ Students data imported successfully!")
