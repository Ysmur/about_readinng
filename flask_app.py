from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from flask_wtf import FlaskForm

from data import db_session
from data.users import User
from data.forms import RegisterForm, LoginForm, AgeForm, LoginStudentForm, RegisterStudentForm
from data.forms import LogOut, EditPhoto

app = Flask(__name__)
app.config['SECRET_KEY'] = 'myread_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# создаём сессию sqlalchemy
db_name = "db/myread.db"
db_session.global_init(db_name)
db_sess = db_session.create_session()

@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    if current_user.is_authenticated:
        if 'teacher' in current_user.role:
            params['teacher'] = True
        if 'parent' in current_user.role:
            params['parent'] = True
        if 'student' in current_user.role:
            params['student'] = True
    print(params)
    return render_template('base.html', **params)


@app.route('/age', methods=['GET', 'POST'])
def age():
    form = AgeForm()
    print('xa')
    if form.validate():
        print('xaxa')
        if form.validate_age(form.age):
            return redirect("/login")
        return redirect("/login_student")

    return render_template('age.html', title='Авторизация1', form=form)

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    form = LoginStudentForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.login.data).first()
        if user and user.check_password(form.code_class.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login_student.html',
                               message="Неправильный логин или код класса",
                               form=form)

    return render_template('login_student.html', title='Авторизация2', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация1', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()

    return redirect("/")

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()


    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.login.data).all()
        if user:
            for us in user:
                if user.check_password(form.code_class.data):
                    return render_template('register_student.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            role='student',
            email=form.login.data,
            age=int(form.code_class.data.split('-')[1])+7
        )
        user.set_password(form.code_class.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login_student')

    return render_template('register_student.html', title='Регистрация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        role = 'human'
        if form.teacher.data:
            role += " teacher"

        if form.parent.data:
            role += " parent"

        if form.student.data:
            role += " student"

        user = User(
            name=form.name.data,
            surname=form.surname.data,
            role=role,
            email=form.email.data,
            age=int(form.age.data)
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def go_to_profile():
    """Профиль пользователя"""

    # загружаем формы для взаимодействия с аккаунтом
    forms = (EditPhoto(), LogOut())
    params = {
        'username': current_user.name,
        'user_avatar': current_user.avatar,
        'registration_date': current_user.registration_date,
        'completed_books': current_user.completed_books,
        'forms': forms,
        'title': 'Профиль'
    }



    return render_template('profile.html', **params)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')