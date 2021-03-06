# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         if not current_user.is_authenticated:
#             return redirect(url_for('index'))

#         title = request.form['title']
#         year = request.form['year']

#         if not title or not year or len(year) > 4 or len(title) > 60:
#             flash('Invalid input.')
#             return redirect(url_for('index'))

#         movie = Movie(title=title, year=year)
#         db.session.add(movie)
#         db.session.commit()
#         flash('Item created.')
#         return redirect(url_for('index'))

#     movies = Movie.query.all()
#     return render_template('index.html', movies=movies)
@app.route('/')
def index():
    return redirect(url_for('upload_test_0'))


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('upload_test_0'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('upload_test_0'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('login'))

import os
import time
from flask import send_from_directory
from watchlist.models import Beat, Music

from pydub import AudioSegment
from pydub import effects

def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    # convert the sound with altered frame rate to a standard frame rate
    # so that regular playback programs will work right. They often only
    # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def Mixer(filepath1,format,filepath2,filename,delay,volume,speed,speed2):
    if format=='mp3':
        sound1=AudioSegment.from_mp3(filepath1)
    elif format=='wav':
        sound1=AudioSegment.from_wav(filepath1)
    sound2=AudioSegment.from_mp3(filepath2)
    sound2_speed_changed=speed_change(sound2,speed)
    # sound1_speed_changed=speed_change(sound1,speed)
    soundtmp=sound1.overlay(sound2_speed_changed,position=delay,gain_during_overlay=volume)
    # soundOutput=sound1.overlay(sound2_speed_changed,position=delay,gain_during_overlay=volume)
    soundOutput=speed_change(soundtmp,speed)
    # soundOutput=sound1_speed_changed
    soundOutput.export(filename,format="mp3")

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # ????????????????????????????????????
basedir = os.path.abspath(os.path.dirname(__file__))  # ?????????????????????????????????
ALLOWED_EXTENSIONS = set(['wav','mp3'])  # ???????????????????????????

BEATS_FOLDER = 'static/beats'
app.config['BEATS_FOLDER'] = BEATS_FOLDER

OUT_FOLDER = 'static/Mixed'
app.config['OUT_FOLDER'] = OUT_FOLDER

# ????????????????????????
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_test_0():
    beats=Beat.query.all()
    return render_template('upload2.html',beats=beats, filename="None")

# ???????????????????????????
@app.route('/upload/<filename>')
def upload_test(filename):
    beats=Beat.query.all()
    return render_template('upload2.html',beats=beats, filename=filename)

@app.route('/api', methods=['GET','POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # ??????????????????????????????
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # ???????????????????????????
    f = request.files['myfile']  # ????????????file?????????????????????myfile???????????????name???
    b = request.form.get('beat')
    d = int(request.form.get('pos'))
    delay= d
    s = request.form.get('speed')
    speed = s
    s = request.form.get('speed2')
    speed2 = s
    v = request.form.get('vol')
    volume = v
    if f and allowed_file(f.filename):  # ??????????????????????????????????????????
        fname=f.filename
        ext = fname.rsplit('.', 1)[1]  # ??????????????????
        unix_time = int(time.time())
        new_filename = str(unix_time)+'.'+ext   # ???????????????
        filepath1 = os.path.join(file_dir, new_filename)
        f.save(filepath1)  #???????????????upload??????
        

        beats_folder = os.path.join(basedir, app.config['BEATS_FOLDER'])
        filepath2 = os.path.join(beats_folder, b)
        # flash(filepath2)

        mixed_name = str(unix_time) + '_mixed.' + ext
        mixed_folder = os.path.join(basedir, app.config['OUT_FOLDER'])
        filepath3 = os.path.join(mixed_folder, mixed_name)
        # flash(filepath3)

        Mixer(filepath1,ext,filepath2,filepath3,delay,volume,float(speed),float(speed2))

        flash("????????????")
        # return render_template('upload2.html',beats=beats,filepath=filepath3)
        return redirect(url_for('upload_test',filename=mixed_name))
    else:
        flash("????????????")
        # return render_template('upload2.html',beats=beats)
        return redirect(url_for('upload_test_0'))

@app.route('/music/<filename>')
def musicplay(filename):
    beats=Music.query.all()
    return render_template('music.html',beats=beats,filename=filename)

@app.route('/music')
def music():
    beats=Music.query.all()
    return render_template('music.html',beats=beats,filename="None")
    # return render_template('music.html',beats=beats,filename="None")

@app.route('/findmusic',methods=['GET','POST'], strict_slashes=False)
def findmusic():
    b = request.form.get('beat')
    b = str(b)
    return redirect(url_for('musicplay',filename=b))

#????????????
@app.route("/download/<path:filename>")
def downloader(filename):
    dirpath = os.path.join(app.root_path, 'static/Mixed')  # ????????????????????????????????????????????????????????????????????????static/js?????????js???????????????????????????static/js???
    return send_from_directory(dirpath, filename, as_attachment=True)  # as_attachment=True ??????????????????????????????????????????????????????