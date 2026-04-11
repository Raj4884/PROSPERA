from flask import Flask, session, request
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import Config
from models import db, User, ActivityLog
import requests
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    # Get absolute paths to templates and static files for Vercel environments
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
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
        if request.endpoint == 'init_db':
            return
        if request.endpoint and 'static' not in request.endpoint:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip: ip = ip.split(',')[0]
            
            activity = ActivityLog(
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
                        activity.country = response.get('country')
                        activity.state = response.get('regionName')
                except:
                    pass
            
            try:
                db.session.add(activity)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Log the error but don't crash the user's request
                print(f"Database error in track_activity: {e}")

    @app.route('/init-db')
    def init_db():
        try:
            # Force schema update by dropping and recreating
            db.drop_all()
            db.create_all()
            from setup_db import setup
            setup()
            return "Database Re-Initialized Successfully (Schema Updated)!"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Database Initialization Failed!<br><br>Error: {str(e)}<br><pre>{error_details}</pre>", 500

    return app

def create_failsafe_app(error_msg):
    app = Flask(__name__)
    @app.route('/')
    @app.route('/<path:path>')
    def error_page(path=''):
        return f"""
        <html>
        <head><title>App Startup Failed</title></head>
        <body style="font-family: sans-serif; padding: 40px; line-height: 1.6;">
            <h1 style="color: #d32f2f;">Critical: App Startup Failed</h1>
            <p>The application encountered an error while initializing. This is likely due to a missing environment variable or a database connection issue.</p>
            <h3>Traceback:</h3>
            <pre style="background: #f4f4f4; padding: 20px; border-left: 5px solid #d32f2f; overflow-x: auto;">{error_msg}</pre>
        </body>
        </html>
        """, 500
    return app

try:
    app = create_app()
except Exception as e:
    import traceback
    app = create_failsafe_app(traceback.format_exc())

if __name__ == '__main__':
    app.run(debug=True)
