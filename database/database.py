from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/progjar"
# DATABASE_URL = "postgresql://postgres.rxbiexzpzproqlqpwrxo:q8zurWtPUeEJDBya@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def check_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Koneksi ke database berhasil:", result.scalar())
    except Exception as e:
        print("❌ Gagal koneksi ke database:", e)

if __name__ == "__main__":
    check_connection()
