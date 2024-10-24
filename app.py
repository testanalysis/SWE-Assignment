from flask import Flask, jsonify, request, Response
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from datetime import datetime
import sqlite3, os, json

app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()

DATABASE = '/app/database.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
jwt = JWTManager(app)

allowed_employment_statuses = ['employed', 'unemployed']
allowed_sexes = ['male', 'female']
allowed_marital_status = ['single', 'married', 'widowed', 'divorced']

scheme_example = {
            "name": "Retrenchment Assistance Scheme",
            "criteria": {
                "employment_status": "unemployed"
            },
            "benefits": [
                {
                    "name": "SkillsFuture Credits",
                    "amount": 500.00
                },
                {
                    "name": "CDC Vouchers",
                    "amount": 200.00
                }
            ]
        }

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def require_json():
    # List the routes where you expect a JSON body
    json_routes = ['/register', '/login', '/applicants', '/add_scheme', '/applications']
    
    # Only apply the check to routes that expect JSON data
    if request.path in json_routes and request.method in ['POST', 'PUT', 'PATCH']:  # Apply to write methods
        if not request.is_json:
            return jsonify({'error': 'Unsupported Media Type. Content-Type should be application/json.'}), 415

@app.route('/')
def home():
    return "Welcome to Flask with SQLite!"

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Here is your data!'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
 
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO administrators (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'User already exists'}), 409

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    conn = get_db_connection()

    cursor = conn.execute('SELECT * FROM administrators WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({'message': 'User not found. Please register.'}), 404

    if bcrypt.check_password_hash(user['password'], password):
        access_token = create_access_token(identity={'username': username, 'role': 'admin'})

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    else:
        return jsonify({'message': 'Invalid password'}), 401

@app.route('/api/administrators', methods=['GET'])
@jwt_required()
def get_administrators():
    conn = get_db_connection()
    administrators = conn.execute('SELECT * FROM administrators').fetchall() 
    conn.close()
    if not administrators:
        return jsonify({"message": "No administrators found."}), 404
    return jsonify([dict(row) for row in administrators]) 

@app.route('/api/administrators/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_administrator(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM administrators WHERE id = ?', (id,))
    conn.commit()  

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'Administrator not found.'}), 404

    conn.close()
    return jsonify({'message': 'Administrator deleted successfully.'}), 200

@app.route('/api/applicants', methods=['GET'])
@jwt_required()
def get_applicants():
    conn = get_db_connection()
    applicants = conn.execute('SELECT * FROM applicants').fetchall() 
    conn.close()
    if not applicants:
        return jsonify({"message": "No applicants found."}), 404

    return jsonify([dict(row) for row in applicants]), 200

def validate_household_member(member):
    if not member.get('name'):
        return 'Household member must have a name.'
    
    if not member.get('employment_status') or member['employment_status'] not in allowed_employment_statuses:
        return f'Invalid employment status for household member {member.get("name")}.'

    if not member.get('sex') or member['sex'] not in allowed_sexes:
        return f'Invalid sex for household member {member.get("name")}.'
    
    if not member.get('date_of_birth'):
        return f'Household member {member.get("name")} must have a date of birth.'
    
    if not member.get('relation'):
        return f'Household member {member.get("name")} must have a relation to the applicant.'
    
    return None 

def insert_applicant_and_household(applicant_data):
    conn = get_db_connection()

    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO applicants (name, marital_status, employment_status, sex, date_of_birth)
        VALUES (?, ?, ?, ?, ?)
    ''', (applicant_data['name'], applicant_data['marital_status'], applicant_data['employment_status'], applicant_data['sex'], applicant_data['date_of_birth']))
    
    applicant_id = cursor.lastrowid

    household = applicant_data.get('household', [])
    
    if isinstance(household, list):
        for member in household:
            error = validate_household_member(member)
            if error:
                return {'Error': error}, 400  
            conn.execute('''
                INSERT INTO household_members (applicant_id, name, employment_status, sex, date_of_birth, relation)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (applicant_id, member['name'], member['employment_status'], member['sex'], member['date_of_birth'], member['relation']))
    else:
        return {'Error': 'Household must be a list'}, 400

    conn.commit()

    return {'message': 'Applicant and household members inserted successfully'}, 200


