import asyncio
import asyncpg
import os
from src.config.settings import settings

async def apply_migrations():
    print("--- Applying Database Migrations ---")
    
    # Connect to DB
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to DB: {e}")
        return

    migrations_dir = "src/persistence/migrations"
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".sql")])
    
    for filename in migration_files:
        print(f"Running migration: {filename}...")
        filepath = os.path.join(migrations_dir, filename)
        with open(filepath, "r") as f:
            sql = f.read()
            
        try:
            await conn.execute(sql)
            print(f"✅ Applied {filename}")
        except Exception as e:
            # Ignore "already exists" errors for idempotency
            if "already exists" in str(e):
                print(f"⚠️  Skipping {filename} (already exists)")
            else:
                print(f"❌ Error applying {filename}: {e}")
                
    await conn.close()
    print("--- Migrations Complete ---")

if __name__ == "__main__":
    asyncio.run(apply_migrations())
