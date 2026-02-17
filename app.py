import sqlite3
import json
import csv
from io import StringIO
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, make_response
from datetime import datetime, timedelta
from functools import wraps
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

app = Flask(__name__)
DATABASE = os.getenv('DATABASE', '/app/data/inventory.db')

# Configuration de la session
app.secret_key = os.getenv('SECRET_KEY', 'votre-clé-secrète-très-sûre-change-en-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des changements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product_type TEXT NOT NULL,
                change_type TEXT NOT NULL,
                designation TEXT NOT NULL,
                analyst TEXT NOT NULL,
                app_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des types de produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des types de changements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ajouter les types par défaut
        default_products = ['Harfanglab', 'Elastic', 'Docker', 'Autre']
        default_change_types = ['IOC', 'Whitelist', 'Règle', 'Autre']
        
        for product in default_products:
            cursor.execute('INSERT OR IGNORE INTO products (name) VALUES (?)', (product,))
        
        for change_type in default_change_types:
            cursor.execute('INSERT OR IGNORE INTO change_types (name) VALUES (?)', (change_type,))
        
        # Ajouter l'utilisateur par défaut depuis les variables d'environnement
        default_user = os.getenv('DEFAULT_USERNAME', 'soc')
        default_password = os.getenv('DEFAULT_PASSWORD', 'Spluk2024!')
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (default_user, generate_password_hash(default_password)))
        
        conn.commit()
        conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Identifiants invalides'), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Changer le mot de passe de l'utilisateur connecté"""
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Les champs sont obligatoires'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
    
    # Récupérer l'utilisateur
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Vérifier le mot de passe actuel
    if not check_password_hash(user['password'], current_password):
        return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
    
    # Mettre à jour le mot de passe
    new_password_hash = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password_hash, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Mot de passe modifié avec succès'})

@app.route('/api/types', methods=['GET'])
@login_required
def get_types():
    """Récupérer les types de produits et changements"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM products ORDER BY name')
    products = [row['name'] for row in cursor.fetchall()]
    
    cursor.execute('SELECT name FROM change_types ORDER BY name')
    change_types = [row['name'] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'products': products,
        'change_types': change_types
    })