@app.route('/api/applicants', methods=['POST'])
@jwt_required()
def add_applicant():
    data = request.get_json()

    example_json_to_follow = {
        "name": "Mary",
        "employment_status": "unemployed",
        "sex": "female",
        "date_of_birth": "1984-10-06",
        "marital_status" : "married",
         "household": [
            {
            "name": "Gwen",
            "employment_status": "unemployed",
            "sex": "female",
            "date_of_birth": "2016-02-01",
            "relation": "daughter"
            },
            {
            "name": "Jayden",
            "employment_status": "unemployed",
            "sex": "male",
            "date_of_birth": "2018-03-15",
            "relation": "son"
            }
        ]
    }

    # Validate the main applicant's fields
    if not data.get('name'):
        return jsonify({
            'Error': 'Name is required.',
            'Example JSON Format': example_json_to_follow
        }), 400

    if not data.get('employment_status') or data['employment_status'] not in allowed_employment_statuses:
        return jsonify({
            'Error': 'Invalid employment status',
            'Example JSON Format': example_json_to_follow
        }), 400

    if not data.get('sex') or data['sex'] not in allowed_sexes:
        return jsonify({
            'Error': 'Invalid sex',
            'Example JSON Format': example_json_to_follow
        }), 400

    if not data.get('date_of_birth'):
        return jsonify({
            'Error': 'Date of birth is required',
            'Example JSON Format': example_json_to_follow
        }), 400

    if not data.get('marital_status') or data['marital_status'] not in allowed_marital_status:
        return jsonify({
            'Error': 'Invalid employment status',
            'Example JSON Format': example_json_to_follow
        }), 400

    response, status = insert_applicant_and_household(data)
    return jsonify(response), status

@app.route('/api/schemes', methods=['GET'])
@jwt_required()
def get_schemes():
    current_user = get_jwt_identity()  # Get the user info from the JWT token
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Unauthorized access, admin only"}), 403
    
    conn = get_db_connection()
    schemes = conn.execute('SELECT * FROM schemes').fetchall()  
    conn.close()

    if not schemes:
        return jsonify({"message": "No schemes found."}), 404

    return jsonify([dict(row) for row in schemes]), 200

def validate_scheme_input(data):
    if 'name' not in data or not data['name']:
        return jsonify({
            'Error': "'name' is required for the scheme.",
            'Example JSON Format': scheme_example
        }), 400

    if 'criteria' not in data or not isinstance(data['criteria'], dict):
        return jsonify({
            'Error': "'criteria' is required and must be an object.",
            'Example JSON Format': scheme_example
        }), 400

    if 'employment_status' not in data['criteria']:
        return jsonify({
            'Error': "'employment_status' is required in the criteria.",
            'Example JSON Format': scheme_example
        }), 400

    if 'has_children' in data['criteria']:
        children_criteria = data['criteria']['has_children']
        if 'school_level' not in children_criteria:
            return jsonify({
                'Error': "'school_level' is required when 'has_children' is specified.",
                'Example JSON Format': scheme_example
            }), 400

    if 'benefits' not in data or not isinstance(data['benefits'], list):
        return jsonify({
            'Error': "'benefits' is required and must be a list.",
            'Example JSON Format': scheme_example
        }), 400

    for benefit in data['benefits']:
        if 'name' not in benefit or not benefit['name']:
            return jsonify({
                'Error': "Each benefit must have a 'name'.",
                'Example JSON Format': scheme_example
            }), 400

        if 'amount' not in benefit or not isinstance(benefit['amount'], (int, float)):
            return jsonify({
                'Error': "Each benefit must have a valid 'amount'.",
                'Example JSON Format': scheme_example
            }), 400

    return None  

