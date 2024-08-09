# Secure File Vault

Secure File Vault is a Flask-based web application designed to provide secure file storage and management. It implements various security measures to protect user data and demonstrate secure-by-design principles.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Security Features](#security-features)
- [Project Intentions and Future Plans](#project-intentions-and-future-plans)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration and authentication
- Secure file upload and storage
- File encryption at rest
- File download functionality
- User-specific file management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/secure-file-vault.git`
cd secure-file-vault
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate`
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Set up the database:
```python
python3
from app import app, db
with app.app_context():
     db.create_all()
exit()
```
5. Run the application:
```bash
python3 secure_file_vault.py
```

## Usage

1. Run the application:
`python3 secure_file_vault.py`
2. Open a web browser and navigate to `http://localhost:5000`
3. Register a new account
4. Log in to your account
5. Use the dashboard to upload, download, and manage your files
6. Log out when finished

## Security Features

The application currently implements the following security measures:

* File encryption at rest
* Strong password requirements, including:
  - Minimum length of 14 characters
  - Mix of uppercase and lowercase letters
  - Inclusion of numbers and special characters
  - Requirement for a space character
* Secure password hashing using PBKDF2 with SHA-256
* SQL Injection protection via SQLAlchemy ORM
* Secure file upload handling:
  - File type restriction
  - Secure filename generation
  - File size limits
* User authentication and access control
* HTTPS enforcement (when properly configured in production)
* Principle of least privilege in user permissions
* Addition of Cross-Site Request Forgery (CSRF) prevention measures

Future security enhancements:
* Implementation of Cross-Site Scripting (XSS) prevention through input sanitization


CSRF Tokens
CSRF (Cross-Site Request Forgery) tokens have been implemented to enhance the security of our application. These tokens help prevent unauthorized actions from being performed on behalf of authenticated users, thereby protecting against CSRF attacks.

Generating Encryption Keys
You need to generate your own encryption keys to ensure the security of your data. Follow the steps below to generate these keys using the provided `key_generator.py` script.

1. Run the key generator script located in `key_generator.py`.

2. Add the generated keys to your `config.env.example` file:
```python
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
```
3. Replace line 17 in `secure_file_vault.py`:
```python
load_dotenv('config.env')
```
with

```python
load_dotenv('config.env.example')
```

## Project Intentions and Future Plans

This application is intended to be the first "secure by design" project for the Claremont Cybersecurity Club. It currently serves as a secure file storage system, with plans to expand its functionality and use it as a base for future cybersecurity education and practice.

### Future Features
We plan to enhance the application with the following features:

* Multi-Factor Authentication (MFA)
* User-to-user file sharing capabilities
* Comprehensive audit logging
* Cloud platform hosting for wider accessibility

### Educational Use
Once these features are implemented, the application will serve as a practical platform for:

1. Hands-on penetration testing exercises
2. Vulnerability assessment and mitigation practice
3. Secure coding workshops and demonstrations

Any vulnerabilities discovered during these educational activities will be addressed, further improving the security of the application.

