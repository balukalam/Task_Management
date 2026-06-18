import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime   # 🔥 important
import csv
from flask import make_response

app = Flask(__name__)
app.secret_key = "task_scheduler_secret"

# 🗄️ Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            description TEXT,
            date TEXT,
            time TEXT,
            priority TEXT,
            status TEXT,
            progress INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()



# 🏠 HOME (Dashboard + Auto Complete)
@app.route('/')
def home():

    # 🔐 Check if user is logged in
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    # 🔥 AUTO UPDATE STATUS BASED ON TIME
    for task in tasks:
        task_id = task[0]
        task_date = task[2]
        task_time = task[3]

        try:
            task_datetime = datetime.strptime(task_date + " " + task_time, "%Y-%m-%d %H:%M")

            if datetime.now() > task_datetime:
                if task[6] != 'Completed':
                    cur.execute(
                        "UPDATE tasks SET status='Missed' WHERE id=?",
                        (task_id,)
        )
        except:
            pass

    conn.commit()

    # reload updated tasks
    cur.execute("SELECT * FROM tasks ORDER BY date ASC, time ASC")
    tasks = cur.fetchall()

    # 📊 Dashboard stats
    total = len(tasks)
    completed = len([t for t in tasks if t[6] == 'Completed'])
    pending = len([t for t in tasks if t[6] == 'Pending'])
    progress = len([t for t in tasks if t[6] == 'In Progress'])

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress
    )
@app.route('/search')
def search():
    query = request.args.get('q')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM tasks WHERE task_name LIKE ?",
        ('%' + query + '%',)
    )

    tasks = cur.fetchall()

    # Dashboard stats
    total = len(tasks)
    completed = len([t for t in tasks if t[5] == 'Completed'])
    pending = len([t for t in tasks if t[5] == 'Pending'])
    progress = len([t for t in tasks if t[5] == 'In Progress'])

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress
    )
@app.route('/filter/<priority>')
def filter_priority(priority):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if priority == 'all':
        cur.execute("SELECT * FROM tasks")
    else:
        cur.execute(
            "SELECT * FROM tasks WHERE priority=?",
            (priority,)
        )

    tasks = cur.fetchall()

    total = len(tasks)
    completed = len([t for t in tasks if t[5] == 'Completed'])
    pending = len([t for t in tasks if t[5] == 'Pending'])
    progress = len([t for t in tasks if t[5] == 'In Progress'])

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress
    )
@app.route('/status/<status>')
def filter_status(status):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if status == 'all':
        cur.execute("SELECT * FROM tasks")
    else:
        cur.execute(
            "SELECT * FROM tasks WHERE status=?",
            (status,)
        )

    tasks = cur.fetchall()

    total = len(tasks)
    completed = len([t for t in tasks if t[5] == 'Completed'])
    pending = len([t for t in tasks if t[5] == 'Pending'])
    progress = len([t for t in tasks if t[5] == 'In Progress'])
    missed = len([t for t in tasks if t[5] == 'Missed'])

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress,
        missed=missed
    )

# ➕ ADD TASK
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_name = request.form['task_name']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        priority = request.form['priority']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("""
    INSERT INTO tasks
    (task_name, description, date, time, priority, status, progress)
    VALUES (?, ?, ?, ?, ?, 'Pending', 0)
""", (task_name, description, date, time, priority))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_task.html')

# ✏️ EDIT TASK
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        task_name = request.form['task_name']
        date = request.form['date']
        time = request.form['time']
        priority = request.form['priority']
        status = request.form['status']

        progress = int(request.form['progress'])
        status = request.form['status']

        if status == 'Completed':
            progress = 100

        elif status == 'Pending' and progress == 100:
            progress = 0

        cur.execute("""
            UPDATE tasks
            SET task_name=?, date=?, time=?, priority=?, status=?, progress=?
            WHERE id=?
        """, (task_name, date, time, priority, status, progress, id))

        conn.commit()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    conn.close()

    return render_template('edit_task.html', task=task)

# ❌ DELETE TASK
@app.route('/delete/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# 📅 CALENDAR
@app.route('/calendar')
def calendar():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()

    conn.close()
    return render_template('calendar.html', tasks=tasks)
@app.route('/export')
def export_csv():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()

    conn.close()

    output = []

    response = make_response()
    response.headers["Content-Disposition"] = "attachment; filename=tasks.csv"
    response.headers["Content-type"] = "text/csv"

    writer = csv.writer(response.stream)

    writer.writerow([
        'Task', 'Description', 'Date',
        'Time', 'Priority', 'Status', 'Progress'
    ])

    for task in tasks:
        writer.writerow(task[1:])

    return response
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(
            request.form['password']
        )

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()

            flash("Account created successfully!")
            return redirect('/login')

        except:
            conn.close()
            flash("User already exists")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]
            return redirect('/')

        flash("Invalid email or password")

    return render_template('login.html')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':
        email = request.form['email']
        new_password = generate_password_hash(
            request.form['password']
        )

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET password=? WHERE email=?",
            (new_password, email)
        )

        conn.commit()
        conn.close()

        flash("Password updated successfully!")
        return redirect('/login')

    return render_template('forgot_password.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/complete/<int:id>')
def mark_complete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute(
        "UPDATE tasks SET status='Completed', progress=100 WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')
# ▶️ RUN
if __name__ == '__main__':
    app.run(debug=True)