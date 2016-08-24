from flask import Flask
from flask import g
import json
import sqlite3

DATABASE = 'test.db'

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/url/<inputURL>')
def testDB(inputURL):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    data = cur.fetchone()
    # print("SQLite version: {}".format(data))
    qry = "select * from `url` where `origin_url` = '{}';".format(inputURL)
    data = query_db(qry, one = True)
    if data:
        # todo: judge tiny or original
        # todo: if tiny, convert into id and get info
        # todo: if original, get info
        id, originalURL, type, times, createTime = data
        urlInfo = {'result': 'succeed','id': id, 'originalURL': originalURL, 'type': type, 'visitedTimes': times, 'createTime': createTime}
        return json.dumps(urlInfo)
    else:
        # todo: create tiny url
        urlInfo = {'result': 'failed', 'data':'Error: No such url created'}
        return json.dumps(urlInfo)

def init_db():
    print("initializing data base...")
    try:
        con = sqlite3.connect('test.db')

        cur = con.cursor()
        qry = "CREATE TABLE IF NOT EXISTS `url` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `type` INTEGER, `origin_url` TEXT NOT NULL, `visited_times` INTEGER NOT NULL DEFAULT 0, `add_time` TEXT);"
        cur.execute(qry)
        print("data base initialized.")
    except sqlite3.Error:#, e:
        print("Error %s:" % sqlite3.Error)#.args[0])
        sys.exit(1)

def get_db():
    DATABASE = 'test.db'
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    init_db()
    app.run()

