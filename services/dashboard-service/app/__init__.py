from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temporary_secret_key_for_ui_testing'

    # Mock user data so that base.html renders correctly without crashing
    mock_client = {
        'firstname': 'Ahmed',
        'lastname': 'Ben Ali',
        'entreprise': 'Tech Corp',
        'email': 'ahmed@techcorp.com',
        'sector': 'Électronique',
        'phone_number': '+216 22 333 444',
        'factories': []
    }

    @app.route('/')
    @app.route('/login')
    def login():
        return render_template('login.html', error=None)

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html', client=mock_client, page='dashboard')

    @app.route('/analysis')
    def analysis():
        return render_template('analysis.html', client=mock_client, page='analysis')

    @app.route('/settings')
    def settings():
        return render_template('settings.html', client=mock_client, page='settings')

    @app.route('/profile')
    def profile():
        return render_template('profile.html', client=mock_client, page='profile')
        
    @app.route('/machine/<int:machine_id>')
    def machine(machine_id):
        return render_template('machine.html', client=mock_client, page='dashboard', machine_id=machine_id)

    return app
