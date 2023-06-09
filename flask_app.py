import os
from sqlalchemy import func
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from flask_wtf import FlaskForm

from data import db_session
from data.users import User
from data.classes import Class
from data.books import Book
from data.covers import Cover
from data.genres import Genre
from data.comments import Comment
from data.forms import RegisterForm, LoginForm, AgeForm, LoginStudentForm, RegisterStudentForm, LogOut, EditPhoto
from data.forms import AddClassForm, AddStudentForm
from data.forms import BookForm, CommentBookForm, ChoiceCover

app = Flask(__name__)
app.config['SECRET_KEY'] = 'myread_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# создаём сессию sqlalchemy
db_name = "db/myread.db"
db_session.global_init(db_name)
db_sess = db_session.create_session()

def available_roles(params):
    if current_user.is_authenticated:
        if 'teacher' in current_user.role:
            params['teacher'] = True
        if 'parent' in current_user.role:
            params['parent'] = True
        if 'student' in current_user.role:
            params['student'] = True
        params['user_avatar'] = current_user.avatar
        params['username'] = current_user.name


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    if params['student']:
        current_class = str(current_user.age - 7)
        return redirect(f"/book_base/student_base_new_8_{current_class}")
    elif params['teacher']:
        current_class = 'all'
        return redirect(f"/book_base/teacher_base_1_{current_class}")
    return render_template('base.html', **params)


@app.route('/age', methods=['GET', 'POST'])
def age():
    form = AgeForm()
    if form.validate():
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

@app.route('/age_reg', methods=['GET', 'POST'])
def age_reg():
    form = AgeForm()
    if form.validate():
        if form.validate_age(form.age):
            return redirect("/register")
        return redirect("/register_student")

    return render_template('age.html', title='Авторизация1', form=form)
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()


    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.login.data).all()
        current_class = db_sess.query(Class).filter(Class.code_class == form.code_class.data).first()
        if not current_class:
            return render_template('register_student.html', title='Регистрация',
                                   form=form,
                                   message="Обратись к учителю за кодом класса")
        if user:
            for us in user:
                if us.check_password(form.code_class.data):
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
    register_date = current_user.registration_date.strftime("%B %Y")

    params = {
        'username': current_user.name,
        'user_avatar': current_user.avatar,
        'registration_date': register_date,
        'completed_books': current_user.completed_books,
        'forms': forms,
        'title': 'Профиль'
    }
    available_roles(params)
    if forms[0].validate_on_submit():
        if '.jpg' in str(request.files['file']) or '.png' in str(request.files['file']):
            input_file = request.files['file']
            if not os.path.isdir(f'static/user_data/{current_user.id}'):
                os.mkdir(f'static/user_data/{current_user.id}')
            avatar = f"{str(current_user.id)}/avatar.jpg"
            new_img = open(f'static/user_data/{avatar}', 'wb')
            new_img.write(input_file.read())
            new_img.close()

            current_user.avatar = avatar
            db_sess.merge(current_user)
            db_sess.commit()

            return redirect('/profile')


    return render_template('profile.html', **params)


@app.route('/my_classes', methods=['GET', 'POST'])
@login_required
def my_classes():
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    classes = db_sess.query(Class).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("my_classes.html", jobs=classes, names=names, title='Classes', **params)


@app.route('/new_class', methods=['GET', 'POST'])
@login_required
def addclass():
    add_form = AddClassForm()
    if add_form.validate_on_submit():
        new_class = Class(
            name=add_form.name.data,
            class_leader=current_user.id,
            code_class=f'{add_form.school.data}-{str(add_form.number_class.data)}-{add_form.letter_class.data}-',
            students=''

        )
        db_sess.add(new_class)
        db_sess.commit()
        return redirect('/my_classes')
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    return render_template('addclass.html', title='Adding a job', form=add_form, **params)

@app.route('/classes/<code_class>', methods=['GET', 'POST'])
@login_required
def class_edit(code_class):
    add_form = AddStudentForm()
    current_class = db_sess.query(Class).filter(Class.code_class == code_class).first()
    if add_form.validate_on_submit():
        max_id = db_sess.query(func.max(User.id)).scalar()
        user = User(
            email=add_form.login.data,
            name=add_form.name.data,
            surname=add_form.surname.data,
            role='student',
            age=int(code_class.split('-')[1]) + 7)
        user.set_password(code_class)
        db_sess.add(user)
        db_sess.commit()

        current_class.students += f' {max_id + 1}'
        db_sess.merge(current_class)
        db_sess.commit()
        return redirect('/my_classes')

    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    users = db_sess.query(User).all()
    names = {str(name.id): (name.surname, name.name, name.email) for name in users}
    return render_template('addstudent.html', form=add_form, names=names, current_class=current_class, **params)

