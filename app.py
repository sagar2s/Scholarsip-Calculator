from flask import Flask, render_template, request, redirect, url_for, session
from google_sheets import append_to_sheet
from flask_session import Session  # Add this import

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
def scholarship_form():
    if request.method == 'POST':
        # Retrieve form data
        program = request.form.get('program')
        cmat_score = int(request.form.get('cmat_score'))
        gpa = float(request.form.get('gpa'))

        # Calculate scholarship based on weighted criteria
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
    # Define weightings for CMAT score and GPA
    weight_cmat = 0.5
    weight_gpa = 0.5

    # Define thresholds for scholarship categories
    high_score_threshold = 100
    high_gpa_threshold = 4
    medium_score_threshold = 70
    medium_gpa_threshold = 3.2

    # Calculate weighted scores
    cmat_score_normalized = min(cmat_score / high_score_threshold, 1.0)
    gpa_normalized = min(gpa / high_gpa_threshold, 1.0)

    # Calculate the overall score
    overall_score = (cmat_score_normalized * weight_cmat) + (gpa_normalized * weight_gpa)

    # Determine scholarship eligibility based on overall score
    if overall_score >= 0.9:
        return 'full'
    elif overall_score >= 0.7:
        return 'half'
    else:
        return 'none'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
