from database.database import Base, engine
import models 

# Migrasi semua model ke DB
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
