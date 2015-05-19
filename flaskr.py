# -*- coding: utf-8 -*-
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from datetime import datetime

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route('/', methods = ['GET', 'POST'])
@app.route('/user/<name>', methods=['GET', 'POST'])
def show_entries(name = "None"):
    """функция отображения главной страницы пользователей."""
    db = get_db()
    cura = db.execute('select * from zik order by id desc')
    polz = cura.fetchall()
    for i in polz:
        if (i['login'] == name) or (name == "None"):
            break
    else:
        if name != "None":
            flash('Takogo polzovatelya net')
            name = "None"
    cura = db.execute('select id,title, text, lake, dizlake, id_polzovatelya, \
                    vreamya from entries where id_polzovatelya = ? \
                    order by id desc', [name])
    entries = cura.fetchall()
    if name == "None":
        cura = db.execute('select id, title, text, lake, dizlake, \
                        id_polzovatelya, vreamya from entries order by id desc')
        entries = cura.fetchall()
    cura = db.execute('select * from kol_lak')
    zik = cura.fetchall()
    return render_template('blog.html', entries=entries, user = name, zak = zik)

@app.route('/top10', methods=['GET', 'POST'])
def top10():
    """функция возврощяет топ 10 постов."""
    db = get_db()
    cura = db.execute('select * from entries order by lake desc LIMIT 10 ')
    entries = cura.fetchall()
    cura = db.execute('select * from kol_lak')
    zik = cura.fetchall()
    return render_template('top10.html', entries=entries, zak = zik)

@app.route('/top10-7', methods=['GET', 'POST'])
def top10_7():
    """функция возврощяет топ 10 постов за неделю."""
    db = get_db()
    cura = db.execute('select id, title, text, lake, dizlake, id_polzovatelya,\
                    vreamya from entries where date(vreamya) > \
                    date(?, \'-7 day\') order by lake desc LIMIT 10 ',
                    [datetime.now()])
    entries = cura.fetchall()
    cura = db.execute('select * from kol_lak')
    zik = cura.fetchall()
    return render_template('top10_7.html', entries=entries, zak = zik)
    
@app.route('/add', methods=['POST'])
def add_entry():
    """функция добавляет пост."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text, lake, dizlake, \
                    id_polzovatelya, vreamya) values (?, ?, ?, ?, ?, ?)',
                    [request.form['title'], request.form['text'],0,0,
                    session['username'],datetime.now()])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries', name = session['username']))

@app.route('/repost-post/<id_post> <user> ', methods = ['GET', 'POST'])
def repost_post(id_post, user):
    """функция репостит пост к пользователю на страницу."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cura = db.execute('select id, title, text, lake, dizlake, \
                    id_polzovatelya, vreamya from entries \
                    where id = ? order by id desc', [id_post])
    post = cura.fetchall()
    for i in post:
        title = i["title"]
        text = i["text"]
        break
    else:
        flash('Takogo posta net')
        return redirect(url_for('show_entries', name = user))
    db.execute('insert into entries (title, text, lake, dizlake, \
                    id_polzovatelya, vreamya) values (?, ?, ?, ?, ?, ?)',
                    [title, text, 0, 0, session['username'], datetime.now()])
    db.commit()
    flash('Post dobavlen v vasy lenty')
    if user == "None":
        return redirect(url_for('top10'))
    return redirect(url_for('show_entries', name = user))

@app.route('/add-user', methods=['POST'])
def add_user():
    """функция регистрации пользователя."""
    db = get_db()
    cura = db.execute('select login from zik order by id desc')
    zik = cura.fetchall()
    signal = 1
    for entry in zik:
        if request.form['username'] == entry['login']:
            flash('takoi login yze est')
            signal = 0
            return redirect(url_for('reg'))
            break
    if signal:
        db.execute('insert into zik (login, pass) values (?, ?)',
                    [request.form['username'], request.form['password']])
    db.commit()
    return login(request.form['username'], request.form['password'])

    

