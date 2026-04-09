from flask import Flask, session, request
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import Config
from models import db, User, ActivityLog
import requests

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.public_routes import public_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.before_request
    def track_activity():
        if request.endpoint and 'static' not in request.endpoint:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip: ip = ip.split(',')[0]
            
            log = ActivityLog(
                user_id=current_user.id if current_user.is_authenticated else None,
                session_id=session.get('_id'),
                page_visited=request.path,
                ip_address=ip
            )
            
            # Real Geolocation fetching
            if ip and ip != '127.0.0.1':
                try:
                    response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
                    if response.get('status') == 'success':
                        log.country = response.get('country')
                        log.state = response.get('regionName')
                except:
                    pass
            
            db.session.add(log)
            db.session.commit()

    @app.route('/init-db')
    def init_db():
        from setup_db import setup
        setup()
        return "Database Initialized Successfully! You can now go to the home page."

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
