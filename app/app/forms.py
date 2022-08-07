from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired('Введите имя пользователя')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    remember_me = BooleanField('Запомнить меня', id='remember_me')
    submit = SubmitField('Войти')

class ReviewForm(FlaskForm):
    text = TextAreaField('Отзыв', validators=[DataRequired()])
    answer = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Обработать', name = 'submit')
    skip = SubmitField('Пропустить', name = 'skip')
    redirect = SubmitField('Перенаправить', name='redirect')

