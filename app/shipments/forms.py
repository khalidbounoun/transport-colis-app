from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField,
    SelectField, HiddenField, RadioField, SubmitField
)
from wtforms.validators import DataRequired, Optional, NumberRange


class ShipmentForm(FlaskForm):
    # Modes de sélection ou création
    sender_mode = RadioField('Mode', choices=[('select', 'Sélectionner'), ('new', 'Nouveau')], default='select')
    recipient_mode = RadioField('Mode', choices=[('select', 'Sélectionner'), ('new', 'Nouveau')], default='select')
    carrier_mode = RadioField('Mode', choices=[('select', 'Sélectionner'), ('new', 'Nouveau')], default='select')

    # Sélections d'existants
    sender_select = SelectField('Sélectionner un expéditeur existant', choices=[], coerce=int, validators=[Optional()])
    recipient_select = SelectField('Sélectionner un destinataire existant', choices=[], coerce=int, validators=[Optional()])
    carrier_select = SelectField('Sélectionner un transporteur existant', choices=[], coerce=int, validators=[Optional()])

    # Champs cachés
    sender_id = HiddenField('Sender ID')
    recipient_id = HiddenField('Recipient ID')
    carrier_id = HiddenField('Carrier ID')

    # Nouveaux clients/transporteurs
    sender_name = StringField('Nom de l\'expéditeur', validators=[Optional()])
    sender_phone = StringField('Téléphone de l\'expéditeur', validators=[Optional()])
    sender_address = StringField('Adresse de l\'expéditeur', validators=[Optional()])

    recipient_name = StringField('Nom du destinataire', validators=[Optional()])
    recipient_phone = StringField('Téléphone du destinataire', validators=[Optional()])
    recipient_address = StringField('Adresse du destinataire', validators=[Optional()])

    carrier_name = StringField('Nom du transporteur', validators=[Optional()])
    carrier_phone = StringField('Téléphone du transporteur', validators=[Optional()])

    # Détails de l'envoi
    destination_city = StringField('Ville de destination', validators=[DataRequired()])
    package_count = IntegerField('Nombre de colis', validators=[DataRequired(), NumberRange(min=1)])
    weight_kg = FloatField('Poids (kg)', validators=[DataRequired(), NumberRange(min=0.1)])
    price = FloatField('Prix (€)', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Remarques', validators=[Optional()])

    # 🆕 Statut de l’envoi
    status = SelectField('Statut', choices=[
        ('En transit', 'En transit'),
        ('Livré', 'Livré'),
        ('Annulé', 'Annulé')
    ])

    submit = SubmitField('Enregistrer')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        # Expéditeur
        if self.sender_mode.data == 'select':
            if not self.sender_id.data and not self.sender_select.data:
                self.sender_select.errors.append('Veuillez sélectionner un expéditeur')
                return False
        else:
            if not self.sender_name.data:
                self.sender_name.errors.append('Le nom de l\'expéditeur est requis')
                return False

        # Destinataire
        if self.recipient_mode.data == 'select':
            if not self.recipient_id.data and not self.recipient_select.data:
                self.recipient_select.errors.append('Veuillez sélectionner un destinataire')
                return False
        else:
            if not self.recipient_name.data:
                self.recipient_name.errors.append('Le nom du destinataire est requis')
                return False

        # Transporteur
        if self.carrier_mode.data == 'select':
            if not self.carrier_id.data and not self.carrier_select.data:
                self.carrier_select.errors.append('Veuillez sélectionner un transporteur')
                return False
        else:
            if not self.carrier_name.data:
                self.carrier_name.errors.append('Le nom du transporteur est requis')
                return False

        return True


class SearchForm(FlaskForm):
    search_term = StringField('Rechercher', validators=[Optional()])
    submit = SubmitField('Rechercher')
