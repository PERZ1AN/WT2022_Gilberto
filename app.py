"""
For rental system:
-check against db date
-
"""






import MySQLdb
from flask import Flask, render_template, request, redirect, session
from flask.helpers import url_for
from flask_mysqldb import MySQL

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = "secretest_secret"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'wt'
mysql = MySQL(app)

def ret_movies():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT cover FROM movies')
    movies = cursor.fetchall()
    imggrid = movies
    print(imggrid)
    return imggrid


@app.route('/')
@app.route('/home')
def homepage():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (session['email'],))
        account = cursor.fetchone()
        return render_template('homepage.html', account = account, imggrid = ret_movies())
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    if request.method == 'GET':
        if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE email = %s', (session['email'],))
            account = cursor.fetchone()
            return render_template('loginpage.html', account = account)
        return render_template('loginpage.html')
    if request.method == 'POST' and 'email' in request.form and 'psw' in request.form:
        email = request.form['email']
        psw = request.form['psw']
        print("Username: " + email + " Password: " + psw)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from accounts where email = %s and password = %s", (email, psw))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['email'] = account['email']
            session['username'] = account['username']
            return redirect(url_for('homepage', account = account))
        return redirect(url_for('loginpage'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (session['email'],))
        account = cursor.fetchone()
        return render_template('profile.html', account = account)
    return redirect(url_for('login'))

@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('loggedin')
    session.pop('email')
    session.pop('username')
    return redirect(url_for('homepage'))