@app.route('/add-like/ <id_posta> <kol_laikov> <id_polzovat>', 
                methods = ['GET', 'POST'])
def add_like(id_posta, kol_laikov, id_polzovat):
    """функция ставит лайк на пост."""
    if not session.get('logged_in'):
        abort(401)
    # проверяем ставил лайк или нет
    db = get_db()
    cura = db.execute('select polzovatel from kol_lak \
                    where post = ? and lake = 1', [int(id_posta)])
    zik = cura.fetchall()
    for i in zik:
        # если такой пользователь есть то не добавляем ещё раз
        if i["polzovatel"]: 
            flash('Vi yze stavili like')
            return redirect(url_for('show_entries', name = id_polzovat))
        
    db = get_db()
    db.execute('UPDATE entries SET lake = ? where id = ?', 
                    [int(kol_laikov) + 1, int(id_posta)])
    db.commit()
    
    # список кто ставил а кто нет 
    db = get_db()
    db.execute('insert into kol_lak (post, polzovatel,lake,dizlake) values \
                    (?,?,?,?)', [int(id_posta), session['username'], 1, 0 ])
    db.commit()
    flash('like dobavlen')
    return redirect(url_for('show_entries', name = id_polzovat))
    
@app.route('/reg', methods = ['GET', 'POST'])
def reg():
    """Функция перенаправляет на пользователя на авторизацию"""
    return render_template('login.html')
    
@app.route('/dizlake/ <id_posta> <kol_laikov> <id_polzovat>', 
                methods = ['GET', 'POST'])
def dizlake(id_posta, kol_laikov, id_polzovat):
    """функция ставит дизлайк на пост."""
    if not session.get('logged_in'):
        abort(401)
    # проверяем ставил лайк или нет
    db = get_db()
    cura = db.execute('select polzovatel from kol_lak \
                    where post = ? and dizlake = 1', [int(id_posta)])
    zik = cura.fetchall()
    for i in zik:
        # если такой пользователь есть то не добавляем ещё раз
        if i["polzovatel"]: 
            flash('Vi yze stavili dizlake')
            return redirect(url_for('show_entries', name = id_polzovat))
        
    db = get_db()
    db.execute('UPDATE entries SET dizlake = ? where id = ?',
                    [int(kol_laikov) - 1, int(id_posta)])
    db.commit()
    # список кто ставил а кто нет 
    db = get_db()
    db.execute('insert into kol_lak (post, polzovatel,lake,dizlake) values \
                    (?,?,?,?)', [int(id_posta), session['username'], 0, 1])
    db.commit()
    flash('dizlake dobavlen')
    return redirect(url_for('show_entries', name = id_polzovat))
    
@app.route('/show-like/<id_posta>', methods = ['GET', 'POST'])
def show_like(id_posta):
    """Функция возвращяет кто ставил лайк на пост."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cura = db.execute('select polzovatel from kol_lak \
                    where post = ? and lake = 1', [int(id_posta)])
    lake = cura.fetchall()
    
    cura = db.execute('select polzovatel from kol_lak \
                    where post = ? and dizlake = 1', [int(id_posta)])
    dizlak = cura.fetchall()
    return render_template('kol-lak.html', lak=lake, dizlak = dizlak)
    
    
@app.route('/profil <name> ',methods=['GET', 'POST'])
def profil(name): 
    """Профиль пользователя."""
    db = get_db()
    cura = db.execute('select id, dryg from dryzia where polzovatel = ?',
                    [name]) # Друзья пользователя
    dryzia = cura.fetchall()
    # Подписчики пользователя которых можно добавить в др
    cura = db.execute('select * from podpiski where komy = ?', 
                    [name]) 
    podpiska = cura.fetchall()
    # dobaflat ili net
    k = False 
    if session.get('logged_in'):
        k = True
        for i in dryzia:
            if i['dryg'] == session['username']:
                k = False
                break
    return render_template('zamena_login.html', user = (name), 
                    zak = dryzia, kit = k, podpisciki = podpiska)
        
@app.route('/zamena_login', methods=['GET', 'POST'])
def zamena_login():
    """Функция меняет пароль пользователя."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cura = db.execute('select dryg from dryzia where polzovatel = ?', 
                    [session['username']])
    dryzia = cura.fetchall()
    if request.method == 'POST':
        db = get_db()
        db.execute('UPDATE zik SET  pass = ? where login = ?', 
                        [request.form['password'], session['username']])
        db.commit()
        flash('danie sohraneni')
    return  profil(session['username'])
    
