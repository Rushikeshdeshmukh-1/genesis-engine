import os
import sys
from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "postgresql://postgres:postgres_password@localhost:5432/idea_engine"

def check_ideas():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print(f"Connecting to {DATABASE_URL}...")
            
            # Simple query
            try:
                result = connection.execute(text("SELECT id, title, description, status, overall_score FROM ideas"))
                ideas = result.fetchall()
                
                print(f"\nFound {len(ideas)} ideas:")
                print("-" * 50)
                for idea in ideas:
                    print(f"ID: {idea[0]}")
                    print(f"Title: {idea[1]}")
                    print(f"Status: {idea[3]}")
                    print(f"Score: {idea[4]}")
                    print(f"Description: {idea[2][:100]}...")
                    print("-" * 50)
            except Exception as e:
                 print(f"Error executing select: {e}")
                 # Check tables
                 print("Checking tables...")
                 result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'idea_engine' OR table_schema = 'public'"))
                 for row in result:
                     print(row)

    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    check_ideas()
