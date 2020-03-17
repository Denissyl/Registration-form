from flask import Flask, render_template, redirect, request, make_response, session

from data import db_session
from data.jobs import Jobs
from data.login_form import LoginForm
from data.register import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/mars_explorer.sqlite")

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
                age=form.age.data,
                position=form.position.data,
                speciality=form.speciality.data,
                address=form.address.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session_db = db_session.create_session()
            user = session_db.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                res = make_response(f"Вы авторизованы")
                session['user_email'] = user.email
                return res
            return render_template('login.html', message="Wrong login or password", form=form)
        return render_template('login.html', title='Authorization', form=form)

    @app.route('/')
    def index():
        if "user_email" in session:
            user_email = session.get("user_email")
        else:
            user_email = ''
        if user_email:
            return 'Current user = ' + user_email
        session_db = db_session.create_session()
        jobs = session_db.query(Jobs).all()
        users = session_db.query(User).all()
        names = {name.id: (name.surname, name.name) for name in users}
        return render_template("index.html", jobs=jobs, names=names, title="Work log")

    app.run()


if __name__ == '__main__':
    main()