@app.route('/add-dryg/<polzovatel> <dryg> <id_podpicika>', 
                methods = ['GET','POST'])
def add_dryg(polzovatel, dryg, id_podpicika):
    """Пользователь у себя в профиле может добавить  подписчиков в др."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into dryzia (polzovatel, dryg) values (?, ?)',
                    [polzovatel, dryg])
                    
    db.execute('insert into dryzia (polzovatel, dryg) values (?, ?)',
                    [dryg, polzovatel])
    
    # удаляем из подписчиков 
    db.execute('DELETE FROM podpiski WHERE ID = ?', [id_podpicika])
    db.commit()
    flash('Dobavlen v dr')
    return redirect(url_for('profil', name = polzovatel))

@app.route('/dell-dryg/<polzovatel>  <id_podpicika>', methods = ['GET','POST'])
def dell_dryg(polzovatel, id_podpicika):
    """Пользователь у себя в профиле может удалить друзей."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    # удаляем из подписчиков 
    db.execute('DELETE FROM dryzia WHERE ID = ?', [id_podpicika])
    db.commit()
    flash('Ydalen iz dr')
    return redirect(url_for('profil', name = polzovatel))
    
@app.route('/dell-post/ <id_posta>', methods=['GET','POST'])
def dell_post(id_posta):
    """Пользователь у себя в профиле может добавить  подписчиков в др."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    
    cura = db.execute('select ID from entries WHERE ID = ? order by id desc',
                    [id_posta])
    polz = cura.fetchall()
    for i in polz:
        db.execute('DELETE FROM entries WHERE ID = ?', [id_posta])
        db.commit()
        flash('Post ydalen')
        break
    else:
        flash('Takogo posta net')
        return redirect(url_for('show_entries', name = session['username']))
    return redirect(url_for('show_entries', name = session['username']))
    
@app.route('/podpiska', methods=['POST'])
def podpiska():
    """функция заносит в подписчики пользователя."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    # проверяем что бы подписался 1 раз
    cura = db.execute('select kto, komy from podpiski where kto = ? and komy \
                    = ?', [request.form['polzovatel'], request.form['dryg']])
    proverka = cura.fetchall()
    for i in proverka:
        if i['kto'] == session['username']:
            flash('Vi yze v podpiskah')
            return redirect(url_for('show_entries',
                            name = request.form['dryg']))
    # если проверку прошел то подписываемся
    db = get_db()
    db.execute('insert into podpiski (kto, komy) values (?, ?)',
                    [request.form['polzovatel'], request.form['dryg']])
    db.commit()
    flash('Vi podpisalis na polzovatelya')
    return redirect(url_for('show_entries', name = request.form['dryg']))
    

    
@app.route('/login', methods=['GET', 'POST'])
def login(log = None, pas = None):
    """Функция авторизации."""
    error = False
    db = get_db()
    cura = db.execute('select login, pass from zik order by id desc')
    zik = cura.fetchall()
    signal = 0
    if request.method == 'POST':
        for entry in zik:
            if request.form['username'] == entry['login']:
                if request.form['password'] == entry['pass']:
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash('Dobro pozalovat ' + request.form['username'])
                    return redirect(url_for('show_entries', 
                                    name = session['username']))
    flash('Osibka vvoda danih')
    return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    #init_db()
    app.run()
