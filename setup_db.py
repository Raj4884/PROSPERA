from app import app
from models import db, User, Category, Product

def setup():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add Admin User if not exists
        if not User.query.filter_by(email='admin@prosperaexim.in').first():
            admin = User(
                name='Admin Prospera',
                email='admin@prosperaexim.in',
                company_name='Prospera Exim Group',
                country='India',
                state='Maharashtra',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Admin user created: admin@prosperaexim.in / admin123")
        
        # Add Default Categories
        category_map = {
            'Agricultural Products': '/static/images/agri.png',
            'Handicrafts': '/static/images/handicrafts.png',
            'Masalas and Spices': '/static/images/spices.png',
            'Jaggery': '/static/images/jaggery.png'
        }
        
        for cat_name in category_map:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.session.add(cat)
        
        db.session.commit()

        # Seed initial products for beginners to see quality examples
        if Product.query.count() == 0:
            agri_cat = Category.query.filter_by(name='Agricultural Products').first()
            hand_cat = Category.query.filter_by(name='Handicrafts').first()
            spice_cat = Category.query.filter_by(name='Masalas and Spices').first()
            jag_cat = Category.query.filter_by(name='Jaggery').first()

            products = [
                Product(name='Premium Basmati Rice', description='Long-grain aged Basmati rice with superior aroma. Suitable for high-end retail and catering.', moq='5000 KG', supply_type='International', category_id=agri_cat.id, image_path='/static/images/agri.png'),
                Product(name='Organic Turmeric Powder', description='High-curcumin turmeric powder, cold-ground to preserve essential oils.', moq='500 KG', supply_type='International', category_id=spice_cat.id, image_path='/static/images/spices.png'),
                Product(name='Hand-Carved Brass Vase', description='Traditional Indian brass work by master artisans. Elegant export-quality finish.', moq='50 Units', supply_type='International', category_id=hand_cat.id, image_path='/static/images/handicrafts.png'),
                Product(name='Bio-Refined Jaggery Cubes', description='Chemical-free natural sweetener blocks. High demand in health-food sectors.', moq='1000 KG', supply_type='International', category_id=jag_cat.id, image_path='/static/images/jaggery.png')
            ]
            for p in products:
                db.session.add(p)
            db.session.commit()
            print("Database seeded with sample commodities.")

        print("Database initialization complete.")

if __name__ == '__main__':
    setup()
