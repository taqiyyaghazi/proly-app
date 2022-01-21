from flask import Blueprint, render_template, request, flash, jsonify
from flask.helpers import flash
from flask_login import login_required, current_user
from sqlalchemy.sql.functions import user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) <= 1:
            flash('Catatan terlalu pendek!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Catatan telah ditambahkan.', category='success')

    return render_template('home.html', user=current_user) # Route Homepage

@views.route('analysis', methods=['GET', 'POST'])
def analysis():
    return render_template('analysis.html', user=current_user) 

@views.route('analysis-member', methods=['GET', 'POST'])
@login_required
def analysisMember():
    return render_template('analysis-member.html', user=current_user) 