def insert_scheme_data(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        scheme_name = data['name']

        cursor.execute('''
            INSERT INTO schemes (name)
            VALUES (?)
        ''', (scheme_name,))
        
        scheme_id = cursor.lastrowid

        criteria = data.get('criteria', {})
        employment_status = criteria.get('employment_status')
        children_required = 'has_children' in criteria
        school_level = criteria.get('has_children', {}).get('school_level', None)

        cursor.execute('''
            INSERT INTO criteria (scheme_id, scheme_name, employment_status, children_required, school_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (scheme_id, scheme_name, employment_status, children_required, school_level))

        benefits = data.get('benefits', [])
        for benefit in benefits:
            benefit_name = benefit['name']
            benefit_amount = benefit['amount']

            cursor.execute('''
                INSERT INTO benefits (scheme_id, scheme_name, name, amount)
                VALUES (?, ?, ?, ?)
            ''', (scheme_id, scheme_name, benefit_name, benefit_amount))

        conn.commit()
        return {"message": "Scheme added successfully."}, 200

    except Exception as e:
        conn.rollback()
        return {"Error": f"An error occurred: {e}"}, 500

    finally:
        conn.close()


@app.route('/api/add_scheme', methods=['POST'])
@jwt_required()
def add_schemes():
    data = request.get_json()
    validation_error = validate_scheme_input(data)

    if validation_error:
        return validation_error
    result, status_code = insert_scheme_data(data)
    return jsonify(result), status_code

@app.route('/api/delete_scheme/<int:scheme_id>', methods=['DELETE'])
@jwt_required()
def delete_scheme(scheme_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM benefits WHERE scheme_id = ?', (scheme_id,))
    
    cursor.execute('DELETE FROM criteria WHERE scheme_id = ?', (scheme_id,))
    
    cursor.execute('DELETE FROM schemes WHERE id = ?', (scheme_id,))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Scheme not found."}), 404

    return jsonify({"message": "Scheme and related data deleted successfully."}), 200

@app.route('/api/scheme_benefits', methods=['GET'])
@jwt_required()
def get_schemes_benefit():
    conn = get_db_connection()
    benefits = conn.execute('SELECT * FROM benefits').fetchall()  
    conn.close()
    return jsonify([dict(row) for row in benefits]) 

@app.route('/api/scheme_criteria', methods=['GET'])
@jwt_required()
def get_schemes_criteria():
    conn = get_db_connection()
    criteria = conn.execute('SELECT * FROM criteria').fetchall()  
    conn.close()
    return jsonify([dict(row) for row in criteria])  


def get_eligible_schemes(scheme_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            schemes.name AS scheme_name,
            benefits.name AS benefit_name,
            benefits.amount AS benefit_amount
        FROM schemes
        JOIN criteria ON schemes.id = criteria.scheme_id
        JOIN benefits ON schemes.id = benefits.scheme_id
        WHERE schemes.id = ?
    ''', (scheme_id,))

    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return []

    schemes_dict = {}

    for row in rows:
        scheme_name = row['scheme_name']
        benefit = f"{row['benefit_name']} (${row['benefit_amount']})"

        if scheme_name not in schemes_dict:
            schemes_dict[scheme_name] = {
                "scheme_name": scheme_name,
                "description": "Financial assistance for retrenched workers",
                "benefits": []
            }
        
        schemes_dict[scheme_name]["benefits"].append(benefit)

    eligible_schemes = list(schemes_dict.values())

    return eligible_schemes


def which_scheme(applicant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM household_members 
        WHERE applicant_id = ? AND (relation = "son" OR relation = "daughter")
    ''', (applicant_id,))

    current_year = datetime.now().year

    cursor.execute('''
        SELECT * FROM household_members 
        WHERE applicant_id = ? 
        AND (relation = "son" OR relation = "daughter")
        AND (? - strftime('%Y', date_of_birth)) BETWEEN 7 AND 12
    ''', (applicant_id, current_year))

    household = cursor.fetchall()

    if not household:
        eligible_schemes = get_eligible_schemes(1)
    else:
        eligible_schemes = get_eligible_schemes(2)

    conn.close()
    return {
        'applicant_id': applicant_id,
        'eligible_schemes': eligible_schemes
    }, 200

def eligibility(applicant_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM applicants WHERE id = ?', (applicant_id,))
    applicant = cursor.fetchone()

    if not applicant:
        return {'error': 'Applicant not found', 'result': False}, 404

    if applicant['employment_status'] != 'unemployed':
        return {'error': 'Applicant is not unemployed and is not eligible for schemes.', 'result': False}, 400

    return {'result': True}, 200

@app.route('/api/schemes/eligible', methods=['GET'])
@jwt_required()
def get_specific_scheme():
    current_user = get_jwt_identity()  # Get the user info from the JWT token
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Unauthorized access, admin only"}), 403

    applicant_id = request.args.get('applicant')

    if not applicant_id:
        return jsonify({'error': 'Applicant ID is required'}), 400

    result, status_code = eligibility(applicant_id)
    if result['result']:
        return which_scheme(applicant_id)
    else:
        return jsonify(result), status_code


@app.route('/api/applications', methods=['GET'])
@jwt_required()
def get_applications():
    conn = get_db_connection()
    applications = conn.execute('SELECT * FROM applications').fetchall()  
    conn.close()
    if not applications:
        return jsonify({"message": "No applications found."}), 404

    return jsonify([dict(row) for row in applications]) 

def insert_application(application_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM applicants WHERE name = ? AND date_of_birth = ?
    ''', (application_data['name'], application_data['date_of_birth']))
    
    applicant = cursor.fetchone()

    if applicant is None:
        return {'Error': 'No matching applicant found. Please register the applicant first with /applicants.'}, 400

    applicant_id = applicant[0]

    result, status_code = eligibility(applicant_id)
    if result['result']:
        eligible_yes_no = 'yes'
        application_status = 'approved'
    else:
        eligible_yes_no = 'no' 
        application_status = 'denied'

    cursor.execute('''
        INSERT INTO applications (applicant_id, scheme_applied, name, date_of_birth, eligible, application_status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        applicant_id,
        application_data['scheme_applied'],
        application_data['name'],
        application_data['date_of_birth'],
        eligible_yes_no,
        application_status
    ))

    conn.commit()
    conn.close()

    return {'message': 'Application inserted successfully'}, 200

@app.route('/api/applications', methods=['POST'])
@jwt_required()
def add_applications():
    current_user = get_jwt_identity()  # Get the user info from the JWT token
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Unauthorized access, admin only"}), 403

    conn = get_db_connection()

    data = request.json

    allowed_schemes = ["Retrenchment Assistance Scheme", "Retrenchment Assistance Scheme (families)"]

    example_json = {
        "name": "jason",
        "date_of_birth": "1990-01-01",
        "scheme_applied": "Retrenchment Assistance Scheme"
    }

    if not data.get('name'):
        return jsonify({
            'Error': 'Name is required.',
            'Example JSON Format': example_json
        }), 400
        

    if not data.get('date_of_birth'):
        return jsonify({
            'Error': 'Date of birth is required.',
            'Example JSON Format': example_json
        }), 400

    if not data.get('scheme_applied') or data.get('scheme_applied') not in allowed_schemes:
        return jsonify({
            'Error': f'Scheme applied must be one of {allowed_schemes}',
            'Example JSON Format': example_json
        }), 400

    return insert_application(data)

@app.route('/api/household', methods=['GET'])
@jwt_required()
def get_household():
    conn = get_db_connection()
    household_members = conn.execute('SELECT * FROM household_members').fetchall()
    conn.close()
    return jsonify([dict(row) for row in household_members])  

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'message': 'Please check your API request',
        'available_endpoints': [
        '/administrators',
        '/applicants',
        '/household',
        '/schemes',
        '/applications',
        '/scheme_benefits',
        '/scheme_criteria',
        '/schemes/eligible?applicant=id',
        '/delete_scheme/id',
        '/add_scheme',
        '/login',
        '/register']
    }), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)