@app.route('/api/add-type', methods=['POST'])
@login_required
def add_type():
    """Ajouter un nouveau type de produit ou changement"""
    data = request.json
    type_category = data.get('type')  # 'product' ou 'changement'
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Le nom est obligatoire'}), 400
    
    if type_category not in ['product', 'changement']:
        return jsonify({'error': 'Type invalide'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if type_category == 'product':
            cursor.execute('INSERT INTO products (name) VALUES (?)', (name,))
        else:
            cursor.execute('INSERT INTO change_types (name) VALUES (?)', (name,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Type ajouté avec succès'})
    
    except Exception as e:
        conn.close()
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Ce type existe déjà'}), 400
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-type', methods=['POST'])
@login_required
def delete_type():
    """Supprimer un type de produit ou changement"""
    data = request.json
    type_category = data.get('type')  # 'product' ou 'changement'
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Le nom est obligatoire'}), 400
    
    if type_category not in ['product', 'changement']:
        return jsonify({'error': 'Type invalide'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if type_category == 'product':
            cursor.execute('DELETE FROM products WHERE name = ?', (name,))
        else:
            cursor.execute('DELETE FROM change_types WHERE name = ?', (name,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Type supprimé avec succès'})
    
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/changes', methods=['GET'])
@login_required
def get_changes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Filtres
    product_type = request.args.get('product_type')
    change_type = request.args.get('change_type')
    designation = request.args.get('designation')
    analyst = request.args.get('analyst')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = 'SELECT * FROM changes WHERE 1=1'
    params = []
    
    if product_type:
        query += ' AND product_type = ?'
        params.append(product_type)
    
    if change_type:
        query += ' AND change_type = ?'
        params.append(change_type)
    
    if designation:
        query += ' AND designation LIKE ?'
        params.append(f'%{designation}%')
    
    if analyst:
        query += ' AND analyst LIKE ?'
        params.append(f'%{analyst}%')
    
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)
    
    query += ' ORDER BY date DESC'
    
    cursor.execute(query, params)
    changes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(changes)

@app.route('/api/changes', methods=['POST'])
@login_required
def add_change():
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO changes (date, product_type, change_type, designation, analyst, app_link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('date'),
        data.get('product_type'),
        data.get('change_type'),
        data.get('designation'),
        data.get('analyst'),
        data.get('app_link', '')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid}), 201

@app.route('/api/changes/<int:id>', methods=['DELETE'])
@login_required
def delete_change(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM changes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/product-types', methods=['GET'])
def get_product_types():
    return jsonify(['Harfanglab', 'Elastic', 'Docker', 'Autre'])

@app.route('/api/change-types', methods=['GET'])
def get_change_types():
    return jsonify(['IOC', 'Whitelist', 'Règle', 'Autre'])

@app.route('/api/export-csv', methods=['GET'])
@login_required
def export_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer tous les changements
    cursor.execute('SELECT * FROM changes ORDER BY date DESC')
    changes = cursor.fetchall()
    conn.close()
    
    # Créer un fichier CSV en mémoire
    output = StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['Date', 'Type de produit', 'Type de changement', 'Désignation', 'Analyste', 'Lien application'])
    
    # Données
    for change in changes:
        writer.writerow([
            change['date'],
            change['product_type'],
            change['change_type'],
            change['designation'],
            change['analyst'],
            change['app_link'] if change['app_link'] else ''
        ])
    
    # Préparer la réponse
    output.seek(0)
    csv_content = output.getvalue()
    
    # Créer une réponse avec le contenu CSV
    from flask import make_response
    response = make_response(csv_content)
    response.headers['Content-Disposition'] = f"attachment; filename=inventaire_changements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response

@app.route('/api/import-csv', methods=['POST'])
@login_required
def import_csv():
    """Importer des changements depuis un fichier CSV"""
    
    # Vérifier si un fichier a été envoyé
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Le fichier doit être un CSV'}), 400
    
    try:
        # Lire le fichier CSV
        stream = file.read().decode('utf-8')
        csv_reader = csv.reader(stream.splitlines())
        
        # Récupérer les en-têtes
        headers = next(csv_reader)
        
        # Valider les en-têtes
        required_headers = ['Date', 'Type de produit', 'Type de changement', 'Désignation', 'Analyste']
        for header in required_headers:
            if header not in headers:
                return jsonify({'error': f"En-tête manquant: {header}"}), 400
        
        # Connecter à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        errors = []
        
        # Importer chaque ligne
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Vérifier que la ligne a assez de colonnes
                if len(row) < len(required_headers):
                    errors.append(f"Ligne {row_num}: Nombre de colonnes insuffisant")
                    continue
                
                # Extraire les valeurs
                date = row[headers.index('Date')].strip()
                product_type = row[headers.index('Type de produit')].strip()
                change_type = row[headers.index('Type de changement')].strip()
                designation = row[headers.index('Désignation')].strip()
                analyst = row[headers.index('Analyste')].strip()
                app_link = row[headers.index('Lien application')].strip() if 'Lien application' in headers else ''
                
                # Valider les champs obligatoires
                if not all([date, product_type, change_type, designation, analyst]):
                    errors.append(f"Ligne {row_num}: Champs obligatoires manquants")
                    continue
                
                # Valider la date (format YYYY-MM-DD)
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Ligne {row_num}: Format de date invalide (utilisez YYYY-MM-DD)")
                    continue
                
                # Insérer dans la base de données
                cursor.execute('''
                    INSERT INTO changes (date, product_type, change_type, designation, analyst, app_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (date, product_type, change_type, designation, analyst, app_link if app_link else None))
                
                imported_count += 1
            
            except Exception as e:
                errors.append(f"Ligne {row_num}: Erreur - {str(e)}")
        
        # Valider et sauvegarder
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{imported_count} changement(s) importé(s) avec succès',
            'imported': imported_count,
            'errors': errors if errors else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement du fichier: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
