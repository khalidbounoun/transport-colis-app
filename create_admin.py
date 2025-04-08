from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Vérifier si un utilisateur existe déjà
    user_count = User.query.count()
    if user_count == 0:
        # Créer un nouvel utilisateur administrateur
        username = input("Entrez le nom d'utilisateur admin: ")
        email = input("Entrez l'email admin: ")
        password = input("Entrez le mot de passe admin: ")
        
        admin = User(username=username, email=email)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Utilisateur {username} créé avec succès!")
    else:
        print("Des utilisateurs existent déjà dans la base de données.")