# fastapi_app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# اتصال به پایگاه‌داده SQLite
DATABASE_URL = "sqlite:///datacatalog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# جدول واسط رابطه many-to-many
etl_tables = Table(
    "etl_tables",
    Base.metadata,
    Column("etl_id", Integer, ForeignKey("etls.id"), primary_key=True),
    Column("table_id", Integer, ForeignKey("tables.id"), primary_key=True),
)

# مدل‌های داده
class ETL(Base):
    __tablename__ = "etls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    tables = relationship("Table", secondary=etl_tables, back_populates="etls")

class Schema(Base):
    __tablename__ = "schemas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    tables = relationship("Table", back_populates="schema")

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=False)
    schema = relationship("Schema", back_populates="tables")
    etls = relationship("ETL", secondary=etl_tables, back_populates="tables")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1)

# ایجاد جدول‌ها
Base.metadata.create_all(bind=engine)

# dependency گرفتن session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# تنظیمات JWT
SECRET_KEY = "change-this-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# توابع احراز هویت
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ایجاد برنامه FastAPI
app = FastAPI(
    title="Mini DataCatalog API",
    description="FastAPI app with ETL and authentication",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "FastAPI running"}

# endpointهای ETL
@app.get("/etl/names")
def get_etl_names(db: Session = Depends(get_db)):
    etls = db.query(ETL).all()
    return [etl.name for etl in etls]

@app.get("/etl/{name}/tables")
def get_etl_tables(name: str, db: Session = Depends(get_db)):
    etl = db.query(ETL).filter(ETL.name == name).first()
    if not etl:
        raise HTTPException(status_code=404, detail="ETL not found")
    return [{"id": t.id, "name": t.name, "schema": t.schema.name} for t in etl.tables]

# endpointهای احراز هویت
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {"username": current_user.username, "is_active": bool(current_user.is_active)}
