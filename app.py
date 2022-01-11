from re import escape
import MySQLdb
from flask import Flask, render_template, request, redirect, session
from flask.helpers import url_for
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = "secretest_secret"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'wt'
mysql = MySQL(app)

def ret_movies():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT cover,id FROM movies')
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
    return render_template('homepage.html', imggrid = ret_movies())

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
        cursor.execute('select mid, due from rentals where cemail = %s', (session['email'],))
        rentals = cursor.fetchall()
        actives = []
        for rental in rentals:
            cursor.execute('select name from movies where id = %s', (rental['mid'],))
            mname = cursor.fetchone()
            actives.append([mname['name'], rental['due']])
        return render_template('profile.html', account = account, actives = actives)
    return redirect(url_for('loginpage'))

@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('loggedin')
    session.pop('email')
    session.pop('username')
    return redirect(url_for('homepage'))

@app.route('/movies/<id>')
def movie(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM movies WHERE id={}'.format(id))
    movie = cursor.fetchone()
    print(movie)
    return render_template('moviepage.html', movie = movie)

@app.route('/movies/rent/<id>', methods = ['POST'])
def rent(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from rentals where mid={}'.format(id))
        check = cursor.fetchone()
        if check:
            return "<h1> The movie you selected is already available to you. <a href='/home'> Return to homepage. </a></h1>"
        cursor.execute('SELECT * FROM movies WHERE id={}'.format(id))
        movie = cursor.fetchone()
        now = datetime.datetime.now()
        due = now + datetime.timedelta(days=2)
        cursor.execute("insert into rentals (cemail, mid, due) values (%s, %s, %s)", (session['email'], movie['id'], due.strftime('%Y-%m-%d %H:%M:%S')))
        mysql.connection.commit()
        return "<h1> The movie '{}' was rented at {}. <a href='/home'> Return to homepage. </a></h1>".format(movie['name'], now)
    return redirect(url_for('loginpage'))

