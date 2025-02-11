from flask import Flask, render_template, request, redirect, url_for, session
from google_sheets import append_to_sheet
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'b8e7d4a1235cfabc9e3b24c5f67a8e9c1d2f345e6789a0b1c2345def6789ab0cd'

# Configure session to use filesystem (or you can choose another type)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Initialize session
Session(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

class FormData(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ScholarshipForm(FlaskForm):
    program = StringField('Program', validators=[DataRequired()])
    cmat_score = IntegerField('CMAT Score', validators=[InputRequired()])
    gpa = FloatField('GPA', validators=[InputRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def index():
    # Clear session data if coming from a fresh start
    if 'name' in session:
        session.pop('name', None)
        session.pop('phone', None)
        session.pop('email', None)
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    # Check if basic info is already filled
    if 'name' in session and 'phone' in session and 'email' in session:
        return redirect(url_for('scholarship_form'))

    form = FormData()
    if form.validate_on_submit():
        # Save form data to session
        session['name'] = form.name.data
        session['phone'] = form.phone.data
        session['email'] = form.email.data

        # Redirect to scholarship_form
        return redirect(url_for('scholarship_form'))
    
    return render_template('form.html', form=form)

@app.route('/scholarship_form', methods=['GET', 'POST'])
def scholarship_form():
    # Ensure basic info is present in the session
    if 'name' not in session or 'phone' not in session or 'email' not in session:
        return redirect(url_for('index'))

    form = ScholarshipForm()
    if form.validate_on_submit():
        # Retrieve form data
        program = form.program.data
        cmat_score = form.cmat_score.data
        gpa = form.gpa.data

        # Calculate scholarship based on criteria
        scholarship = calculate_scholarship(cmat_score, gpa)

        # Retrieve data from session
        name = session.get('name')
        phone = session.get('phone')
        email = session.get('email')

        # Save to Google Sheets
        append_to_sheet(name, email, phone, program, gpa, cmat_score, scholarship)

        return render_template('result.html', name=name, program=program, cmat_score=cmat_score, gpa=gpa, scholarship=scholarship)
    
    return render_template('scholarship_form.html', form=form)

def calculate_scholarship(cmat_score, gpa):
    # Define scholarship criteria as a list of rules, ordered by priority
    scholarship_rules = [
        {"gpa_min": 3.8, "gpa_max": 4.0, "cmat_min": 0, "cmat_max": 100, "scholarship": 100},  # Highest priority
        {"gpa_min": 3.3, "gpa_max": 3.79, "cmat_min": 0, "cmat_max": 100, "scholarship": 50},   # Second priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 81, "cmat_max": 100, "scholarship": 50},     # Third priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 70, "cmat_max": 80, "scholarship": 30},      # Fourth priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 50, "cmat_max": 69, "scholarship": 20},      # Fifth priority
    ]

    # Check each rule in order of priority
    for rule in scholarship_rules:
        if rule["gpa_min"] <= gpa <= rule["gpa_max"] and rule["cmat_min"] <= cmat_score <= rule["cmat_max"]:
            return rule["scholarship"]

    # No rule matched
    return 0

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=False)
