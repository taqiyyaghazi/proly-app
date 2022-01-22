from flask import Blueprint, render_template, request, flash, jsonify
from flask.helpers import flash
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    

    return render_template('home.html', user=current_user) # Route Homepage

@views.route('analysis', methods=['GET', 'POST'])
def analysis():
    data = []
    for i in request.form.values():
        data.append(i)
    print(data)
    return render_template('analysis.html', user=current_user) 

@views.route('analysis-member', methods=['GET', 'POST'])
@login_required
def analysisMember():
    data = []
    for i in request.form.values():
        data.append(i)
    print(data)
    return render_template('analysis-member.html', user=current_user) 
