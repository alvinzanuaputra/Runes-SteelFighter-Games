from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

# Ganti sesuai konfigurasi PostgreSQL kamu
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/progjar"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def check_connection():
    try:
        # Coba buka koneksi dan eksekusi query sederhana
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Koneksi ke database berhasil:", result.scalar())
    except Exception as e:
        print("❌ Gagal koneksi ke database:", e)

if __name__ == "__main__":
    check_connection()
