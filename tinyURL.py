from flask import Flask, g, redirect, url_for, request
import json
import sqlite3

DATABASE = 'test.db'
CHAR = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World! Thank you for using my tinyURL system."

@app.route('/<inputStr>')
def getOriginalURL(inputStr):
    # todo: different divices
    print(request.user_agent.platform)
    id = 0
    for i in range(len(inputStr)):
        char = inputStr[i]
        if char in CHAR:
            curr = 0
            if 65 <= ord(char) <= 90: #A-Z
                curr = ord(char) - 29
            elif 97 <= ord(char) <= 122: #a-z
                curr = ord(char) - 87
            elif 48 <= ord(char) <= 57:
                curr = ord(char) - 48
            id = id * len(CHAR) + curr
        else :
            urlInfo = {'result': 'failed', 'data':'Error: Invalid chatacters'}
            return json.dumps(urlInfo)

    data = query_db("SELECT * from url WHERE id = ?;",(str(id)), one = True)
    if data:
        id, _, type, originalURL, times, createTime = data

        # todo: times doesn't work
        times += int(times) + 1
        res = query_db("UPDATE url SET visited_times=? WHERE id=?", (str(times), str(id)))

        if originalURL is not None:
            if originalURL.find("http://") != 0 and originalURL.find("https://") != 0:
                originalURL = "http://" + originalURL

        return redirect("{}".format(originalURL), code=302)
    else :
        urlInfo = {'result': 'failed', 'data':'Error: Shorten URL not existed'}
        return json.dumps(urlInfo)

@app.route('/url/<user>/<inputURL>')
def getTinyURL(inputURL, user):
    # db = get_db()
    # cur = db.cursor()
    print(inputURL)
    data = query_db("SELECT * FROM url WHERE origin_url = ?", (inputURL,), True)
    if data:
        # todo: judge tiny or original
        # todo: if tiny, convert into id and get info
        # todo: if original, get info
        id, userid, type, originalURL, times, createTime = data
        total, modifiedStr = id, ''
        while total != 0:
            modifiedStr += CHAR[total % len(CHAR)]
            total //= len(CHAR)
        generatedURL = "localhost:5000/{}".format(modifiedStr)
        urlInfo = {'result': 'succeed','id': id, 'userID': userid, 'type': type, 'originalURL': originalURL, 'generatedURL': generatedURL, 'visitedTimes': times, 'createTime': createTime}
        return json.dumps(urlInfo)
    else:
        # todo: create tiny url
        urlInfo = {'result': 'failed', 'data':'Error: No such url created'}
        return json.dumps(urlInfo)

@app.route('/url/<user>')
def getURLList(user):
    data = query_db("SELECT * FROM url WHERE userid = ?",(user,), False)
    urlSet = []
    for urlData in data:
        id, _, type, originalURL, times, createTime = urlData
        url = {'id': id, 'originalURL': originalURL, 'type': type, 'visitedTimes': times, 'createTime': createTime}
        urlSet.append(url)
    return json.dumps(urlSet)

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

