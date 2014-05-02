from flask import Flask, render_template, request, flash
from hashlib import sha256
from database import *
import string,random
import re
from config import secret_key

app = Flask(__name__)
app.debug = True
app.secret_key = secret_key
nickserv_regex = re.compile(r'[^ ]+')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash(('danger','Password confirmation does not match'))
            return render_template('register.html')
        if not nickserv_regex.findall(request.form['account']):
            flash(('danger','Invalid NickServ account'))
            return render_template('register.html')
        users = session.query(User).filter(User.account == request.form['account']).filter(User.confirmed == True).count()
        if users > 0:
            flash(('danger','A user is already registered with this NickServ account. Please try again.'))
            return render_template('register.html')
        password = sha256(request.form['password']).hexdigest()
        confirmation_code = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(10)])
        u = User(account=request.form['account'], password=password, confirmation_code=confirmation_code)
        session.add(u)
        session.commit()
        flash(('success','Registration successful.'))
        return render_template('register.html',submitted=True,confirmation_code=confirmation_code)
        


if __name__ == '__main__':
    app.run()
