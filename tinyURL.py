from flask import Flask, g, redirect, url_for, request
import json
import sqlite3
import sys
import time

DATABASE = 'test.db'
CHAR = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

app = Flask(__name__)

# Hello World
@app.route("/")
def hello():
    info = {'result': 'succeed', 'data': 'Hello World! Thank you for using my tinyURL system.'}
    print("device category: %s" % (request.user_agent.platform))
    return json.dumps(info)

# Redirect from shorten URL
@app.route('/<inputStr>')
def getOriginalURL(inputStr):
    # Judge different divices
    platform = request.user_agent.platform
    mode = 'computer'
    if platform in ['iphone', 'android', 'blackberry']:
        mode = 'mobile'
    elif platform in ['ipad']:
        mode = 'tablet'
    # else:
    #     print('computer')
    id = convertIDFromStr(inputStr)
    if id == -1:
        errMsg = {'result': 'failed', 'data':'Error: inviled character'}
        return json.dumps(errMsg)

    data = query_db('SELECT origin_url, mobile_redirect, tablet_redirect, original_times, mobile_times, tablet_times FROM url WHERE id = ?;',(str(id),), one = True)
    if data:
        originalURL, mobile, tablet, originalTimes, mobileTimes, tabletTimes = data

        # Add different time for different divices
        url = originalURL
        conditions = {'id':id}
        if mode == 'mobile' and mobile is not None:
            url = mobile
            mobileTimes = int(mobileTimes) + 1
            values = {'mobile_times': mobileTimes}
        elif mode == 'tablet' and tablet is not None:
            url = tablet
            tabletTimes = int(tabletTimes) + 1
            values = {'tablet_times': tabletTimes}
        else:
            originalTimes = int(originalTimes) + 1
            values = {'original_times':originalTimes}

        update_db('url',values,conditions)

        if url.find('http://') != 0 and url.find('https://') != 0:
            url = 'http://' + url

        return redirect(url, code=302)
    else :
        urlInfo = {'result': 'failed', 'data':'Error: Shorten URL not existed'}
        return json.dumps(urlInfo)


# Get all the urls this user generated
@app.route('/u/<user>')
def getURLList(user):
    data = query_db("SELECT * FROM url WHERE userid = ?",(user,), False)
    urlSet = []
    for urlData in data:
        id, userid, type, originalURL, mobile, tablet, originalTimes, mobileTimes, tabletTimes, createDate = urlData
        generatedURL = convertURLFromID(id)
        url = {'id': id, 'shortenURL': generatedURL, 'originalURL': originalURL, 'mobileURL':mobile, 'tabletURL':tablet, 'originalTimes': originalTimes, 'mobileTimes':mobileTimes, 'tabletTimes':tabletTimes, 'createDate': createDate}
        urlSet.append(url)
    urlInfo = {'result': 'succeed', 'data': urlSet}
    return json.dumps(urlInfo)


# Get perticular url this user generated
@app.route('/u/<user>/<inputURL>')
def getTinyURL(inputURL, user):
    # Judge tiny or original
    tinyMode = False
    id = convertIDFromStr(inputURL)

    if id == -1: #original url
        data = query_db('SELECT * FROM url WHERE origin_url = ?', (inputURL,), True)
    else:        #tiny url
        data = query_db('SELECT * FROM url WHERE id = ?', (id,), True)
        tinyMode = True

    if data:
        id, userid, type, originalURL, mobile, tablet, originalTimes, mobileTimes, tabletTimes, createDate = data
        generatedURL = convertURLFromID(id)
        urlInfo = {'result': 'succeed','id': id, 'userID': userid, 'generatedURL': generatedURL, 'originalURL': originalURL, 'mobileURL': mobile, 'tabletURL': tablet, 'originalTimes': originalTimes, 'mobileTimes':mobileTimes, 'tabletTimes':tabletTimes, 'createDate': createDate}
        return json.dumps(urlInfo)
    else:
        if tinyMode:
            urlInfo = {'result': 'failed', 'data':'Error: No such url created'}
            return json.dumps(urlInfo)
        else:
            # Create a new shorten url
            timestr = time.strftime("%Y-%m-%d %H:%M:%S.000", time.gmtime())
            id = insert_db('url', ('userid', 'origin_url', 'create_date'), (user, inputURL, timestr))

            generatedURL = convertURLFromID(id)
            url = {'id': id, 'shortenURL': generatedURL, 'originalURL': inputURL, 'createDate': timestr}
            urlInfo = {'result': 'succeed', 'data': url}
            return json.dumps(urlInfo)

