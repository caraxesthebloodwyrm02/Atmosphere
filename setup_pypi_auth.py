import os
import sys
from getpass import getpass

def setup_pypi_token():
    # Check if token exists in environment
    token = os.environ.get('PYPI_TOKEN')
    if token:
        print(f"✅ Found PYPI_TOKEN in environment: {token[:10]}...")
        return token
    
    # If not found, prompt to set it
    print("🔑 PyPI token not found in environment variables")
    print("To set it up, you can use one of these methods:")
    print("\n1. Temporary (current session only):")
    print("   $env:PYPI_TOKEN = 'pypi-...'  # PowerShell")
    print("   set PYPI_TOKEN=pypi-...       # CMD")
    print("   export PYPI_TOKEN='pypi-...'  # Bash")
    
    print("\n2. Permanent (Windows):")
    print("   [Environment]::SetEnvironmentVariable('PYPI_TOKEN', 'pypi-...', 'User')  # PowerShell")
    
    print("\n3. Or enter your PyPI token now (it will be used only for this session):")
    token = getpass("PyPI Token (starts with pypi-): ").strip()
    
    if token and token.startswith('pypi-'):
        os.environ['PYPI_TOKEN'] = token
        print("✅ Token set for current session")
        return token
    else:
        print("❌ Invalid or no token provided")
        return None

if __name__ == "__main__":
    token = setup_pypi_token()
    if token:
        # Update .pypirc with the token
        import configparser
        c = configparser.ConfigParser()
        c.read('.pypirc')
        c.set('pypi', 'password', token)
        with open('.pypirc', 'w') as f:
            c.write(f)
        print("✅ Updated .pypirc with the token")
        print("\n🔧 Now you can upload with:")
        print("   python -m twine upload dist/*")
    else:
        print("\n⚠️  Please set your PyPI token and try again")
        print("   Get token from: https://pypi.org/manage/account/token/")