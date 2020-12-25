from flask import Flask, redirect, url_for, session, request, make_response, jsonify, Response
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_declarative import Group, User, GroupSchema
import json
import os

is_prod = os.environ.get('IS_HEROKU', None)
if is_prod:
    print("running in heroku")
    react_base_url = "https://mytwitterappui.herokuapp.com"
else:
    print("running locally")
    react_base_url = "http://localhost:3000"

def resolve_truth(boolean):
    if boolean:
        return 1
    else:
        return 0

Base = declarative_base()
engine = create_engine('sqlite:///sqlalchemy_example.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
dbSession = DBSession()

# Insert an Address in the address table
# new_address = Address(post_code='00000', person=new_person)
# session.add(new_address)
# session.commit()
app = Flask(__name__, static_folder='./build', static_url_path='/')
CORS(app, support_credentials=True, resources={r"/*": {"origins": react_base_url}})
app.config.from_pyfile('config.py')
app.secret_key = "realsupersekrit"  # Replace this with your own secret!
blueprint = make_twitter_blueprint(
    api_key = app.config['TWITTER_CONSUMER_KEY'],
    api_secret = app.config['TWITTER_CONSUMER_SECRET'],
    )
app.register_blueprint(blueprint, url_prefix="/login")
app.config['CORS_HEADERS'] = 'Content-Type'

# @app.after_request
# def add_headers(response):
#     response.headers.add('Content-Type', 'application/json')
#     response.headers.add('Access-Control-Allow-Origin', react_base_url)
#     response.headers.add('Access-Control-Allow-Credentials', "true")
#     response.headers.add('Access-Control-Allow-Methods', 'PUT, GET, POST, DELETE, OPTIONS')
#     response.headers.add("Access-Control-Allow-Headers","Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, withCredentials")
#     response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length,Authorization,X-Pagination')
#     print(twitter.token)
#     return response

@app.route('/')
def index():
    if is_prod:
        return app.send_static_file('index.html')
    return redirect(react_base_url)

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')



@app.route("/login")
def login():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok

    # Insert a Person in the person table
    # new_person = User(name='new person')
    # session.add(new_person)
    # session.commit()

    response = make_response(redirect('/home'))
    return response

@app.route("/api/twitter-username")
def login_with_twitter():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok
    session['twitter_token'] = (
        twitter.token['oauth_token'],
        twitter.token['oauth_token_secret']
    )
    session['twitter_user'] = twitter.token['screen_name']
    session['twitter_user_id'] = twitter.token['user_id']
    print(twitter.token) #This is the token you are looking for
    return {"screen_name":resp.json()["screen_name"]}

@app.route("/api/groups", methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
def get_twitter_groups():

    try:
        if twitter.token:
            user = twitter.token['screen_name']
    except UserWarning:
        print("user not authorized")
        return redirect(url_for("twitter.login"))

    if request.method == "GET":
        print("getting group")
        groups = dbSession.query(Group).filter(Group.owner == "@" + session['twitter_user']).all()
        group_schema = GroupSchema(many=True)
        dump_data = group_schema.dump(groups)
        print(dump_data)
        if len(dump_data) > 0:
            print(dump_data)
            print("---------")
            print(jsonify(dump_data))
            print("---------")
            return jsonify(dump_data)
        else:
            return jsonify([])
        # return Response(jsonify(dump_data),  mimetype='application/json')

    if request.method == "DELETE":
        print("delete/leaving a group")
        print(session['twitter_user'])
        request_data = json.loads(request.data)

        # validate user is the owner of the group
        groups = dbSession.query(Group)\
            .filter(Group.owner == "@" + session['twitter_user'])\
            .filter(Group.id == request_data['groupId'])\
            .all()

        # if owner, delete group
        if len(groups) == 1:
            # delete_group = Group(groups[0])
            dbSession.delete(groups[0])
            dbSession.commit()

        else:
            print("need to remove user from groups")
            # missing code

    if request.method == "POST":
        print("adding user group")
        print(session['twitter_user'])
        request_data = json.loads(request.data)
        new_group = Group(name=request_data['groupName'],
                  owner='@' + session['twitter_user'],
                  follow_all=resolve_truth(request_data['followAll']),
                  like_all=resolve_truth(request_data['likeAll']),
                  retweet_all=resolve_truth(request_data['retweetAll'])
                  )

        dbSession.add(new_group)
        dbSession.commit()
        print("group added")
        return "success"

    return "test"


@app.route("/api/join-group", methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
def join_groups():

    if request.method == "GET":
        groups = dbSession.query(Group).all()
        group_schema = GroupSchema(many=True)
        dump_data = group_schema.dump(groups)

        print(jsonify(dump_data))
        if len(dump_data) > 0:
            return jsonify(dump_data)
        else:
            return jsonify([])

    if request.method == "POST":
        print("adding user group")


        print("group added")
        return "success"

    return "success"

@app.route("/home")
def indexHome():
    return redirect('/')

if __name__ == "__main__":
    if is_prod:
        app.run(debug=False, port=os.environ.get('PORT', 80))
    else:
        app.run(host="localhost", threaded=True, port=5000)