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
    
    # Debug: Log template directory for Vercel troubleshooting
    print(f"[STARTUP] Base dir: {base_dir}")
    print(f"[STARTUP] Template dir: {template_dir}")
    print(f"[STARTUP] Template dir exists: {os.path.exists(template_dir)}")
    if os.path.exists(template_dir):
        for root, dirs, files in os.walk(template_dir):
            for f in files:
                print(f"[STARTUP] Template found: {os.path.join(root, f)}")
    else:
        print(f"[STARTUP] WARNING: Template directory does not exist!")
        print(f"[STARTUP] CWD: {os.getcwd()}")
        print(f"[STARTUP] CWD contents: {os.listdir(os.getcwd())}")
        # Try to find templates relative to CWD as fallback
        cwd_template_dir = os.path.join(os.getcwd(), 'templates')
        if os.path.exists(cwd_template_dir):
            print(f"[STARTUP] Found templates at CWD-relative path: {cwd_template_dir}")
            template_dir = cwd_template_dir
            static_dir = os.path.join(os.getcwd(), 'static')
    
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
            
            try:
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Log the error but don't crash the user's request
                print(f"Database error in track_activity: {e}")

    @app.route('/init-db')
    def init_db():
        from setup_db import setup
        setup()
        return "Database Initialized Successfully! You can now go to the home page."

    @app.route('/debug-paths')
    def debug_paths():
        import json
        info = {
            '__file__': __file__,
            'abs_file': os.path.abspath(__file__),
            'dirname': os.path.dirname(os.path.abspath(__file__)),
            'cwd': os.getcwd(),
            'template_folder': app.template_folder,
            'template_folder_exists': os.path.exists(app.template_folder) if app.template_folder else False,
        }
        
        # List /var/task contents
        task_dir = '/var/task'
        if os.path.exists(task_dir):
            info['var_task_contents'] = []
            for root, dirs, files in os.walk(task_dir):
                # Skip _vendor to avoid massive output
                dirs[:] = [d for d in dirs if d != '_vendor' and d != '__pycache__']
                for f in files:
                    info['var_task_contents'].append(os.path.join(root, f))
        
        # List CWD contents
        try:
            info['cwd_contents'] = os.listdir(os.getcwd())
        except:
            info['cwd_contents'] = 'error listing'
            
        return json.dumps(info, indent=2, default=str), 200, {'Content-Type': 'application/json'}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
