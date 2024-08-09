import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import mimetypes
import hashlib
import re
import binascii
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if app.config['SECRET_KEY'] is None:
    raise ValueError("SECRET_KEY is not set in the environment variables")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secure_uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Ensure secure_uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

# Use environment variable for encryption key
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if ENCRYPTION_KEY is None:
    raise ValueError("ENCRYPTION_KEY is not set in the environment variables")
fernet = Fernet(ENCRYPTION_KEY.encode())

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    files = db.relationship('File', backref='owner', lazy='dynamic')

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_check(file):
    if not file.filename:
        return False, "No filename provided"

    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename"

    if not allowed_file(filename):
        return False, "File type not allowed"

    file_content = file.read()
    file.seek(0)  # Reset file pointer to the beginning

    # Use mimetypes for file type checking
    file_mime, _ = mimetypes.guess_type(filename)
    if not file_mime or file_mime.split('/')[0] not in ['text', 'image', 'application']:
        return False, "Invalid file type detected"

    if len(file_content) > app.config['MAX_CONTENT_LENGTH']:
        return False, "File too large"

    file_hash = hashlib.sha256(file_content).hexdigest()

    return True, file_hash

def is_password_strong(password):
    strength = 0
    if len(password) >= 14:
        strength += 1
    if re.search(r"[A-Z]", password):
        strength += 1
    if re.search(r"[a-z]", password):
        strength += 1
    if re.search(r"\d", password):
        strength += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        strength += 1
    if re.search(r"\s", password):
        strength += 1
    
    if strength < 5:
        return False, "Password is not strong enough. It must be at least 14 characters long and include uppercase and lowercase letters, numbers, special characters, and a space."
    return True, "Password meets all requirements."

def hash_password(password):
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    salt = binascii.unhexlify(stored_password[:64])
    stored_pwdhash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return stored_pwdhash == binascii.hexlify(pwdhash).decode('ascii')

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and verify_password(user.password, request.form['password']):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password or not confirm_password:
            flash('All fields are required')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash(message)
            return redirect(url_for('register'))
        
        hashed_password = hash_password(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user_files = current_user.files.all()
        return render_template('dashboard.html', files=user_files)
    except Exception as e:
        app.logger.error(f"Error in dashboard route: {str(e)}")
        app.logger.exception("Full traceback:")
        return "An error occurred while loading the dashboard. Please check the server logs.", 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Generate a unique filename to avoid overwriting
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            filename = f"{base}_{counter}{extension}"
            counter += 1
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Read file content
            file_content = file.read()
            
            # Encrypt file content
            encrypted_content = fernet.encrypt(file_content)
            
            # Test decryption
            try:
                decrypted_content = fernet.decrypt(encrypted_content)
                app.logger.info("Test decryption successful")
            except Exception as e:
                app.logger.error(f"Test decryption failed: {str(e)}")
            
            # Save encrypted content
            with open(file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_content)
            
            # Verify the file was actually saved
            if not os.path.exists(file_path):
                raise IOError("File was not saved successfully")
            
            # Debug information
            app.logger.info(f"File uploaded and encrypted: {filename}")
            app.logger.info(f"Full file path: {file_path}")
            app.logger.info(f"File size: {os.path.getsize(file_path)} bytes")
            
            new_file = File(filename=filename, path=file_path, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            
            flash('File uploaded and encrypted successfully')
        except Exception as e:
            app.logger.error(f"Error during file upload and encryption: {str(e)}")
            flash(f'An error occurred while uploading and encrypting the file: {str(e)}')
        
        return redirect(url_for('dashboard'))
    else:
        flash('File type not allowed')
        return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('Unauthorized access to file')
        return redirect(url_for('dashboard'))
    
    file_path = file.path
    
    # Debug information
    app.logger.info(f"Attempting to download file: {file.filename}")
    app.logger.info(f"Full file path: {file_path}")
    app.logger.info(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        flash(f'File not found: {file.filename}')
        return redirect(url_for('dashboard'))
    
    try:
        # Read encrypted content
        with open(file_path, 'rb') as encrypted_file:
            encrypted_content = encrypted_file.read()
        
        # Decrypt content
        decrypted_content = fernet.decrypt(encrypted_content)
        
        # Create a temporary file with decrypted content
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + file.filename)
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(decrypted_content)
        
        return send_file(temp_path, as_attachment=True, download_name=file.filename)
    except Exception as e:
        app.logger.error(f'Error downloading and decrypting file: {str(e)}')
        app.logger.error(f'File ID: {file_id}, Filename: {file.filename}, Path: {file_path}')
        app.logger.exception("Full traceback:")
        flash(f'An error occurred while downloading and decrypting the file: {str(e)}')
        return redirect(url_for('dashboard'))
    finally:
        # Remove the temporary decrypted file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        abort(403)  # Return a 403 Forbidden error if the user doesn't own the file
    
    try:
        if os.path.exists(file.path):
            os.remove(file.path)
        db.session.delete(file)
        db.session.commit()
        flash('File deleted successfully')
    except Exception as e:
        app.logger.error(f"Error deleting file: {str(e)}")
        flash(f'An error occurred while deleting the file: {str(e)}')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)