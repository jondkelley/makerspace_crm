from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from flask import Flask, session, request, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models.crm.makerspace import *
from helpers.constants import MUNICIP, US_STATES_LIST, get_michigan_in_first_three
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired # password reset token
from . import webapp_crm, inject_user_roles, requires_admin

from flask import request, jsonify
import requests

@webapp_crm.route("/impersonate/<int:user_id>")
@requires_admin
def impersonate_user(user_id):
    try:
        # Find the PersonCredentials record based on user_id
        credentials = PersonCredentials.get(PersonCredentials.person == str(user_id))
    except DoesNotExist:
        # Handle the case where the user_id doesn't exist in PersonCredentials
        return redirect(url_for("error_page"))  # Redirect to an error page or handle as needed

    # TODO needs to set session based on person id not the 
    # Store the original user's ID in the session
    session["my_id"] = session.get("user_id")

    # Switch the session to the impersonated user
    session["user_id"] = user_id

    # Get the corresponding Person record for the username
    impersonated_person = credentials.person

    return f"Impersonating {impersonated_person.first} {impersonated_person.last}"

@webapp_crm.route("/impersonating_logout")
@requires_admin
def stop_impersonating():
    if "my_id" in session:
        # Revert back to the original user
        session["user_id"] = session["my_id"]
        session.pop("my_id", None)
    
    return redirect(url_for("index"))

@webapp_crm.route('/registexr', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        # Gather data from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        # ... gather other fields ...

        # Prepare data for the API request
        api_data = {
            "first": first_name,
            "last": last_name,
            "email": email,
        }

        # Make a request to the RESTful API endpoint
        response = requests.post('http://localhost:5000/api/person', json=api_data)

        if response.status_code == 201:
            # Handle success
            return 'Registration successful'
        else:
            # Handle errors
            return 'Registration failed', response.status_code

    # For GET request, render the registration form
    return render_template('crm/core/register.html', states=get_michigan_in_first_three(US_STATES_LIST), municipalities=MUNICIP)


@webapp_crm.route('/register', methods=['GET', 'POST'])
def register_model():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            flash('Your passwords do not match')
            return render_template('crm/core/register.html', states=get_michigan_in_first_three(US_STATES_LIST), municipalities=MUNICIP)
        if not len(password) > 5:
            flash('Password must be 5 characters')
            return render_template('crm/core/register.html', states=get_michigan_in_first_three(US_STATES_LIST), municipalities=MUNICIP)
        email = request.form.get('email')
        phone = request.form.get('phone')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        if state.lower() == 'mi' or state.lower() == 'michigan':
            state = 'Michigan'
        if state != 'Michigan':
            flash('Sorry, membership is not available in your area.')
            return render_template('crm/core/register.html', states=get_michigan_in_first_three(US_STATES_LIST), municipalities=MUNICIP)
        zip_code = request.form.get('zip_code')

        # Check if user already exists
        existing_user = PersonCredentials.get_or_none(PersonCredentials.user_id == username)
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('webapp_crm.register'))

        # Create new user
        new_person = Person.create(first=first_name, last=last_name, email=email)
        new_person.save()

        # Hash password and save credentials
        hashed_password = generate_password_hash(password)
        new_credentials = PersonCredentials.create(
            uid=None,
            user_id=username,
            password_hash=hashed_password,
            person=new_person,
            email=email
        )
        new_credentials.save()

        # New code to handle PersonEmergencyContact and PersonContact
        emergency_email = request.form.get('emergency_email')
        emergency_phone = request.form.get('emergency_phone')
        emergency_first_name = request.form.get('emergency_first_name')
        emergency_last_name = request.form.get('emergency_last_name')

        new_emergency_contact = PersonEmergencyContact.create(
            email=emergency_email,
            phone=emergency_phone,
            first=emergency_first_name,
            last=emergency_last_name,
            person=new_person
        )
        new_emergency_contact.save()

        new_person_contact = PersonContact.create(
            phone=phone,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            person=new_person
        )
        new_person_contact.save()

        flash('Registration successful')
        return redirect(url_for('webapp_crm.index'))

    return render_template('crm/core/register.html', states=get_michigan_in_first_three(US_STATES_LIST), municipalities=MUNICIP)

@webapp_crm.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = PersonCredentials.get_or_none(PersonCredentials.email == email)
        if user:
            # Generate a token
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(user.user_id, salt=app.config['SECURITY_PASSWORD_SALT'])

            # Save token to database
            PasswordResetToken.create_token_for_user(user=user, token=token)

            # Send email with SendGrid (not shown here)

        # Redirect or show a message
        flash('If the email is registered, you will receive a password reset link.')

    return render_template('crm/core/reset_password_request.html')

def get_user_id_from_token(token, secret_key, salt, max_age=3600):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        user_id = serializer.loads(token, salt=salt, max_age=max_age)
        return user_id
    except SignatureExpired:
        # Handle the case when the token is valid but expired
        return None
    except BadSignature:
        # Handle the case when the token is invalid
        return None

@webapp_crm.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = get_user_id_from_token(token, app.config['SECRET_KEY'], app.config['SECURITY_PASSWORD_SALT'])

    if user_id is None:
        # Handle invalid or expired token
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('webapp_crm.reset_password_request'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        # Validate and update the password
        PersonCredentials.update_password(user_id=user_id, new_password=new_password)

        # Additional logic (e.g., invalidating the token)

        flash('Your password has been reset successfully.')
        return redirect(url_for('webapp_crm.login'))

    return render_template('crm/core/reset_password.html')

@webapp_crm.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = PersonCredentials.get_or_none(PersonCredentials.user_id == username)
        if user and check_password_hash(user.password_hash, password):
            resp = make_response(redirect(url_for('webapp_crm.index')))
            resp.set_cookie('user_id', username)
            return resp

        flash('Invalid username or password')
        return redirect(url_for('webapp_crm.login'))

    return render_template('crm/core/login.html')

@webapp_crm.route('/logout')
def logout():
    resp = make_response(redirect(url_for('webapp_crm.index')))
    resp.delete_cookie('user_id')  # Delete the user_id cookie
    flash('You have been logged out.')
    return resp

@webapp_crm.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('webapp_crm.login'))

    user = PersonCredentials.get_or_none(PersonCredentials.user_id == user_id)
    if not user:
        return redirect(url_for('webapp_crm.login'))

    # Check if the user is an admin
    roles = [role.role for role in PersonRbac.select().where((PersonRbac.person == user.person) & (PersonRbac.permission == True))]
    is_admin = PersonRbac.get_or_none((PersonRbac.person == user.person) & (PersonRbac.role == 'admin') & (PersonRbac.permission == True))
    
    return render_template('crm/core/index.html', user=user.person)


