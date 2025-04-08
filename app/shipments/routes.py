from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.shipments import bp
from app.shipments.forms import ShipmentForm, SearchForm
from app.models import Shipment, Client, Carrier
from sqlalchemy import or_

@bp.route('/', methods=['GET'])
@login_required
def list_shipments():
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    
    query = Shipment.query
    
    search_term = request.args.get('search_term', '')
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(or_(
            Shipment.sender_name.like(search_term),
            Shipment.recipient_name.like(search_term),
            Shipment.destination_city.like(search_term),
            Shipment.carrier_name.like(search_term)
        ))
    
    shipments = query.order_by(Shipment.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('shipments/list.html', title='Liste des Envois', 
                          shipments=shipments, search_form=search_form, search_term=search_term)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_shipment():
    form = ShipmentForm()
    if form.validate_on_submit():
        # Création de l'objet shipment avec les informations de base
        shipment = Shipment(
            # Informations d'envoi
            destination_city=form.destination_city.data,
            package_count=form.package_count.data,
            weight_kg=form.weight_kg.data,
            price=form.price.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        
        # Traitement de l'expéditeur
        if form.sender_mode.data == 'select':
            # Utilisation d'un expéditeur existant
            sender_id = form.sender_id.data or form.sender_select.data
            if sender_id:
                client = Client.query.get(sender_id)
                shipment.sender_id = client.id
                shipment.sender_name = client.name
                shipment.sender_phone = client.phone
                shipment.sender_address = client.address
        else:
            # Création d'un nouvel expéditeur
            shipment.sender_name = form.sender_name.data
            shipment.sender_phone = form.sender_phone.data
            shipment.sender_address = form.sender_address.data
            
            # Création de l'entité Client
            new_sender = Client(
                name=form.sender_name.data,
                phone=form.sender_phone.data,
                address=form.sender_address.data,
                is_sender=True,
                is_recipient=False
            )
            db.session.add(new_sender)
            db.session.flush()  # Pour obtenir l'ID
            shipment.sender_id = new_sender.id
            
        # Traitement du destinataire (même logique)
        if form.recipient_mode.data == 'select':
            recipient_id = form.recipient_id.data or form.recipient_select.data
            if recipient_id:
                client = Client.query.get(recipient_id)
                shipment.recipient_id = client.id
                shipment.recipient_name = client.name
                shipment.recipient_phone = client.phone
                shipment.recipient_address = client.address
        else:
            shipment.recipient_name = form.recipient_name.data
            shipment.recipient_phone = form.recipient_phone.data
            shipment.recipient_address = form.recipient_address.data
            
            new_recipient = Client(
                name=form.recipient_name.data,
                phone=form.recipient_phone.data,
                address=form.recipient_address.data,
                city=form.destination_city.data,
                is_sender=False,
                is_recipient=True
            )
            db.session.add(new_recipient)
            db.session.flush()
            shipment.recipient_id = new_recipient.id
            
        # Traitement du transporteur (même logique)
        if form.carrier_mode.data == 'select':
            carrier_id = form.carrier_id.data or form.carrier_select.data
            if carrier_id:
                carrier = Carrier.query.get(carrier_id)
                shipment.carrier_id = carrier.id
                shipment.carrier_name = carrier.name
                shipment.carrier_phone = carrier.phone
        else:
            shipment.carrier_name = form.carrier_name.data
            shipment.carrier_phone = form.carrier_phone.data
            
            new_carrier = Carrier(
                name=form.carrier_name.data,
                phone=form.carrier_phone.data
            )
            db.session.add(new_carrier)
            db.session.flush()
            shipment.carrier_id = new_carrier.id
        
        shipment.status = form.status.data  #Ajout du statut


        # Enregistrement final
        db.session.add(shipment)
        db.session.commit()
        flash('Nouvel envoi enregistré avec succès!')
        return redirect(url_for('shipments.list_shipments'))
        
    return render_template('shipments/add.html', title='Ajouter un envoi', form=form)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    return render_template('shipments/view.html', title='Détails de l\'envoi', shipment=shipment)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    db.session.delete(shipment)
    db.session.commit()
    flash('Envoi supprimé avec succès!')
    return redirect(url_for('shipments.list_shipments'))    

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    form = ShipmentForm(obj=shipment)
    
    # Pré-remplir les IDs des tiers associés
    form.status.data = shipment.status  # Pré-remplissage
    if shipment.sender_id:
        form.sender_id.data = shipment.sender_id
    if shipment.recipient_id:
        form.recipient_id.data = shipment.recipient_id
    if shipment.carrier_id:
        form.carrier_id.data = shipment.carrier_id
        
    if form.validate_on_submit():
        shipment.status = form.status.data
        # Vérifier que l'on a au moins un expéditeur, destinataire et transporteur
        has_sender = form.sender_id.data or form.sender_name.data
        has_recipient = form.recipient_id.data or form.recipient_name.data
        has_carrier = form.carrier_id.data or form.carrier_name.data
        
        if not (has_sender and has_recipient and has_carrier):
            if not has_sender:
                form.sender_name.errors.append('Veuillez sélectionner un expéditeur existant ou saisir un nom')
            if not has_recipient:
                form.recipient_name.errors.append('Veuillez sélectionner un destinataire existant ou saisir un nom')
            if not has_carrier:
                form.carrier_name.errors.append('Veuillez sélectionner un transporteur existant ou saisir un nom')
            return render_template('shipments/edit.html', title='Modifier l\'envoi', form=form, shipment=shipment)
        
        # Mise à jour des informations d'expédition
        shipment.sender_name = form.sender_name.data
        shipment.sender_phone = form.sender_phone.data
        shipment.sender_address = form.sender_address.data
        shipment.recipient_name = form.recipient_name.data
        shipment.recipient_phone = form.recipient_phone.data
        shipment.recipient_address = form.recipient_address.data
        shipment.destination_city = form.destination_city.data
        shipment.carrier_name = form.carrier_name.data
        shipment.carrier_phone = form.carrier_phone.data
        shipment.package_count = form.package_count.data
        shipment.weight_kg = form.weight_kg.data
        shipment.price = form.price.data
        shipment.notes = form.notes.data
        
        # Mise à jour des associations avec les tiers
        if form.sender_id.data:
            shipment.sender_id = form.sender_id.data
        else:
            shipment.sender_id = None
            
        if form.recipient_id.data:
            shipment.recipient_id = form.recipient_id.data
        else:
            shipment.recipient_id = None
            
        if form.carrier_id.data:
            shipment.carrier_id = form.carrier_id.data
        else:
            shipment.carrier_id = None
        
        # Vérifier si on doit créer de nouveaux tiers
        if not form.sender_id.data and form.sender_name.data:
            # Vérifier si ce client existe déjà
            existing_client = Client.query.filter_by(name=form.sender_name.data, 
                                                  phone=form.sender_phone.data).first()
            if existing_client:
                shipment.sender_id = existing_client.id
            else:
                # Créer un nouveau client expéditeur
                new_sender = Client(
                    name=form.sender_name.data,
                    phone=form.sender_phone.data,
                    address=form.sender_address.data,
                    is_sender=True,
                    is_recipient=False
                )
                db.session.add(new_sender)
                db.session.flush()  # Pour obtenir l'ID
                shipment.sender_id = new_sender.id
                
        if not form.recipient_id.data and form.recipient_name.data:
            # Vérifier si ce client existe déjà
            existing_client = Client.query.filter_by(name=form.recipient_name.data, 
                                                  phone=form.recipient_phone.data).first()
            if existing_client:
                shipment.recipient_id = existing_client.id
            else:
                # Créer un nouveau client destinataire
                new_recipient = Client(
                    name=form.recipient_name.data,
                    phone=form.recipient_phone.data,
                    address=form.recipient_address.data,
                    city=form.destination_city.data,
                    is_sender=False,
                    is_recipient=True
                )
                db.session.add(new_recipient)
                db.session.flush()  # Pour obtenir l'ID
                shipment.recipient_id = new_recipient.id
                
        if not form.carrier_id.data and form.carrier_name.data:
            # Vérifier si ce transporteur existe déjà
            existing_carrier = Carrier.query.filter_by(name=form.carrier_name.data, 
                                                    phone=form.carrier_phone.data).first()
            if existing_carrier:
                shipment.carrier_id = existing_carrier.id
            else:
                # Créer un nouveau transporteur
                new_carrier = Carrier(
                    name=form.carrier_name.data,
                    phone=form.carrier_phone.data
                )
                db.session.add(new_carrier)
                db.session.flush()  # Pour obtenir l'ID
                shipment.carrier_id = new_carrier.id
        
        db.session.commit()
        flash('Envoi mis à jour avec succès!')
        return redirect(url_for('shipments.view_shipment', id=shipment.id))
        
    # Pour l'affichage initial, pré-sélectionner les valeurs dans les listes déroulantes
    if shipment.sender_id:
        form.sender_select.data = str(shipment.sender_id)
    if shipment.recipient_id:
        form.recipient_select.data = str(shipment.recipient_id)
    if shipment.carrier_id:
        form.carrier_select.data = str(shipment.carrier_id)
        
    return render_template('shipments/edit.html', title='Modifier l\'envoi', form=form, shipment=shipment)