@app.route('/book_base/<action>', methods=['GET'])
@login_required
def student_base(action):
    """
    action: role_work_genre_class
    """
    print(action)
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    genres = db_sess.query(Genre).all()
    if "student_base" in action:
        current_class = action.split('_')[-1]
        work = action.split('_')[-3]
        genre = (action.split('_')[-2])
        if work == 'new':
            books = db_sess.query(Book).filter(Book.for_class.like(f'%{current_class}%')).filter(Book.genre_id == genre).all()
            return render_template("student_base.html", current_class=current_class, current_genre=genre,
                                   work=work, books=books, genres=genres, title='Books', **params)
    if "teacher_base" in action:
        current_class = action.split('_')[-1]
        if current_class == 'all':
            books = db_sess.query(Book).all()
            return render_template("teacher_base.html", current_class=current_class, genres=genres,
                                   current_genre=action.split('_')[-2], books=books, title='Books', **params)
        else:
            books = db_sess.query(Book).filter(Book.for_class.like(f'%{current_class}%')).all()
            return render_template("teacher_base.html", current_class=current_class, genres=genres,
                                   books=books, title='Books', **params)
    return redirect('/')


@app.route('/books/<book_id>', methods=['GET', 'POST'])
@login_required
def book(book_id):
    form_task = BookForm()
    if form_task.validate_on_submit():
        return redirect(f'/student_book/t1/{book_id}')
    form_comment = CommentBookForm()
    if form_comment.validate_on_submit():
        comment = Comment(
        content=form_comment.content.data,
        is_private=form_comment.is_private.data,
        book_id=book_id,
        user_id=current_user.id)

        db_sess.add(comment)
        db_sess.commit()

        return redirect(f'/books/{book_id}')

    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)

    my_comments = db_sess.query(Comment).filter(Comment.book_id == book_id).filter(Comment.user_id == current_user.id).all()
    comments = db_sess.query(Comment).filter(Comment.book_id == book_id).filter(Comment.user_id != current_user.id).filter(Comment.is_private != True).all()
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    return render_template('current_book.html',
                           form_task=form_task, form_comment=form_comment,
                           book=current_book, my_comments=my_comments, comments=comments, **params)



@app.route('/student_book/t1/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task1(book_id):
    """
    Страница заданий для ученика по конкретной книге
    :param tacks: bookid_task
    :return:
    """
    form = ChoiceCover()
    if form.validate_on_submit():
        print('image2')
    form1 = ChoiceCover()
    if form1.validate_on_submit():
        print('image1')
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task1.html', current_book=current_book, form=form,  form1=form1, work='1', **params)

@app.route('/student_book/t2/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task2(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task2.html', current_book=current_book, work='2', **params)

@app.route('/student_book/t3/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task3(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task3.html', current_book=current_book, work='3', **params)

@app.route('/student_book/t4/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task4(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task4.html', current_book=current_book, work='4', **params)


@app.route('/student_book/t5/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task5(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task5.html', current_book=current_book, work='5', **params)


@app.route('/student_book/t6/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task6(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task6.html', current_book=current_book, work='6', **params)


@app.route('/student_book/t7/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task7(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task7.html', current_book=current_book, work='7', **params)


@app.route('/student_book/t8/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task8(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task8.html', current_book=current_book, work='8', **params)


@app.route('/student_book/t9/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task9(book_id):
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False}
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    print('xa', book_id)
    return render_template('student_task9.html', current_book=current_book, work='9', **params)


@app.route('/student_book/t10/<book_id>', methods=['GET', 'POST'])
@login_required
def student_task10(book_id):
    form = EditPhoto()
    params = {'is_registered': current_user.is_authenticated,
              'teacher': False,
              'parent': False,
              'student': False
              }
    available_roles(params)
    current_book = db_sess.query(Book).filter(Book.id == book_id).first()
    current_cover = db_sess.query(Cover).filter(Cover.book_id == book_id).filter(Cover.user_id == current_user.id).all()
    if not current_cover:
        cover = 'listt.png'
    else:
        cover = current_cover[0].avatar
        print('xaxa', cover)
    if form.validate_on_submit():
        if '.jpg' in str(request.files['file']) or '.png' in str(request.files['file']):
            input_file = request.files['file']
            if not os.path.isdir(f'static/user_data/{current_user.id}/{str(book_id)}'):
                os.mkdir(f'static/user_data/{current_user.id}/{str(book_id)}')
            cover = f"{str(current_user.id)}/{str(book_id)}/cover0.jpg"
            new_img = open(f'static/user_data/{cover}', 'wb')
            new_img.write(input_file.read())
            new_img.close()
            cover = cover
            print(cover)
            current_cover = Cover(
                avatar=cover,
                user_id=current_user.id,
                book_id=book_id,
                likes='1',
                about='Обложка',
                status=0)
            db_sess.add(current_cover)
            db_sess.commit()

            return redirect(f'/student_book/t10/{book_id}')
    return render_template('student_task10.html', current_book=current_book, cover=cover, form=form, work='10', **params)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')

    # s = open("static/book_data/genres.txt", encoding='utf-8').read().split('\n')
    # for i in s[:-1]:
    #     print(i)
    #     user = Genre()
    #     user.title = i
    #     db_sess = db_session.create_session()
    #     db_sess.add(user)
    #     db_sess.commit()
    #
    # user = Book()
    # user.genre_id = 1
    # user.author = 'Э. Успенский'
    # user.title = 'Следствие ведут колобки'
    # user.for_class = '2 3 4'
    # user.about = 'Цикл повестей про Неотложный Пункт Добрых Дел и его неизменных сотрудников, Колобка, Булочкина и Колбочкину'
    #
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()