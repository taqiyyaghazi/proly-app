from flask import Blueprint, render_template, request, Response
from flask.helpers import flash
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from . import db
from website.predict import *


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
            df = shopeeScraper(url)
        if ecommerce == 'tokopedia':
            df = tokopediaScraper(url)
            pass
        
        
        label_pos, label_neg, recommend = runApp(path, df)
        total_label = label_pos + label_neg 
        percent_pos = label_pos/total_label*100
        percent_neg = label_neg/total_label*100
    else:
        percent_neg, percent_pos = 50, 50

    return render_template('analysis.html', user=current_user, sentiment=[percent_neg, percent_pos]) 

@views.route('analysis-member', methods=['GET', 'POST'])
@login_required
def analysisMember():
    data = []
    for i in request.form.values():
        data.append(i)
    print(data)
    return render_template('analysis-member.html', user=current_user) 
