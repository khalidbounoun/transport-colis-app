from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.clients import bp
from app.models import Client, Shipment
from app.clients.forms import ClientForm, ClientSearchForm
from sqlalchemy import or_


@bp.route('/', methods=['GET'])
@login_required
def list_clients():
    search_form = ClientSearchForm()
    page = request.args.get('page', 1, type=int)
    
    query = Client.query
    
    search_term = request.args.get('search_term', '')
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(or_(
            Client.name.like(search_term),
            Client.phone.like(search_term),
            Client.email.like(search_term),
            Client.city.like(search_term)
        ))
    
    clients = query.order_by(Client.name).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('clients/list.html', title='Liste des Clients', 
                          clients=clients, search_form=search_form, search_term=search_term)


@bp.route('/<int:id>/json', methods=['GET'])
@login_required
def get_client_json(id):
    client = Client.query.get_or_404(id)
    return jsonify({
        'id': client.id,
        'name': client.name,
        'phone': client.phone or '',
        'address': client.address or '',
        'city': client.city or ''
    })

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            is_sender=form.is_sender.data,
            is_recipient=form.is_recipient.data,
            notes=form.notes.data
        )
        db.session.add(client)
        db.session.commit()
        flash('Nouveau client ajouté avec succès!')
        return redirect(url_for('clients.list_clients'))
    return render_template('clients/add.html', title='Ajouter un client', form=form)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view_client(id):
    client = Client.query.get_or_404(id)
    return render_template('clients/view.html', title='Détails du client', client=client, Shipment=Shipment)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    client = Client.query.get_or_404(id)
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        client.name = form.name.data
        client.phone = form.phone.data
        client.email = form.email.data
        client.address = form.address.data
        client.city = form.city.data
        client.is_sender = form.is_sender.data
        client.is_recipient = form.is_recipient.data
        client.notes = form.notes.data
        
        db.session.commit()
        flash('Client mis à jour avec succès!')
        return redirect(url_for('clients.view_client', id=client.id))
    return render_template('clients/edit.html', title='Modifier le client', form=form, client=client)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('Client supprimé avec succès!')
    return redirect(url_for('clients.list_clients'))

@bp.route('/search-json', methods=['GET'])
@login_required
def search_json():
    search_term = request.args.get('term', '')
    client_type = request.args.get('type', 'all')
    
    # Pour débogage
    print(f"Recherche client: {search_term}, type: {client_type}")
    
    query = Client.query
    
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(Client.name.like(search_term))
    
    if client_type == 'sender':
        query = query.filter(Client.is_sender == True)
    elif client_type == 'recipient':
        query = query.filter(Client.is_recipient == True)
    
    clients = query.limit(10).all()
    
    # Pour débogage
    print(f"Clients trouvés: {len(clients)}")
    
    result = []
    for client in clients:
        client_data = {
            'id': client.id,
            'name': client.name,
            'phone': client.phone or '',
            'address': client.address or '',
            'city': client.city or '',
            'value': client.name,
            'label': f"{client.name} - {client.phone or 'pas de tél.'} ({client.city or 'pas de ville'})"
        }
        result.append(client_data)
        # Pour débogage
        print(f"Client ajouté à la réponse: {client_data}")
    
    return jsonify(result)