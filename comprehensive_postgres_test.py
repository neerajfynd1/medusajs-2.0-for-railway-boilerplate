#!/usr/bin/env python3
import psycopg2
import sys
import socket
import subprocess
import os
from urllib.parse import urlparse

def test_dns_resolution(hostname):
    """Test DNS resolution of the hostname."""
    try:
        print(f"Testing DNS resolution for {hostname}...")
        ip_address = socket.gethostbyname(hostname)
        print(f"✓ DNS resolution successful: {hostname} -> {ip_address}")
        return ip_address
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed for {hostname}: {e}")
        return None

def test_network_connectivity(hostname, port):
    """Test basic network connectivity to the host."""
    try:
        print(f"Testing network connectivity to {hostname}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✓ Network connectivity successful to {hostname}:{port}")
            return True
        else:
            print(f"✗ Network connectivity failed to {hostname}:{port} (error code: {result})")
            return False
    except Exception as e:
        print(f"✗ Network test error: {e}")
        return False

def check_environment_variables():
    """Check for common Railway environment variables."""
    print("\nEnvironment Variables Check:")
    print("-" * 40)
    
    railway_vars = [
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID', 
        'RAILWAY_ENVIRONMENT',
        'DATABASE_URL',
        'POSTGRES_URL',
        'PGHOST',
        'PGPORT',
        'PGDATABASE',
        'PGUSER',
        'PGPASSWORD'
    ]
    
    found_vars = []
    for var in railway_vars:
        value = os.environ.get(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"  {var}: {'*' * len(value)}")
            else:
                print(f"  {var}: {value}")
            found_vars.append(var)
    
    if not found_vars:
        print("  No Railway environment variables found")
    
    return found_vars

def check_network_info():
    """Check network configuration and available interfaces."""
    print("\nNetwork Information:")
    print("-" * 30)
    
    try:
        # Check hostname
        result = subprocess.run(['hostname'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Current hostname: {result.stdout.strip()}")
        
        # Check if we're in a container
        if os.path.exists('/.dockerenv'):
            print("Running inside Docker container")
        else:
            print("Not running inside Docker container")
            
        # Check resolv.conf for DNS configuration
        if os.path.exists('/etc/resolv.conf'):
            print("DNS configuration file exists")
        else:
            print("DNS configuration file not found")
            
    except Exception as e:
        print(f"Error checking network info: {e}")

def test_alternative_connections():
    """Test alternative connection methods and common Railway patterns."""
    print("\nTesting Alternative Connection Methods:")
    print("-" * 45)
    
    # Test common Railway hostname patterns
    test_hostnames = [
        "postgres.railway.internal",
        "postgres.railway.app",
        "localhost",
        "127.0.0.1"
    ]
    
    for hostname in test_hostnames:
        print(f"\nTesting hostname: {hostname}")
        ip = test_dns_resolution(hostname)
        if ip:
            test_network_connectivity(hostname, 5432)

def test_postgres_connection(connection_string):
    """Test PostgreSQL connection with the provided connection string."""
    try:
        print("\nTesting PostgreSQL connection...")
        print(f"Connection string: {connection_string}")
        
        # Parse the connection string to show the components
        parsed = urlparse(connection_string)
        print(f"\nParsed connection details:")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port}")
        print(f"  Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"  Username: {parsed.username}")
        print(f"  Password: {'*' * len(parsed.password) if parsed.password else 'N/A'}")
        
        # Test DNS resolution first
        ip_address = test_dns_resolution(parsed.hostname)
        if not ip_address:
            print("DNS resolution failed. Cannot proceed with network connectivity test.")
            return False
        
        # Test network connectivity
        if not test_network_connectivity(parsed.hostname, parsed.port):
            print("Network connectivity failed. Cannot proceed with database connection.")
            return False
        
        # Attempt to connect
        print(f"\nAttempting to connect...")
        conn = psycopg2.connect(connection_string)
        
        # Test basic operations
        cursor = conn.cursor()
        
        # Test version query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Connection successful!")
        print(f"  PostgreSQL version: {version[0]}")
        
        # Test current database
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"  Current database: {current_db[0]}")
        
        # Test current user
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()
        print(f"  Current user: {current_user[0]}")
        
        # Close connections
        cursor.close()
        conn.close()
        print("✓ Connection closed successfully")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"✗ PostgreSQL operational error:")
        print(f"  Error message: {e}")
        return False
    except psycopg2.Error as e:
        print(f"✗ PostgreSQL connection failed:")
        print(f"  Error code: {e.pgcode}")
        print(f"  Error message: {e.pgerror}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False

def main():
    """Main function to run all tests."""
    print("Comprehensive PostgreSQL Connection Test")
    print("=" * 60)
    
    # Check environment and network information
    check_environment_variables()
    check_network_info()
    
    # Test alternative connection methods
    test_alternative_connections()
    
    # Test the main connection string
    connection_string = "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@postgres.railway.internal:5432/railway"
    
    success = test_postgres_connection(connection_string)
    
    if success:
        print("\n🎉 Connection test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Connection test FAILED!")
        print("\nTroubleshooting Steps:")
        print("1. Verify you're running this from the correct Railway environment")
        print("2. Check if the hostname 'postgres.railway.internal' is correct")
        print("3. Ensure you're in the Railway internal network")
        print("4. Try using the external connection string if available")
        print("5. Check Railway dashboard for correct connection details")
        print("\nCommon Railway Connection Patterns:")
        print("- Internal: postgres.railway.internal:5432")
        print("- External: postgres.railway.app:5432 (or custom domain)")
        print("- Environment variables: DATABASE_URL, POSTGRES_URL")
        sys.exit(1)

if __name__ == "__main__":
    main()