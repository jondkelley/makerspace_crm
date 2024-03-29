from flask import Flask, redirect, url_for
from api import api
from blueprint.crm import webapp_crm
import os

from models.crm.makerspace import create_tables as create_tables_makerspace  # Import the create_tables function
from models.crm.cardaccess import create_tables as create_tables_cardaccess  # Import the create_tables function
from models.crm.chore import create_tables as create_tables_chore  # Import the create_tables function

app = Flask(__name__)

app.config['DATABASE_FILE'] = 'crm.sqlite'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key')
# Initialize the API views
api.init_app(app)
app.register_blueprint(webapp_crm, url_prefix='/')

@app.route('/assets/<path:filename>')
def redirect_to_static(filename):
    return redirect(url_for('static', filename='assets/' + filename))


if __name__ == '__main__':
    with app.app_context():
        # Create tables and apply database settings
        create_tables_makerspace()
        create_tables_cardaccess()
        create_tables_chore()

    app.run(debug=True)
