from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from models import db, Product, Category, Inquiry, ProductClick

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/choice')
@login_required
def choice():
    return render_template('public/choice.html')

@public_bp.route('/catalog/<supply_type>')
@login_required
def catalog(supply_type):
    if supply_type not in ['Domestic', 'International']:
        return redirect(url_for('public.choice'))
    
    category_id = request.args.get('category', type=int)
    categories = Category.query.all()
    
    query = Product.query.filter_by(supply_type=supply_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.all()
    return render_template('public/catalog.html', products=products, categories=categories, supply_type=supply_type)

@public_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Track click
    click = ProductClick(product_id=product.id, user_id=current_user.id)
    db.session.add(click)
    db.session.commit()
    
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        message = request.form.get('message')
        
        inquiry = Inquiry(
            user_id=current_user.id,
            company_name=current_user.company_name,
            contact_person=current_user.name,
            email=current_user.email,
            country=current_user.country,
            state=current_user.state,
            product_name=product.name,
            quantity=quantity,
            message=message
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Inquiry submitted successfully! We will contact you soon.')
        return redirect(url_for('public.product_detail', product_id=product_id))
        
    return render_template('public/product_detail.html', product=product)

@public_bp.route('/logistics')
def logistics():
    return render_template('public/logistics.html')

@public_bp.route('/company')
def company():
    return render_template('public/company.html')

@public_bp.route('/my-inquiries')
@login_required
def my_inquiries():
    inquiries = Inquiry.query.filter_by(user_id=current_user.id).order_by(Inquiry.created_at.desc()).all()
    return render_template('public/my_inquiries.html', inquiries=inquiries)
