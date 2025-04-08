from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.carriers import bp
from app.carriers.forms import CarrierForm, CarrierSearchForm
from app.models import Carrier, Shipment
from sqlalchemy import or_

@bp.route('/', methods=['GET'])
@login_required
def list_carriers():
    search_form = CarrierSearchForm()
    page = request.args.get('page', 1, type=int)
    
    query = Carrier.query
    
    search_term = request.args.get('search_term', '')
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(or_(
            Carrier.name.like(search_term),
            Carrier.phone.like(search_term),
            Carrier.email.like(search_term)
        ))
    
    carriers = query.order_by(Carrier.name).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('carriers/list.html', title='Liste des Transporteurs', 
                          carriers=carriers, search_form=search_form, search_term=search_term)

@bp.route('/<int:id>/json', methods=['GET'])
@login_required
def get_carrier_json(id):
    carrier = Carrier.query.get_or_404(id)
    return jsonify({
        'id': carrier.id,
        'name': carrier.name,
        'phone': carrier.phone or ''
    })

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_carrier():
    form = CarrierForm()
    if form.validate_on_submit():
        carrier = Carrier(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            notes=form.notes.data
        )
        db.session.add(carrier)
        db.session.commit()
        flash('Nouveau transporteur ajouté avec succès!')
        return redirect(url_for('carriers.list_carriers'))
    return render_template('carriers/add.html', title='Ajouter un transporteur', form=form)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def view_carrier(id):
    carrier = Carrier.query.get_or_404(id)
    return render_template('carriers/view.html', title='Détails du transporteur', carrier=carrier, Shipment=Shipment)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_carrier(id):
    carrier = Carrier.query.get_or_404(id)
    form = CarrierForm(obj=carrier)
    if form.validate_on_submit():
        carrier.name = form.name.data
        carrier.phone = form.phone.data
        carrier.email = form.email.data
        carrier.notes = form.notes.data
        
        db.session.commit()
        flash('Transporteur mis à jour avec succès!')
        return redirect(url_for('carriers.view_carrier', id=carrier.id))
    return render_template('carriers/edit.html', title='Modifier le transporteur', form=form, carrier=carrier)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_carrier(id):
    carrier = Carrier.query.get_or_404(id)
    db.session.delete(carrier)
    db.session.commit()
    flash('Transporteur supprimé avec succès!')
    return redirect(url_for('carriers.list_carriers'))

@bp.route('/search-json', methods=['GET'])
@login_required
def search_json():
    search_term = request.args.get('term', '')
    
    query = Carrier.query
    
    if search_term:
        search_term = f"%{search_term}%"
        query = query.filter(Carrier.name.like(search_term))
    
    carriers = query.limit(10).all()
    
    # Débogage
    print(f"Carrier search term: {search_term}, found: {len(carriers)}")
    
    result = []
    for carrier in carriers:
        result.append({
            'id': carrier.id,
            'name': carrier.name,
            'phone': carrier.phone or '',
            'value': carrier.name,  # Nécessaire pour jQuery UI autocomplete
            'label': f"{carrier.name} - {carrier.phone or 'pas de tél.'}"
        })
    
    return jsonify(result)