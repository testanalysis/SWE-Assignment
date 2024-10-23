import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS administrators")
cursor.execute("DROP TABLE IF EXISTS applicants")
cursor.execute("DROP TABLE IF EXISTS schemes")
cursor.execute("DROP TABLE IF EXISTS applications")
cursor.execute("DROP TABLE IF EXISTS household_members")
cursor.execute("DROP TABLE IF EXISTS criteria")
cursor.execute("DROP TABLE IF EXISTS benefits")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS administrators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS applicants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    sex TEXT NOT NULL,
    date_of_birth DATE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS household_members (
    id INTEGER PRIMARY KEY,
    applicant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    sex TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    relation TEXT NOT NULL,
    FOREIGN KEY (applicant_id) REFERENCES applicants (id)
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id INTEGER NOT NULL,
        scheme_applied TEXT NOT NULL,
        name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        eligible TEXT NOT NULL,
        application_status TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_id INTEGER NOT NULL,
    scheme_name TEXT NOT NULL,
    employment_status TEXT,
    children_required BOOLEAN,
    school_level TEXT,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id)
);
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_id TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    name TEXT NOT NULL,
    amount REAL,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id)
)
''')

data = {
        "schemes": [
            {
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
            },
            {
                "name": "Retrenchment Assistance Scheme (families)",
                "criteria": {
                    "employment_status": "unemployed",
                    "has_children": {
                        "school_level": "primary"
                    }
                },
                "benefits": [
                    {
                        "name": "SkillsFuture Credits",
                        "amount": 500.00
                    },
                    {
                        "name": "CDC Vouchers",
                        "amount": 200.00
                    },
                    {
                        "name": "School Meal Vouchers",
                        "amount": 200.00
                    }
                ]
            }
        ]
    }


def insert_scheme_data(data):
    for scheme in data['schemes']:
        scheme_name = scheme['name']

        cursor.execute('''
            INSERT INTO schemes (name)
            VALUES (?)
        ''', (scheme_name,))
        
        scheme_id = cursor.lastrowid

        criteria = scheme.get('criteria', {})
        employment_status = criteria.get('employment_status')
        children_required = 'has_children' in criteria
        school_level = criteria.get('has_children', {}).get('school_level', None)

        cursor.execute('''
            INSERT INTO criteria (scheme_id, scheme_name, employment_status, children_required, school_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (scheme_id, scheme_name, employment_status, children_required, school_level))

        benefits = scheme.get('benefits', [])
        for benefit in benefits:
            benefit_name = benefit['name']
            benefit_amount = benefit['amount']

            cursor.execute('''
                INSERT INTO benefits (scheme_id, scheme_name, name, amount)
                VALUES (?, ?, ?, ?)
            ''', (scheme_id, scheme_name, benefit_name, benefit_amount))

insert_scheme_data(data)

connection.commit()
connection.close()
