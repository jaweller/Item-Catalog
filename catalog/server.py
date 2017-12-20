from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_oauth import OAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application import Base, Platform, Games, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']


engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px height: 300px border - radius: 150px-webkit - border - radius: 150px-moz - border - radius: 150px"> '
    flash("you are logged in as %s" % login_session['username'])
    print "done!"
    return output

# Creates user


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# disconnects users from server login


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON endpoint


@app.route('/platforms/<int:platform_id>/game/JSON')
def gamesforplatformJSON(platform_id):
    platform = session.query(Platform).filter_by(id=platform_id).one()
    items = session.query(Game).filter_by(
        platform_id=platform_id).all()
    return jsonify(Games=[i.serialize for i in items])

# Show platforms


@app.route('/')
@app.route('/platform/')
def showplatforms():
    platforms = session.query(Platform).all()
    return render_template('test.html', platforms=platforms)


@app.route('/')
@app.route('/platform/<int:platform_id>/')
def gameCatalog(platform_id):
    platform = session.query(Platform).filter_by(id=platform_id).one()
    items = session.query(Games).filter_by(platform_id=platform.id)
    return render_template(
        'platform.html', platform=platform, platform_id=platform_id, items=items)

# show games


@app.route('/platform/<int:platform_id>/')
@app.route('/platform/<int:platform_id>/game/')
def showgames(platform_id):
    platform = session.query(Platform).filter_by(id=platform_id).one()
    items = session.query(Games).filter_by(
        platform_id=platform_id).all()
    return render_template('platform.html', items=items, platform=platform)

# new game


@app.route('/platform/<int:platform_id>/new/', methods=['GET', 'POST'])
def newgame(platform_id):
    if request.method == 'POST':
        newItem = Games(name=request.form['name'],
                        platform_id=platform_id, user_id=platform.user_id)
        session.add(newItem)
        session.commit()
        flash("GG New game created!")
        return redirect(url_for('gameCatalog', platform_id=platform_id))
    else:
        return render_template('newgame.html', platform_id=platform_id)


# edit game
@app.route('/platform/<int:platform_id>/<int:game_id>/edit/', methods=['GET', 'POST'])
def editgame(platform_id, game_id):
    editedItem = session.query(Games).filter_by(id=game_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            session.add(editedItem)
            session.commit()
            flash("Game was edited")
            return redirect(url_for('gameCatalog', platform_id=platform_id))
    else:
        return render_template('editgame.html', platform_id=platform_id, game_id=game_id, i=editedItem)


# delete game
@app.route('/platform/<int:platform_id>/<int:game_id>/delete/', methods=['GET', 'POST'])
def deletegame(platform_id, game_id):
    itemToDelete = session.query(Games).filter_by(id=game_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Game was deleted")
        return redirect(url_for('gameCatalog', platform_id=platform_id))
    else:
        return render_template('deletegame.html', i=itemToDelete)

# newplatform


@app.route('/platform/new/', methods=['GET', 'POST'])
def newplatform():
    if request.method == 'POST':
        newPlatform = Platform(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newPlatform)
        session.commit()
        return redirect(url_for('showplatforms'))
    else:
        return render_template('newplatform.html')

# edit platform


@app.route('/platform/<int:platform_id>/edit/', methods=['GET', 'POST'])
def editplatform(platform_id):
    editedplatform = session.query(
        Platform).filter_by(id=platform_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedplatform.name = request.form['name']
            return redirect(url_for('showplatforms'))
    else:
        return render_template(
            'editplatform.html', platform=editedplatform)

# delete platform


@app.route('/platform/<int:platform_id>/delete/', methods=['GET', 'POST'])
def deleteplatform(platform_id):
    platformdeleted = session.query(
        Platform).filter_by(id=platform_id).one()
    if request.method == 'POST':
        session.delete(platformdeleted)
        session.commit()
        return redirect(
            url_for('showplatforms', platform_id=platform_id))
    else:
        return render_template(
            'deleteplatform.html', platform=deleteplatform)


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
