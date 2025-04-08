from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired, Optional, Email, Length

class CarrierForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=120)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class CarrierSearchForm(FlaskForm):
    search_term = StringField('Rechercher', validators=[Optional()])
    submit = SubmitField('Rechercher')