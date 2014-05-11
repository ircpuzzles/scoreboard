from flask import Flask, render_template, request, flash, jsonify
from hashlib import sha256
from database import *
import string,random
import re
from config import secret_key
from challenge.game import Game
from operator import itemgetter

app = Flask(__name__)
app.debug = False
app.secret_key = secret_key
nickserv_regex = re.compile(r'^[a-zA-Z0-9_\|`\^-]+$')

def dict_to_list(d):
    dictlist = []
    for key,value in d.iteritems():
        temp = [key,value]
        dictlist.append(temp)
    return dictlist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if request.form['tos'] != 'agree':
            flash(('danger','You must agree to the Terms of Service.'))
            return render_template('register.html')
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
        return render_template('stats.html',game=False)
    if game:
        tracks = {}
        for track in game.tracks:
            tracks[track.name] = {'users':{}}
            for chan in range(len(track.channels)):
                j = session.query(Join).filter(Join.channel == track.channels[chan].name)

                for join in j.all():
                    tracks[track.name]['users'][join.user.account] = [chan,str(join.time)]
            tracks[track.name]['users'] = sorted(dict_to_list(tracks[track.name]['users']),key=lambda x:x[1],reverse=True)
            tracks[track.name]['maxchan'] = (max(tracks[track.name]['users'],key=lambda x:x[1][0])[1][0] if tracks[track.name]['users'] else 0)
        
        return render_template('stats.html',game=True,tracks=tracks)

@app.route('/faq/')
def faq():
    return render_template('faq.html')

@app.route('/stats.json')
def stats_json():
    game = getRunningGame()
    if not game:
        return jsonify(error="Game not running")
    tracks = {}
    for track in game.tracks:
        tracks[track.name] = {'users': {}}
        for chan in range(len(track.channels)):
            j = session.query(Join).filter(Join.channel == track.channels[chan].name)
            for join in j.all():
                tracks[track.name]['users'][join.user.account] = [chan, str(join.time)]
            #tracks[track.name]['users'] = sorted(dict_to_list(tracks[track.name]['users']),key=lambda x:x[1],reverse=True)
            #tracks[track.name]['maxchan'] = (max(tracks[track.name]['users'],key=lambda x:x[1][0])[1][0] if tracks[track.name]['users'] else 0)
    return jsonify(stats=tracks)

@app.route('/tos/')
def tos():
    return render_template('tos.html')

if __name__ == '__main__':
    app.run()
