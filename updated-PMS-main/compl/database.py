from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

# Database connection string
DATABASE_URL = "mysql+pymysql://root:@localhost/parking_db"

# Create engine with optimized connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Check connection validity before using
    pool_timeout=30,     # Wait up to 30 seconds for a connection from the pool
    connect_args={
        'connect_timeout': 60,  # Timeout for establishing new connections (seconds)
    }
)

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Function to initialize database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)
