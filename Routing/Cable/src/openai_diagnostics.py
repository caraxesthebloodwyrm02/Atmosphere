"""
OpenAI Integration Diagnostics

This module provides verification for OpenAI API endpoint authenticity and basic functionality.
It performs TLS certificate validation and runs a smoke test to ensure the integration
is communicating with the real OpenAI API and not a malicious proxy.
"""

import os
import ssl
import socket
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("openai_diagnostics")

# Constants
OPENAI_API_URL = "https://api.openai.com/v1/models"
EXPECTED_ISSUER = "CN=DigiCert Global Root CA, OU=www.digicert.com, O=DigiCert Inc, C=US"
EXPECTED_ORGANIZATION = "OpenAI, L.L.C."
EXPECTED_ORGANIZATION_UNIT = "IT Department"
SMOKE_TEST_MODEL = "gpt-3.5-turbo"  # Using a lightweight model for the smoke test


def get_certificate_info(hostname: str = "api.openai.com", port: int = 443) -> Dict[str, Any]:
    """
    Retrieve and parse the SSL certificate from the specified host.
    
    Args:
        hostname: The host to connect to (default: api.openai.com)
        port: The port to connect to (default: 443 for HTTPS)
        
    Returns:
        Dictionary containing certificate information
    """
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            
            # Get the certificate in binary format for additional verification
            der_cert = ssock.getpeercert(binary_form=True)
            cert_obj = ssl.DER_cert_to_PEM_cert(der_cert)
            
            # Parse the certificate
            x509 = ssl.PEM_cert_to_DER_cert(cert_obj)
            x509 = ssl.DER_cert_to_PEM_cert(x509)
            
            # Extract subject information
            subject = dict(x[0] for x in cert['subject'])
            issuer = dict(x[0] for x in cert['issuer'])
            
            return {
                'subject': subject,
                'issuer': issuer,
                'version': cert.get('version'),
                'serial_number': cert.get('serialNumber'),
                'not_before': cert.get('notBefore'),
                'not_after': cert.get('notAfter'),
                'cert_pem': x509,
                'raw_cert': cert
            }


def verify_openai_certificate() -> Tuple[bool, Dict[str, Any]]:
    """
    Verify that the OpenAI API endpoint has a valid certificate from the expected issuer.
    
    Returns:
        Tuple of (is_valid, details) where details contains certificate information
    """
    try:
        logger.info("Verifying OpenAI TLS certificate...")
        cert_info = get_certificate_info()
        
        # Check issuer
        issuer_str = ", ".join(f"{k}={v}" for k, v in cert_info['issuer'].items())
        is_issuer_valid = EXPECTED_ISSUER in issuer_str
        
        # Check subject (organization)
        subject = cert_info['subject']
        is_org_valid = subject.get('organizationName') == EXPECTED_ORGANIZATION
        
        # Check certificate expiration
        not_after = cert_info['not_after']
        expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
        is_not_expired = datetime.utcnow() < expiry_date
        
        # Overall validation
        is_valid = all([is_issuer_valid, is_org_valid, is_not_expired])
        
        result = {
            'is_valid': is_valid,
            'issuer': cert_info['issuer'],
            'expected_issuer': EXPECTED_ISSUER,
            'is_issuer_valid': is_issuer_valid,
            'organization': subject.get('organizationName'),
            'is_org_valid': is_org_valid,
            'expiry_date': expiry_date.isoformat(),
            'is_not_expired': is_not_expired,
            'certificate_info': cert_info
        }
        
        if is_valid:
            logger.info("✅ OpenAI TLS certificate verification passed")
        else:
            logger.warning("❌ OpenAI TLS certificate verification failed")
            logger.warning(f"Issuer: {issuer_str}")
            logger.warning(f"Expected issuer: {EXPECTED_ISSUER}")
            
        return is_valid, result
        
    except Exception as e:
        error_msg = f"Error verifying OpenAI certificate: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, {
            'is_valid': False,
            'error': error_msg,
            'exception': str(e)
        }


