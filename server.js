require('dotenv').config();
const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT || "10"),
  queueLimit: 0,
  ssl: {
    ca: fs.readFileSync('/ca.pem')
  }
});
app.post('/mark-preference', async (req, res) => {
  const { application_number, name, category, college_preference, marks } = req.body;
  console.log(application_number, name, category, college_preference, marks);
  if (!application_number || !name || !category || !college_preference || marks == null) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  try {
    const connection = await pool.getConnection();
    const [rows] = await connection.execute(
      'SELECT application_number FROM users WHERE application_number = ?',
      [application_number]
    );
    if (rows.length === 0) {
      await connection.execute(
        'INSERT INTO users (application_number, name, category, uni_code, marks) VALUES (?, ?, ?, ?, ?)',
        [application_number, name, category, college_preference, marks]
      );
    } else {
      await connection.execute(
        'UPDATE users SET category = ?, uni_code = ?, marks = ? WHERE application_number = ?',
        [category, college_preference, marks, application_number]
      );
    }
    connection.release();
    return res.json({ message: 'Preference submitted successfully' });
  } catch (error) {
    console.error('DB error:', error);
    return res.status(500).json({ error: 'Database error' });
  }
});
app.get('/ranks', async (req, res) => {
  const limit = parseInt(req.query.limit) || 100;
  const offset = parseInt(req.query.offset) || 0;
  try {
    const connection = await pool.getConnection();
    const [rows] = await connection.execute(
      `SELECT s.name, s.marks, u.uni_code, u.category
       FROM students s
       LEFT JOIN users u ON s.application_number = u.application_number
       ORDER BY s.marks DESC
       LIMIT ${limit} OFFSET ${offset}`
    );
    connection.release();
    return res.json(rows);
  } catch (error) {
    console.error('DB error:', error);
    return res.status(500).json({ error: 'Database error' });
  }
});
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});