# Config the url for different device
# Warning: might cause duplicate url
@app.route('/u/<user>/<shortenURL>/config/<mode>/<newURL>')
def configURL(user, shortenURL, mode, newURL):
    id = convertIDFromStr(shortenURL)
    if id == -1:
        urlInfo = {'result': 'failed', 'data':'Error: Shorten URL not existed'}
        return json.dumps(urlInfo)
    else:
        data = query_db('SELECT * FROM url WHERE id = ?', (id,), True)

        if data is not None:
            conditions = {'id': id}
            if mode == 'mobile':
                values = {'mobile_redirect': "'%s'" % (newURL), 'mobile_times': 0}
            elif mode == 'tablet':
                values = {'tablet_redirect': "'%s'" % (newURL), 'tablet_times': 0}
            else:
                values = {'origin_url': "'%s'" % (newURL), 'original_times': 0}
            update_db('url', values, conditions)
            data = query_db('SELECT * FROM url WHERE id = ?', (id,), True)
            id, userid, type, originalURL, mobile, tablet, originalTimes, mobileTimes, tabletTimes, createDate = data
            generatedURL = convertURLFromID(id)
            url = {'id': id, 'shortenURL': generatedURL, 'originalURL': originalURL, 'mobileURL':mobile, 'tabletURL':tablet, 'originalTimes': originalTimes, 'mobileTimes':mobileTimes, 'tabletTimes':tabletTimes, 'createDate': createDate}
            urlInfo = {'result': 'succeed', 'data': url}
            return json.dumps(urlInfo)
        else:
            urlInfo = {'result': 'failed', 'data':'Error: Shorten URL not existed'}
            return json.dumps(urlInfo)


def init_db():
    print('Initializing data base...')
    try:
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        urlqry = 'CREATE TABLE IF NOT EXISTS `url` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `userid` INTEGER, `type` INTEGER NOT NULL DEFAULT 0, `origin_url` TEXT NOT NULL, `mobile_redirect` TEXT, `tablet_redirect` TEXT, `original_times` INTEGER NOT NULL DEFAULT 0, `mobile_times` INTEGER, `tablet_times` INTEGER, `create_date` TEXT);'
        userqry = 'CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `username` TEXT NOT NULL);'
        cur.execute(urlqry)
        cur.execute(userqry)
        print('data base initialized.')
    except sqlite3.Error as e:
        print('Error %s:' % e.args[0])
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

def insert_db(table, fields=(), values=()):
    # g.db is the database connection
    db = get_db()
    cur = db.cursor()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ', '.join(fields), ', '.join(['?'] * len(values)))
    cur.execute(query, values)
    db.commit()
    id = cur.lastrowid
    cur.close()
    return id

def update_db(table, values={}, conditions = {}):
    db = get_db()
    cur = db.cursor()
    valuesStr = ', '.join(str(k)+'='+str(v) for (k, v) in values.items())
    conditionStr = ', '.join(str(k)+'='+str(v) for (k, v) in conditions.items())
    query = 'UPDATE %s SET %s WHERE %s' % (table, valuesStr, conditionStr)
    cur.execute(query, values)
    db.commit()
    count = cur.rowcount
    cur.close()
    return count


def convertURLFromID(id):
    total, modifiedStr = id, ''
    while total != 0:
        modifiedStr += CHAR[total % len(CHAR)]
        total //= len(CHAR)
    if len(modifiedStr) < 6:
        modifiedStr = '0'*(6-len(modifiedStr)) + modifiedStr
    generatedURL = 'localhost:5000/{}'.format(modifiedStr)
    return generatedURL

def convertIDFromStr(inputStr):
    id = 0
    for i in range(len(inputStr)):
        char = inputStr[i]
        if char in CHAR:
            curr = 0
            if 65 <= ord(char) <= 90: #A-Z
                curr = ord(char) - 29
            elif 97 <= ord(char) <= 122: #a-z
                curr = ord(char) - 87
            elif 48 <= ord(char) <= 57: #0-9
                curr = ord(char) - 48
            id = id * len(CHAR) + curr
        else :
            return -1
    return id


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    init_db()
    app.run()