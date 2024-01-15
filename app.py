from flask import Flask
from views import api
from views.webapp import webapp_main
import os


from models.makerspace import create_tables as create_tables_makerspace  # Import the create_tables function
from models.cardaccess import create_tables as create_tables_cardaccess  # Import the create_tables function
from models.chore import create_tables as create_tables_chore  # Import the create_tables function

app = Flask(__name__)

app.config['DATABASE_FILE'] = 'crm.sqlite'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key')
# Initialize the API views
api.init_app(app)
app.register_blueprint(webapp_main, url_prefix='/')



if __name__ == '__main__':
    with app.app_context():
        # Create tables and apply database settings
        create_tables_makerspace()
        create_tables_cardaccess()
        create_tables_chore()

    app.run(debug=True)
