from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt

app = Flask(__name__)
app.secret_key = "tajny_klic"

# uložiště uživatelů (email → hashed heslo)
users = {}


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']

        if email in users:
            error = "Uživatel už existuje."
        else:
            hashed = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )
            users[email] = hashed
            return redirect(url_for('login'))

    return render_template('formular/register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']

        if email in users:
            if bcrypt.checkpw(
                password.encode('utf-8'),
                users[email]
            ):
                session['email'] = email
                return redirect(url_for('home'))
            else:
                error = "Špatné heslo."
        else:
            error = "Uživatel neexistuje."

    return render_template('formular/login.html', error=error)


@app.route('/home')
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    return render_template('formular/home.html', email=session['email'])


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
