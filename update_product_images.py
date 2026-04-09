from app import app
from models import db, Product, Category

def update_images():
    with app.app_context():
        category_map = {
            'Agricultural Products': '/static/images/agri.png',
            'Handicrafts': '/static/images/handicrafts.png',
            'Masalas and Spices': '/static/images/spices.png',
            'Jaggery': '/static/images/jaggery.png'
        }
        
        products = Product.query.all()
        for p in products:
            if p.category.name in category_map:
                p.image_path = category_map[p.category.name]
                print(f"Updated {p.name} image to {p.image_path}")
        
        db.session.commit()
        print("Image paths updated in database.")

if __name__ == '__main__':
    update_images()
