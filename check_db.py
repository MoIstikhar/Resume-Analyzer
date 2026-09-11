from app import app, db
from models import User

with app.app_context():
    print("\n==========================================")
    print("DATABASE CONNECTION TARGET:")
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    print("==========================================")
    
    users = User.query.all()
    print(f"TOTAL USERS IN APP: {len(users)}")
    print("------------------------------------------")
    for u in users:
        print(f"ID: {u.id} | Name: {u.name} | Email: {u.email}")
    print("==========================================\n")