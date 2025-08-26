#!/usr/bin/env python3
import psycopg2
import sys
import socket
import subprocess
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

def check_network_info():
    """Check network configuration and available interfaces."""
    print("\nNetwork Information:")
    print("-" * 30)
    
    try:
        # Check hostname
        result = subprocess.run(['hostname'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Current hostname: {result.stdout.strip()}")
        
        # Check network interfaces
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Network interfaces found")
        else:
            print("Could not retrieve network interfaces")
            
        # Check routing table
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Routing table available")
        else:
            print("Could not retrieve routing table")
            
    except Exception as e:
        print(f"Error checking network info: {e}")

def test_postgres_connection(connection_string):
    """Test PostgreSQL connection with the provided connection string."""
    try:
        print("Testing PostgreSQL connection...")
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

if __name__ == "__main__":
    # The connection string from the user
    connection_string = "postgresql://postgres:IQchuqTamVFIcQLEMIQgUHraivGKZukL@postgres.railway.internal:5432/railway"
    
    print("PostgreSQL Connection Test")
    print("=" * 50)
    
    # Check network information first
    check_network_info()
    
    success = test_postgres_connection(connection_string)
    
    if success:
        print("\n🎉 Connection test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Connection test FAILED!")
        print("\nPossible issues:")
        print("1. Hostname 'postgres.railway.internal' cannot be resolved")
        print("2. You may not be in the Railway internal network")
        print("3. The hostname might be incorrect")
        print("4. Check if you're running this from the right environment")
        sys.exit(1)