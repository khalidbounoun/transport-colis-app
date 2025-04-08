from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Optional, Email, Length

class ClientForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=120)])
    address = StringField('Adresse', validators=[Optional(), Length(max=200)])
    city = StringField('Ville', validators=[Optional(), Length(max=100)])
    is_sender = BooleanField('Est expéditeur', default=True)
    is_recipient = BooleanField('Est destinataire', default=True)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class ClientSearchForm(FlaskForm):
    search_term = StringField('Rechercher', validators=[Optional()])
    submit = SubmitField('Rechercher')