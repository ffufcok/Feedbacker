from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, ReviewForm
from app.models import User
from app.models import Review
from app.main import bot
from aiogram.types import Message

def inverse(a):
    if a==0:
        return 1
    else:
        return 0


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    form = ReviewForm()
    item = (Review.query.where(Review.is_done != 1).where(Review._group == current_user._group).filter_by(executor=current_user.id).first())


    if item is None:
        return render_template('index.html', title='Home', form=form,
                               items=item)  # render_template('index.html', title='Home', form=form, items=item)
    else:
        form.text.data = item.text

        if request.args.get('submit'):
            answer = request.args.get('answer')

            item.answer = answer
            item.is_done = True

            db.session.commit()
            print('check')
            userr = User.query.where(User.id==current_user.id).first()
            userr.queue-=1

            async def send_message(answer):
                await bot.send_message(item.user_id, 'Здравствуйте!\nОтвет тех. поддержки на ваш отзыв:\n' + answer)
            #message = Message()
            send_message(answer)
            #message.text = answer

            #bot_answer(message)
            db.session.commit()
            return redirect(url_for('index'))


        if request.args.get('skip'):
            print('skip')
            item.is_done = True
            print(item)

            review = Review(text=item.text,executor=item.executor,_group=item._group)
            db.session.add(review)

            db.session.commit()

            return redirect(url_for('index'))

        if request.args.get('redirect'):
            print('redirect')
            item.is_done = True
            print(item)

            review = Review(text=item.text,executor=item.executor,is_done=0,date_create=item.date_create,_group=inverse(item._group))

            db.session.add(review)
            print('check')
            userr = User.query.where(User.id == current_user.id).first()
            userr.queue -= 1
            db.session.commit()

            return redirect(url_for('index'))

    return render_template('index.html', title='Home', form=form, items=item)






@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if request.args.get('submit'):
        username = request.args.get('username')
        password = request.args.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        print(form.remember_me.data)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#@app.route('/register', methods=['GET', 'POST'])
#def register():
#    if current_user.is_authenticated:
#        return redirect(url_for('index'))
#    form = RegistrationForm()
#    if form.validate_on_submit():
#        user = User(username=form.username.data)
#        user.set_password(form.password.data)
#        db.session.add(user)
#        db.session.commit()
#        flash('Congratulations, you are now a registered user!')
#        return redirect(url_for('login'))
#    return render_template('register.html', title='Register', form=form)