def run_openai_smoke_test(api_key: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Run a simple smoke test against the OpenAI API.
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Tuple of (success, response_data)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple chat completion request
    data = {
        "model": SMOKE_TEST_MODEL,
        "messages": [{"role": "user", "content": "Hello, this is a smoke test. Please respond with 'pong'."}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        logger.info("Running OpenAI API smoke test...")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            
            # Check if we got a valid response
            is_success = (
                response.status == 200 and 
                'choices' in response_data and 
                len(response_data['choices']) > 0 and
                'message' in response_data['choices'][0] and
                'content' in response_data['choices'][0]['message']
            )
            
            if is_success:
                logger.info("✅ OpenAI API smoke test passed")
            else:
                logger.warning(f"❌ OpenAI API smoke test failed: {response_data}")
                
            return is_success, {
                'status_code': response.status,
                'response_data': response_data,
                'model': response_data.get('model'),
                'usage': response_data.get('usage', {}),
                'request_id': response.headers.get('x-request-id')
            }
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error: {e.code} {e.reason}"
        logger.error(error_msg)
        try:
            error_body = e.read().decode('utf-8')
            logger.error(f"Error response: {error_body}")
            error_data = json.loads(error_body)
        except:
            error_data = {"error": str(e)}
            
        return False, {
            'status_code': e.code,
            'error': error_msg,
            'error_details': error_data,
            'request_id': e.headers.get('x-request-id') if hasattr(e, 'headers') else None
        }
        
    except Exception as e:
        error_msg = f"Error during smoke test: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, {
            'error': error_msg,
            'exception': str(e)
        }


def verify_openai_integration(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify the OpenAI integration by checking the TLS certificate and running a smoke test.
    
    Args:
        api_key: Optional OpenAI API key. If not provided, will try to get from environment.
        
    Returns:
        Dictionary with verification results
    """
    if api_key is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Run certificate verification
    cert_valid, cert_result = verify_openai_certificate()
    
    # Run smoke test
    smoke_test_success, smoke_test_result = run_openai_smoke_test(api_key)
    
    # Overall status
    is_valid = cert_valid and smoke_test_success
    
    # Create result dictionary
    result = {
        'timestamp': datetime.utcnow().isoformat(),
        'is_valid': is_valid,
        'certificate_verification': {
            'passed': cert_valid,
            'details': cert_result
        },
        'smoke_test': {
            'passed': smoke_test_success,
            'details': smoke_test_result
        },
        'environment': {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'openai_api_base': os.environ.get('OPENAI_API_BASE', 'https://api.openai.com'),
            'openai_api_version': os.environ.get('OPENAI_API_VERSION', '')
        }
    }
    
    # Log overall status
    if is_valid:
        logger.info("✅ OpenAI integration verification passed")
    else:
        logger.error("❌ OpenAI integration verification failed")
        
    return result


def main():
    """Command-line entry point for running diagnostics."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify OpenAI integration')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY environment variable)')
    parser.add_argument('--skip-cert-check', action='store_true', help='Skip TLS certificate verification')
    parser.add_argument('--skip-smoke-test', action='store_true', help='Skip API smoke test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Run verification
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'is_valid': False,
            'certificate_verification': {'passed': False, 'details': {}},
            'smoke_test': {'passed': False, 'details': {}}
        }
        
        # Run certificate verification if not skipped
        if not args.skip_cert_check:
            cert_valid, cert_result = verify_openai_certificate()
            result['certificate_verification'] = {
                'passed': cert_valid,
                'details': cert_result
            }
        else:
            logger.warning("⚠️  Skipping certificate verification")
            result['certificate_verification']['skipped'] = True
        
        # Run smoke test if not skipped and certificate is valid (or check was skipped)
        if not args.skip_smoke_test and (args.skip_cert_check or cert_valid):
            api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not provided. Use --api-key or set OPENAI_API_KEY environment variable.")
                
            smoke_test_success, smoke_test_result = run_openai_smoke_test(api_key)
            result['smoke_test'] = {
                'passed': smoke_test_success,
                'details': smoke_test_result
            }
        elif not args.skip_smoke_test:
            logger.warning("⚠️  Skipping smoke test due to failed certificate verification")
            result['smoke_test']['skipped'] = True
            result['smoke_test']['details'] = {'reason': 'certificate_verification_failed'}
        else:
            logger.warning("⚠️  Skipping smoke test")
            result['smoke_test']['skipped'] = True
        
        # Determine overall status
        cert_check_passed = args.skip_cert_check or result['certificate_verification']['passed']
        smoke_test_passed = args.skip_smoke_test or result['smoke_test'].get('passed', False)
        result['is_valid'] = cert_check_passed and smoke_test_passed
        
        # Print summary
        print("\n=== OpenAI Integration Diagnostics ===")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Overall Status: {'✅ PASSED' if result['is_valid'] else '❌ FAILED'}")
        
        print("\n--- Certificate Verification ---")
        if args.skip_cert_check:
            print("Status: SKIPPED (--skip-cert-check)")
        else:
            status = "PASSED" if result['certificate_verification']['passed'] else "FAILED"
            print(f"Status: {'✅' if result['certificate_verification']['passed'] else '❌'} {status}")
            if 'issuer' in result['certificate_verification']['details']:
                print(f"Issuer: {result['certificate_verification']['details']['issuer']}")
            if 'organization' in result['certificate_verification']['details']:
                print(f"Organization: {result['certificate_verification']['details']['organization']}")
            if 'expiry_date' in result['certificate_verification']['details']:
                print(f"Expires: {result['certificate_verification']['details']['expiry_date']}")
        
        print("\n--- API Smoke Test ---")
        if args.skip_smoke_test:
            print("Status: SKIPPED (--skip-smoke-test)")
        elif result['smoke_test'].get('skipped', False):
            print("Status: SKIPPED (certificate verification failed)")
        else:
            status = "PASSED" if result['smoke_test']['passed'] else "FAILED"
            print(f"Status: {'✅' if result['smoke_test']['passed'] else '❌'} {status}")
            if 'details' in result['smoke_test'] and 'model' in result['smoke_test']['details']:
                print(f"Model: {result['smoke_test']['details']['model']}")
            if 'details' in result['smoke_test'] and 'usage' in result['smoke_test']['details']:
                print(f"Tokens used: {result['smoke_test']['details']['usage']}")
            if 'details' in result['smoke_test'] and 'request_id' in result['smoke_test']['details']:
                print(f"Request ID: {result['smoke_test']['details']['request_id']}")
        
        # Exit with appropriate status code
        sys.exit(0 if result['is_valid'] else 1)
        
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}", exc_info=args.verbose)
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
