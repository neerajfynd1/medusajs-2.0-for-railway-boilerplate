#!/usr/bin/env python3
import psycopg2
import sys
from urllib.parse import urlparse

def test_external_connection():
    """Test external Railway PostgreSQL connection."""
    
    # Test different external connection patterns
    test_connections = [
        "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@postgres.railway.app:5432/railway",
        "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@34.107.141.139:5432/railway",
        "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@postgres.railway.app:5432/railway?sslmode=require",
        "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@34.107.141.139:5432/railway?sslmode=require"
    ]
    
    for i, connection_string in enumerate(test_connections, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {connection_string}")
        print(f"{'='*60}")
        
        try:
            # Parse the connection string
            parsed = urlparse(connection_string)
            print(f"Host: {parsed.hostname}")
            print(f"Port: {parsed.port}")
            print(f"Database: {parsed.path[1:] if parsed.path else 'N/A'}")
            print(f"Username: {parsed.username}")
            print(f"Query params: {parsed.query}")
            
            # Attempt connection
            print(f"\nAttempting connection...")
            conn = psycopg2.connect(connection_string)
            
            # Test basic operations
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ SUCCESS! PostgreSQL version: {version[0]}")
            
            cursor.close()
            conn.close()
            print("✓ Connection closed successfully")
            
            print(f"\n🎉 Test {i} PASSED!")
            return True
            
        except psycopg2.OperationalError as e:
            print(f"✗ Operational error: {e}")
        except psycopg2.Error as e:
            print(f"✗ PostgreSQL error: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    print(f"\n❌ All external connection tests failed")
    return False

if __name__ == "__main__":
    print("External Railway PostgreSQL Connection Test")
    print("Testing various external connection patterns...")
    
    success = test_external_connection()
    
    if success:
        print("\n🎉 External connection successful!")
        print("Use the working connection string for your application.")
        sys.exit(0)
    else:
        print("\n❌ All connection attempts failed.")
        print("\nNext steps:")
        print("1. Check Railway dashboard for correct external connection details")
        print("2. Verify if the database service is running")
        print("3. Check if you need to whitelist your IP address")
        print("4. Contact Railway support if issues persist")
        sys.exit(1)