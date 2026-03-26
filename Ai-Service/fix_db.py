import pymysql
from app.core.config import settings

# Parse the database URL (basic parsing for mysql+pymysql)
# DATABASE_URL = "mysql+pymysql://root:Tilak1604@localhost:3306/docmind-ai"
db_url = settings.DATABASE_URL.replace("mysql+pymysql://", "")
auth, rest = db_url.split("@")
user, password = auth.split(":")
host_port, db_name = rest.split("/")
host, port = host_port.split(":")

def update_schema():
    print(f"Connecting to database: {db_name} at {host}...")
    try:
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        with connection.cursor() as cursor:
            print("Adding missing columns to 'documents' table...")
            
            # Standard ALTER TABLE syntax
            queries = [
                "ALTER TABLE documents ADD COLUMN extraction_status VARCHAR(50) DEFAULT 'PENDING';",
                "ALTER TABLE documents ADD COLUMN global_summary TEXT;",
                "ALTER TABLE documents ADD COLUMN mind_map_plantuml TEXT;"
            ]
            
            # MySQL 8.0.19+ supports IF NOT EXISTS for columns, but for older versions we might need a safer approach.
            # I'll just run the queries and catch the "Duplicate column" error (1060).
            
            for query in queries:
                try:
                    cursor.execute(query)
                    print(f"Executed: {query[:50]}...")
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1060:
                        print(f"Column already exists, skipping.")
                    else:
                        raise e
            
            connection.commit()
            print("Schema update successful!")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    update_schema()
