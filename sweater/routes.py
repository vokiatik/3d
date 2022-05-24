import os
import plotly.express as px
import pandas as pd
import email_validator

from dash import html, dcc
from flask import render_template, url_for, redirect, request, flash, make_response
from flask_login import login_user, login_required, logout_user, current_user
from flask_user import roles_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_principal import Principal, Permission, RoleNeed

from sweater import server, dash_app, db
from sweater.models import User, Model, Control


def chunker():
    current_chunk = int(request.form['dzchunkindex'])
    file = request.files['file']
    save_path = os.path.join('sweater/objects', file.filename)

    if os.path.exists(save_path) and current_chunk == 0:
        return 'already exists', 400
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        return "mistake", 500

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            return 'Size mismatch', 500
    return "load", 200


principals = Principal(server)
admin_permission = Permission(RoleNeed('admin'))


@server.route("/register", methods=['GET', 'POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (username or password or password2 or email):
            flash('Please fill all fields')
            return render_template('flask_user/register.html')
        elif password != password2:
            flash('Password are no equal')
            return render_template('flask_user/register.html')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('user.login'))
    elif request.method == 'GET':
        return render_template('flask_user/register.html')


@server.route("/login", methods=['GET', 'POST'])
def login():

    username = request.form.get('login')
    password = request.form.get('password')
    next_page = request.args.get('next_page')

    if not next_page:
        next_page = 'main'

    if current_user.is_authenticated:
        flash('You already logged in!')
        return redirect(url_for('profile'))

    if username and password:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('There is no such user')
            return render_template('flask_user/login.html')
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(next_page)
        else:
            flash('Password is incorrect')
    else:
        flash('Please fill login and password fields')
    return render_template('flask_user/login.html')


@server.route("/profile", methods=['GET'])
@login_required
def profile():
    return render_template('profile_page.html')


@server.route('/work_list', methods=['GET', 'POST'])
def work_list():
    models_names = db.session.query(Model.name).all()
    models_description = db.session.query(Model.description).all()
    models_project = db.session.query(Model.project).all()

    dict_with_models = {}
    for i in range(len(models_names)):
        dict_with_models[models_names[i][0]] = [models_description[i][0], models_project[i][0]]
    return render_template('list_of_models.html', models=dict_with_models)


@server.route('/three')
def three():
    name = request.args.get('name')
    model = {'name': name}
    return render_template('three.html', model=model)


@server.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@server.route('/')
def index():
    return redirect(url_for('main'))


@server.route('/main')
def main():
    return render_template('base.html')


@server.route('/upload', methods=['POST'])
@roles_required('Admin')
def upload():
    response = chunker()
    return make_response(response)


@server.route("/add_new_file", methods=['GET', 'POST'])
@roles_required('Admin')
def add_new_file():
    name = request.form.get('name')
    description = request.form.get('description')
    project = request.form.get('project')

    if request.method == 'POST':
        if name:
            new_model = Model(name=name, description=description, project=project)
            db.session.add(new_model)
            db.session.commit()
            flash('Model downloaded successfully')
            return redirect(url_for('work_list'))
    elif request.method == 'GET':
        return render_template('add_model.html')

@server.route("/works", methods=['GET', 'POST'])
@roles_required('Admin')
def works():
    models_names = db.session.query(Model.name).all()
    models_project = db.session.query(Model.project).all()
    models_description = db.session.query(Model.description).all()

    df = pd.DataFrame(columns=['model', 'project', 'description', 'words_in_description'])

    for i in range(len(models_names)):
        df = df.append(
            {'model': models_names[i][0],
             'project': models_project[i][0],
             'description': models_description[i][0]},
            ignore_index=True)

    for j in df.index:
        df.loc[j, 'words_in_description'] = len(df.at[j, 'description'].split(' '))

    fig = px.bar(df, x="model", y="words_in_description", color="project", barmode="group")

    df1 = pd.DataFrame(columns=['data', 'year', 'project'])

    for year in range(10):
        df1.loc[year, 'year'] = 2002 + year
        df1.loc[year, 'data'] = 17 + year * 2
        if year % 2 == 0:
            df1.loc[year, 'project'] = 'Project1'
        else:
            df1.loc[year, 'project'] = 'Project2'

    fig1 = px.line(df1, x="year", y="data", color="project")

    dash_app.layout = html.Div(children=[
        html.H1(children='Models dashboard'),

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        html.H1(children='Models dashboard spline'),

        dcc.Graph(
            id='example-spline',
            figure=fig1
        )
    ])
    '''name = request.args.get('name')
    obj_file = "sweater/objects/" + name + '.obj'
    '''
    return redirect(url_for('/dashboard/'))


@server.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next_page=' + request.url)
    return response


@server.route('/download', methods=['GET'])
@roles_required('Subscriber')
def download():
    model = request.args.get('name')
    pass
    flash('Download started')
    return render_template('list_of_models.html')