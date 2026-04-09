from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Product, Category, Inquiry, ActivityLog, ProductClick, User
from functools import wraps
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_visitors = ActivityLog.query.count()
    total_inquiries = Inquiry.query.count()
    total_products = Product.query.count()
    country_count = db.session.query(func.count(func.distinct(ActivityLog.country))).scalar() or 0
    
    # Engagement Data
    top_products = db.session.query(Product, func.count(ProductClick.id).label('clicks'))\
        .outerjoin(ProductClick, Product.id == ProductClick.product_id)\
        .group_by(Product.id)\
        .order_by(desc('clicks'))\
        .limit(5).all()
        
    visitor_countries = db.session.query(ActivityLog.country, func.count(ActivityLog.id))\
        .group_by(ActivityLog.country)\
        .order_by(desc(func.count(ActivityLog.id)))\
        .limit(5).all()
        
    # Time-series Analytics (Last 7 Days)
    from datetime import timedelta, date
    today = date.today()
    labels = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    visits_data = []
    inquiries_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        v_count = ActivityLog.query.filter(func.date(ActivityLog.timestamp) == day).count()
        i_count = Inquiry.query.filter(func.date(Inquiry.created_at) == day).count()
        visits_data.append(v_count)
        inquiries_data.append(i_count)

    # Recent Inquiries
    recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
        
    return render_template('admin/dashboard.html', 
                           total_visitors=total_visitors,
                           total_inquiries=total_inquiries,
                           total_products=total_products,
                           country_count=country_count,
                           top_products=top_products,
                           visitor_countries=dict(visitor_countries),
                           recent_inquiries=recent_inquiries,
                           chart_labels=labels,
                           visits_data=visits_data,
                           inquiries_data=inquiries_data)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            cat = Category(name=name)
            db.session.add(cat)
            db.session.commit()
            flash('Category added')
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_products():
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        moq = request.form.get('moq')
        supply_type = request.form.get('supply_type')
        category_id = request.form.get('category_id')
        
        product = Product(name=name, description=desc, moq=moq, supply_type=supply_type, category_id=category_id)
        # Handling image upload would go here
        db.session.add(product)
        db.session.commit()
        flash('Product added')
        
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/inquiries')
@login_required
@admin_required
def view_inquiries():
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template('admin/inquiries.html', inquiries=inquiries)

@admin_bp.route('/activity')
@login_required
@admin_required
def view_activity():
    activities = db.session.query(ActivityLog, User.name)\
        .outerjoin(User, ActivityLog.user_id == User.id)\
        .order_by(ActivityLog.timestamp.desc())\
        .limit(200).all()
    
    product_clicks = db.session.query(ProductClick, User.name, Product.name)\
        .outerjoin(User, ProductClick.user_id == User.id)\
        .join(Product, ProductClick.product_id == Product.id)\
        .order_by(ProductClick.timestamp.desc())\
        .limit(100).all()
        
    return render_template('admin/activity.html', 
                           activities=activities, 
                           product_clicks=product_clicks)

@admin_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.moq = request.form.get('moq')
        product.supply_type = request.form.get('supply_type')
        product.category_id = request.form.get('category_id')
        
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('public.product_detail', product_id=product.id))
        
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)
