from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def main():
    db = SessionLocal()
    u = db.query(User).filter(User.username == 'admin').first()
    if u is None:
        u = User(username='admin', hashed_password=get_password_hash('admin123'), is_active=True)
        db.add(u)
    else:
        u.hashed_password = get_password_hash('admin123')
        u.is_active = True
    db.commit()
    print("OK: admin reset/created")

if __name__ == "__main__":
    main()
