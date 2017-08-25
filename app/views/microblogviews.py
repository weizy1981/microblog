from app import app
from flask import render_template
from flask import flash
from flask import request
from flask import g
from flask import redirect
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.controller.usercontroller import UserController
from app.controller.full_text_search import query as search_by_text
from flask import url_for
from datetime import datetime
from app.views.forms import EditForm, NewUserForm, PostForm, SearchForm
from os.path import join
from os import remove
from app.models import session
from flask_login import login_user
from app.controller.emails import follower_notification
from app import babel
from flask_babel import gettext as _
from app.controller.translate import translate
from flask import jsonify


@babel.localeselector
def get_locale():
    language = request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    g.locale = language
    return language
    #return 'zh'

@app.route('/translate', methods = ['POST'])
@login_required
def translate_action():
    text = request.form['text']
    print(text)
    print(type(text))
    return jsonify({
        'text': translate(
            request.form['text'],
            request.form['destLang'])})


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['get', 'post'])
@app.route('/index', methods=['get', 'post'])
@app.route('/index/<int:page>', methods=['get', 'post'])
@login_required
def index(page=1):
    user = current_user
    form = PostForm()

    if form.validate_on_submit():
        post_body = form.post.data
        user_id = user.id
        nickname = user.nickname
        userController = UserController()
        userController.addpost(user_id=user_id, nickname=nickname, post_body=post_body)
        return redirect(url_for('index'))

    # get posts
    followed_posts_results = current_user.followed_posts(page=page)
    posts = followed_posts_results['posts']
    has_pre_page = followed_posts_results['has_pre_page']
    pre_page_num = followed_posts_results['pre_page_num']
    has_next_page = followed_posts_results['has_next_page']
    next_page_num = followed_posts_results['next_page_num']

    template_naeme = 'posts.html'
    return render_template(template_naeme, title='Posts', posts=posts, user=user, form=form,
                           has_next_page=has_next_page, next_page_num=next_page_num, has_pre_page=has_pre_page,
                           pre_page_num=pre_page_num)


@app.route('/hello')
def hello():
    return 'Hello World!'


@app.route('/html')
def html():
    user = {'nickname': 'Miguel'}  # fake user
    return '''
    <html>
      <head>
        <title>Home Page</title>
      </head>
      <body>
        <h1>Hello, ''' + user['nickname'] + '''</h1>
      </body>
    </html>
    '''


@app.route('/posts')
@login_required
def posts():
    # fake user
    user = current_user

    # fake array of posts
    posts = [{'author': {'nickname': 'John'}, 'body': 'Beautiful day in Portland!'},
             {'author': {'nickname': 'Susan'}, 'body': 'The Avengers movie was so cool!'}]

    template_naeme = 'posts.html'
    return render_template(template_naeme, title='Posts', posts=posts, user=user)


@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
@login_required
def user(username, page=1):
    userController = UserController()
    user = userController.query_byname(username=username)

    if user == None:
        flash('User ' + username + ' not found.')
        return redirect('/')

    # get posts
    followed_posts_results = current_user.followed_posts(page=page)
    posts = followed_posts_results['posts']
    has_pre_page = followed_posts_results['has_pre_page']
    pre_page_num = followed_posts_results['pre_page_num']
    has_next_page = followed_posts_results['has_next_page']
    next_page_num = followed_posts_results['next_page_num']

    template_naeme = 'user.html'
    return render_template(template_naeme, posts=posts, user=user,
                           has_next_page=has_next_page, next_page_num=next_page_num, has_pre_page=has_pre_page,
                           pre_page_num=pre_page_num)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        userController = UserController()
        userController.update(current_user)
        g.search_form = SearchForm()

@app.route('/search', methods=['POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_results', query=form.search.data))
    else :
        return redirect(url_for('index'))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = search_by_text(query)
    post_ids = []
    for item in results:
        post_ids.append(item['post_id'])

    if len(post_ids) == 0:
        return redirect(url_for('index'))
    else :
        userController = UserController()
        posts = userController.search_posts(post_ids=post_ids)
        template_name = 'search_results.html'
        return render_template(template_name, title='Search Results', posts=posts, query=query)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.description = form.description.data
        file = form.image.data

        if file:
            # 保存上传的文件
            fileName = str(current_user.username) + secure_filename(file.filename)
            path = join(app.config['UPLOAD_FOLDER'], fileName)

            if current_user.imgpath != 'default.jpg':
                try:
                    remove(join(app.config['UPLOAD_FOLDER'], current_user.imgpath))
                except:
                    print('There is no file to be deleted!')

            file.save(path)
            current_user.imgpath = fileName

            flash('Your changes have been saved.')

        return redirect(url_for('edit'))
    else:
        form.nickname.data = current_user.nickname
        form.description.data = current_user.description
    return render_template('edit.html', title='Edit User', form=form)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    form = NewUserForm()
    if form.validate_on_submit():
        username = form.username.data
        userController = UserController()
        user = userController.query_byname(username)
        if user:
            flash(_('The username is signned up, please use another username!'))
            render_template('newuser.html', title='Sign Up', form=form)
        else:
            password = form.password.data
            nickname = form.nickname.data
            description = form.description.data
            user = userController.add(username=username, password=password, nickname=nickname, description=description)
            login_user(user)
            return redirect(url_for('user', username=username))

    return render_template('newuser.html', title='Sign Up', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    userController = UserController()
    user = userController.query_byname(username)
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', username=username))
    u = current_user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('user', username=username))
    flash('You are now following ' + username + '!')
    follower_notification(user, current_user)

    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    userController = UserController()
    user = userController.query_byname(username)
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', username=username))
    u = current_user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('user', username=username))
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('user', username=username))
