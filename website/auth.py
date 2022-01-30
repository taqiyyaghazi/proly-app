from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Hallo ' + str(user.first_name) +', Anda berhasil masuk!', category='success')
                login_user(user, remember=True) #Mengingat pengguna yang masuk
                return redirect(url_for('views.home'))
            else:
                flash('Password salah, coba lagi.', category='error')
        else:
            flash('Email belum terdaftar.', category='error')

    return render_template('login.html', user='login')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = 'User'

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email telah terdaftar', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, role=role, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True) #Mengingat pengguna yang masuk
            flash('Akun telah dibuat.', category='succes') #add user to database
            return redirect(url_for('views.home'))
    return render_template('sign_up.html', user='signUp')