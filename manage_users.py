#!/usr/bin/env python3
"""
Script de gestion des utilisateurs - Inventaire des changements SOC
Permet de:
- Lister les utilisateurs
- Ajouter un nouvel utilisateur
- Modifier le mot de passe d'un utilisateur
- Supprimer un utilisateur
"""

import sqlite3
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import os

DATABASE = 'data/inventory.db'


def get_connection():
    """Connecter à la base de données"""
    if not os.path.exists(DATABASE):
        print(f"❌ Erreur: La base de données {DATABASE} n'existe pas!")
        print("Assurez-vous que l'application a déjà créé la base de données.")
        sys.exit(1)
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def list_users():
    """Lister tous les utilisateurs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, username, created_at FROM users')
        users = cursor.fetchall()
        
        if not users:
            print("❌ Aucun utilisateur trouvé!")
            return
        
        print("\n" + "="*60)
        print("📋 LISTE DES UTILISATEURS")
        print("="*60)
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Identifiant: {user['username']}")
            print(f"Créé le: {user['created_at']}")
            print("-" * 60)
        
        print(f"✅ Total: {len(users)} utilisateur(s)\n")
    
    finally:
        conn.close()


def add_user(username, password):
    """Ajouter un nouvel utilisateur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            print(f"❌ Erreur: L'utilisateur '{username}' existe déjà!")
            return False
        
        # Ajouter l'utilisateur
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (username, password_hash))
        
        conn.commit()
        
        print("="*60)
        print("✅ UTILISATEUR CRÉÉ AVEC SUCCÈS")
        print("="*60)
        print(f"Identifiant: {username}")
        print(f"Mot de passe: {'*' * len(password)} (masqué)")
        print("="*60)
        print("\n💡 Tip: Vous pouvez maintenant vous connecter avec ces identifiants!\n")
        
        return True
    
    except sqlite3.IntegrityError:
        print(f"❌ Erreur: L'utilisateur '{username}' existe déjà!")
        return False
    
    finally:
        conn.close()


def change_password(username, new_password):
    """Modifier le mot de passe d'un utilisateur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Erreur: L'utilisateur '{username}' n'existe pas!")
            return False
        
        # Modifier le mot de passe
        password_hash = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE users
            SET password = ?
            WHERE username = ?
        ''', (password_hash, username))
        
        conn.commit()
        
        print("="*60)
        print("✅ MOT DE PASSE MODIFIÉ AVEC SUCCÈS")
        print("="*60)
        print(f"Utilisateur: {username}")
        print(f"Nouveau mot de passe: {'*' * len(new_password)} (masqué)")
        print("="*60)
        print("\n💡 Tip: Vous pouvez maintenant vous connecter avec le nouveau mot de passe!\n")
        
        return True
    
    finally:
        conn.close()


def delete_user(username):
    """Supprimer un utilisateur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'utilisateur existe
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Erreur: L'utilisateur '{username}' n'existe pas!")
            return False
        
        # Confirmation
        confirm = input(f"⚠️  Êtes-vous sûr de vouloir supprimer l'utilisateur '{username}'? (oui/non): ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Suppression annulée.")
            return False
        
        # Supprimer l'utilisateur
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        
        print("="*60)
        print("✅ UTILISATEUR SUPPRIMÉ AVEC SUCCÈS")
        print("="*60)
        print(f"Utilisateur: {username}")
        print("="*60 + "\n")
        
        return True
    
    finally:
        conn.close()


def main():
    """Menu principal"""
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("🔐 GESTION DES UTILISATEURS")
        print("Inventaire des changements SOC")
        print("="*60)
        print("\nUsage:")
        print("  python manage_users.py list                  # Lister les utilisateurs")
        print("  python manage_users.py add <username> <pwd>  # Ajouter un utilisateur")
        print("  python manage_users.py change <username> <pwd> # Modifier mot de passe")
        print("  python manage_users.py delete <username>     # Supprimer un utilisateur")
        print("\nExemples:")
        print("  python manage_users.py list")
        print("  python manage_users.py add jean MaSecurePassword123!")
        print("  python manage_users.py change soc NouveauMotDePasse456!")
        print("  python manage_users.py delete jean")
        print("="*60 + "\n")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_users()
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_users.py add <username> <password>")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        add_user(username, password)
    
    elif command == 'change':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_users.py change <username> <new_password>")
            sys.exit(1)
        username = sys.argv[2]
        new_password = sys.argv[3]
        change_password(username, new_password)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py delete <username>")
            sys.exit(1)
        username = sys.argv[2]
        delete_user(username)
    
    else:
        print(f"❌ Commande inconnue: {command}")
        print("\nCommandes disponibles: list, add, change, delete")
        sys.exit(1)


if __name__ == '__main__':
    main()
