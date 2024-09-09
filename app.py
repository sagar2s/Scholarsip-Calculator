from flask import Flask, render_template, request, redirect, url_for, session
from google_sheets import append_to_sheet
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'b8e7d4a1235cfabc9e3b24c5f67a8e9c1d2f345e6789a0b1c2345def6789ab0cd'

# Configure session to use filesystem (or you can choose another type)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Initialize session
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Retrieve form data
        session['name'] = request.form.get('name')
        session['phone'] = request.form.get('phone')
        session['email'] = request.form.get('email')

        # Redirect to scholarship_form
        return redirect(url_for('scholarship_form'))
    return render_template('form.html')

@app.route('/scholarship_form', methods=['GET', 'POST'])
@app.route('/scholarship_form', methods=['GET', 'POST'])
def scholarship_form():
    if request.method == 'POST':
        # Retrieve form data
        program = request.form.get('program')
        cmat_score = int(request.form.get('cmat_score'))
        gpa = float(request.form.get('gpa'))

        # Calculate scholarship based on criteria
        scholarship = calculate_scholarship(cmat_score, gpa)

        # Retrieve data from session
        name = session.get('name')
        phone = session.get('phone')
        email = session.get('email')

        # Debug print statements
        print(f"Name: {name}")
        print(f"Phone: {phone}")
        print(f"Email: {email}")

        # Save to Google Sheets
        append_to_sheet(name, email, phone, program, gpa, cmat_score, scholarship)

        return render_template('result.html', name=name, program=program, cmat_score=cmat_score, gpa=gpa, scholarship=scholarship)
    return render_template('form.html')

def calculate_scholarship(cmat_score, gpa):
    # Define scholarship criteria as a list of rules, ordered by priority
    scholarship_rules = [
        {"gpa_min": 3.8, "gpa_max": 4.0, "cmat_min": 0, "cmat_max": 100, "scholarship": 100},  # Highest priority
        {"gpa_min": 3.3, "gpa_max": 3.79, "cmat_min": 0, "cmat_max": 100, "scholarship": 50},   # Second priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 81, "cmat_max": 100, "scholarship": 50},     # Third priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 70, "cmat_max": 80, "scholarship": 30},      # Fourth priority
        {"gpa_min": 0, "gpa_max": 4.0, "cmat_min": 50, "cmat_max": 69, "scholarship": 20},      # Fifth priority
    ]
    print (gpa)
    print(cmat_score)
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
    app.run(debug=False, host='0.0.0.0', port=5000)
