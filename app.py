from flask import Flask, render_template, request, flash
from hashlib import sha256
from database import *
import string,random
import re
from config import secret_key
from challenge.game import Game

app = Flask(__name__)
app.debug = False
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

def getRunningGame():
    res = session.query(GameInfo).filter(GameInfo.running == True)
    if res.count() < 1:
        return None
    else:
        return Game(res.one().path)


@app.route('/stats/')
def stats():
    game = getRunningGame()
    if not game:
        return render_templates('stats.html',game=False)
    if game:
        tracks = {}
        for track in game.tracks:
            tracks[track.name] = {'users':{}}
            for chan in range(len(track.channels)):
                j = session.query(Join).filter(Join.channel == track.channels[chan].name)
                for join in j.all():
                    tracks[track.name]['users'][join.user.account] = chan+1
            tracks[track.name]['users'] = sorted(list(tracks[track.name]['users']),key=lambda x:x[1],reverse=True)
        print(tracks)
        return render_templates('stats.html',game=True)


if __name__ == '__main__':
    app.run()
