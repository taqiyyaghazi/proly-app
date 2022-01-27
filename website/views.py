from flask import Blueprint, render_template, request, Response, jsonify
from flask.helpers import flash
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .models import User, db
from . import db
from website.predict import *
import json


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', user=current_user) # Route Homepage



@views.route('analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        url, category, ecommerce = [x for x in request.form.values()]

        if category == 'elektronik':
            path = 'website/data/train/electronic_data.csv'
        if category == 'makanan':
            path = 'website/data/train/food_data.csv'
        if category == 'pakaian':
            path = 'website/data/train/fashion_data.csv'
        

        if ecommerce == 'shopee':
            df, runtime, product_name = shopeeScraper(url)
        if ecommerce == 'tokopedia':
            df, runtime = tokopediaScraper(url)
            pass

        if runtime >= 28:
            flash(str(len(df)) + ' ulasan berhasil dianalisis', category='succes')
        
        
        label_pos, label_neg, recommend = runApp(path, df)
        total_label = label_pos + label_neg 
        percent_pos = label_pos/total_label*100
        percent_neg = label_neg/total_label*100
    else:
        product_name = ''
        label_pos, label_neg = 0, 0
        percent_neg, percent_pos = 50, 50

    return render_template('analysis.html', user=current_user, sentiment=[percent_neg, percent_pos], neg=label_neg, pos=label_pos, product_name=product_name) 

@views.route('analysis-member', methods=['GET', 'POST'])
@login_required
def analysisMember():
    if request.method == 'POST':
        url, category, ecommerce = [x for x in request.form.values()]

        if category == 'elektronik':
            path = 'website/data/train/electronic_data.csv'
        if category == 'makanan':
            path = 'website/data/train/food_data.csv'
        if category == 'pakaian':
            path = 'website/data/train/fashion_data.csv'
        

        if ecommerce == 'shopee':
            df, runtime, product_name = shopeeScraper(url)
        if ecommerce == 'tokopedia':
            df, runtime = tokopediaScraper(url)
            pass
        
        if runtime >= 28:
            flash(str(len(df)) + ' ulasan berhasil dianalisis', category='succes')
        
        label_pos, label_neg, recommend = runApp(path, df)
        total_label = label_pos + label_neg 
        percent_pos = label_pos/total_label*100
        percent_neg = label_neg/total_label*100
    else:
        label_pos, label_neg = 0, 0
        percent_neg, percent_pos = 50, 50
        recommend = ''
        product_name = ''
    return render_template('analysis-member.html', user=current_user, username=current_user.first_name, sentiment=[percent_neg, percent_pos], recommend=recommend, neg=label_neg, pos=label_pos, product_name=product_name) 

@views.route('admin', methods=['GET', 'POST'])
@login_required
def admin():
    user_database = User.query.all()

    return render_template('admin.html', user=current_user, user_database=user_database)

@views.route('/delete-member', methods=['POST'])
def delete_member():
    user = json.loads(request.data)
    userId = user['id']
    user = User.query.get(userId)
    print(user)
    if user:
        if current_user.email == 'admin@gmail.com':
            db.session.delete(user)
            db.session.commit()

    return jsonify({})
