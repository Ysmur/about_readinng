from flask_wtf import *
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[InputRequired()])
    teacher = BooleanField('Я учитель')
    parent = BooleanField('Я родитель')
    student = BooleanField('Я ученик')
    submit = SubmitField('Создать аккаунт')


class RegisterStudentForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    code_class = StringField('Код класса', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])

    submit = SubmitField('Присоединиться к классу')

class AgeForm(FlaskForm):
    age = IntegerField('Возраст', validators=[InputRequired()])
    def validate_age(form, field):
        if field.data < 13:
            return False
        return True


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class LoginStudentForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    code_class = StringField('Код класса', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditPhoto(FlaskForm):
    submit_avatar = SubmitField('Изменить')


class LogOut(FlaskForm):
    logout = SubmitField('Выйти')