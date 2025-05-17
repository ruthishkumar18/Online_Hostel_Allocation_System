from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'hostel_secret'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS rooms (room_no TEXT PRIMARY KEY, status TEXT, student TEXT)")
    
    # Insert default admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin123', 'admin'))

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (uname, pwd, "student"))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect('/admin')
            return redirect('/dashboard')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session and session['role'] == 'student':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM rooms WHERE student=?", (session['username'],))
        allocation = c.fetchone()
        conn.close()
        return render_template('dashboard.html', allocation=allocation)
    return redirect('/login')

@app.route('/admin')
def admin():
    if 'username' in session and session['role'] == 'admin':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM rooms")
        rooms = c.fetchall()
        conn.close()
        return render_template('admin.html', rooms=rooms)
    return redirect('/login')

@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if 'username' in session and session['role'] == 'admin':
        if request.method == 'POST':
            room = request.form['room']
            student = request.form['student']
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO rooms (room_no, status, student) VALUES (?, ?, ?)", (room, "Allocated", student))
            conn.commit()
            conn.close()
            return redirect('/admin')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role='student'")
        students = c.fetchall()
        conn.close()
        return render_template('allocate.html', students=students)
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
