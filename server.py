from flask import Flask, render_template, request, redirect,session,flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt  

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "keep it secret"

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/create_user', methods=['POST'])
def create_user():
    if len(request.form['firstname']) < 1:
    	flash("Please enter a first name")
    if len(request.form['lastname']) < 1:
    	flash("Please enter a last name")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if len(request.form['password']) < 8:
        flash("Password must be longe than 7 characters!")
    if request.form['cpassword'] != request.form['password']:
        flash('Passwords DO NOT Match!')
    if not '_flashes' in session.keys():
        flash("You Are Successfully Added!")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])

        query= "INSERT INTO users(firstname, lastname, email, password, created_at, updated_at) VALUES (%(firstname)s,%(lastname)s,%(email)s,%(password)s,NOW(),NOW());"
        mysql=connectToMySQL("reg")
        data = {
            'firstname': request.form['firstname'],
            'lastname': request.form['lastname'],
            'email': request.form['email'],
            'password': pw_hash
        }
        user_ = mysql.query_db(query,data)
        session['user_id']= user_
        return redirect("/success")
    else: 
        return redirect("/")

@app.route("/login", methods = ['POST','GET'])
def login():

    query = "SELECT * FROM users WHERE email = %(email)s;"
    data= {
        'email': request.form['email']
    }
    mysql=connectToMySQL("reg")
    result = mysql.query_db(query, data)
    print(result)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['user_id'] = result[0]['id']
            return redirect("/success")
        else:
            flash("Password DOES NOT Match!")
            return redirect("/")
    else:
        flash("Could NOT Login!")
        return redirect("/")

    

@app.route("/success")
def success():
    if 'user_id' not in session:
        flash("You Need to Login!")
        return redirect("/")
    query = "SELECT * FROM users WHERE id= %(id)s;"
    data= {
        'id': session['user_id']
    }
    mysql=connectToMySQL("reg")
    user = mysql.query_db(query, data)
    return render_template("success.html", one_user = user[0])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")









if __name__ == "__main__":
    app.run(debug=True)