print("=== FLASK APP STARTED FROM smartfilling-frontend ===")
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/form1')
def form1():
    return render_template('form1.html')

@app.route('/form2')
def form2():
    return render_template('form2.html')



@app.route('/check')
def check():
    return "OK"


if __name__ == '__main__':
    app.run(debug=True)
