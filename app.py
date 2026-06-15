from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import bcrypt
import os
from werkzeug.utils import secure_filename
from matcher import find_matches

app = Flask(__name__)

app.secret_key = "lostfoundsecret"

app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB']       = 'lost_found_ai'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items ORDER BY created_at DESC")
    items = cur.fetchall()
    cur.close()
    return render_template('index.html', items=items)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    name     = request.form['name']
    reg_no   = request.form['reg_no']
    email    = request.form['email']
    password = request.form['password']

    hashed = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, reg_no, email, password) VALUES (%s,%s,%s,%s)",
            (name, reg_no, email, hashed)
        )
        mysql.connection.commit()
        flash("Registration successful! Please login.", "success")
        return redirect('/login')
    except Exception as e:
        flash("Email or Register Number already exists.", "error")
        return redirect('/register')
    finally:
        cur.close()

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    email    = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", [email])
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
        session['user_id']   = user[0]
        session['user_name'] = user[1]
        return redirect('/dashboard')

    flash("Invalid email or password.", "error")
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE user_id=%s ORDER BY created_at DESC", [session['user_id']])
    items = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', items=items, name=session['user_name'])

@app.route('/post')
def post():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('post.html')

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return redirect('/login')

    title       = request.form['title']
    description = request.form['description']
    item_type   = request.form['type']
    category    = request.form['category']
    location    = request.form['location']
    contact     = request.form['contact']
    image_name  = None

    if 'image' in request.files:
        image = request.files['image']
        if image.filename != "":
            image_name = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO items (title, description, type, category, location, contact, image, user_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (title, description, item_type, category, location, contact, image_name, session['user_id']))
    mysql.connection.commit()


    opposite = 'Found' if item_type == 'Lost' else 'Lost'
    cur.execute("SELECT * FROM items WHERE type=%s", [opposite])
    other_items = cur.fetchall()
    cur.close()

    matches = find_matches(
        {'title': title, 'description': description, 'category': category, 'location': location},
        other_items
    )

    flash("Item posted successfully!", "success")

    if matches:
        flash(f"🤖 AI found {len(matches)} possible match(es) for your item!", "info")
        return render_template('matches.html', matches=matches, posted_title=title)

    return redirect('/')

@app.route('/delete_item/<int:id>')
def delete_item(id):
    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM items WHERE id=%s AND user_id=%s", [id, session['user_id']])
    mysql.connection.commit()
    cur.close()

    flash("Item deleted.", "success")
    return redirect('/dashboard')

@app.route('/claim/<int:item_id>', methods=['GET', 'POST'])
def claim(item_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        message = request.form['message']
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO claims (item_id, claimant_id, message)
            VALUES (%s,%s,%s)
        """, (item_id, session['user_id'], message))
        mysql.connection.commit()
        cur.close()
        flash("Claim submitted! The poster will be notified.", "success")
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id=%s", [item_id])
    item = cur.fetchone()
    cur.close()

    return render_template('claim.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)
