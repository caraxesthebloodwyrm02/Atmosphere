#!/usr/bin/env python3
"""
OpenAI API Connection Test & Client Onboarding
Comprehensive testing and authentication for direct OpenAI API integration.
"""

import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIConnectionTester:
    """Comprehensive OpenAI API connection tester and onboarding."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize connection tester."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.test_results = {}
        self.connection_status = "disconnected"
        
        if not self.api_key:
            logger.error("❌ No OpenAI API key provided")
            return
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive connection and capability test."""
        logger.info("🔍 Starting comprehensive OpenAI API test...")
        
        test_suite = {
            "authentication": self._test_authentication,
            "models": self._test_models_access,
            "chat_completion": self._test_chat_completion,
            "rate_limits": self._test_rate_limits,
            "token_usage": self._test_token_usage,
            "error_handling": self._test_error_handling
        }
        
        results = {}
        
        for test_name, test_func in test_suite.items():
            logger.info(f"🧪 Running {test_name} test...")
            try:
                result = await test_func()
                results[test_name] = result
                if result["success"]:
                    logger.info(f"✅ {test_name} test passed")
                else:
                    logger.warning(f"⚠️ {test_name} test failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"❌ {test_name} test crashed: {e}")
                results[test_name] = {"success": False, "error": str(e)}
        
        # Calculate overall status
        passed_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        
        self.connection_status = "connected" if passed_tests == total_tests else "partial"
        
        overall_result = {
            "timestamp": datetime.now().isoformat(),
            "connection_status": self.connection_status,
            "tests_passed": passed_tests,
            "total_tests": total_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
            "test_results": results
        }
        
        logger.info(f"🎯 Test complete: {passed_tests}/{total_tests} tests passed")
        return overall_result
    
    async def _test_authentication(self) -> Dict[str, Any]:
        """Test API authentication."""
        try:
            # Test with models list - requires authentication
            models = self.client.models.list()
            return {
                "success": True,
                "models_count": len(models.data),
                "message": "Authentication successful"
            }
        except openai.AuthenticationError as e:
            return {
                "success": False,
                "error": "Authentication failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e)
            }
    
    async def _test_models_access(self) -> Dict[str, Any]:
        """Test access to available models."""
        try:
            models = self.client.models.list()
            model_list = [model.id for model in models.data]
            
            # Check for key models
            key_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
            available_key_models = [m for m in key_models if m in model_list]
            
            return {
                "success": True,
                "total_models": len(model_list),
                "key_models_available": available_key_models,
                "all_models": model_list[:10]  # First 10 models
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Failed to access models",
                "details": str(e)
            }
    
    async def _test_chat_completion(self) -> Dict[str, Any]:
        """Test chat completion functionality."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API test successful' in exactly those words."}
                ],
                max_tokens=10,
                temperature=0
            )
            
            content = response.choices[0].message.content
            expected = "API test successful"
            
            return {
                "success": expected.lower() in content.lower(),
                "response": content,
                "model_used": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Chat completion failed",
                "details": str(e)
            }
    
    async def _test_rate_limits(self) -> Dict[str, Any]:
        """Test rate limit handling."""
        try:
            # Make multiple rapid requests to test rate limiting
            start_time = datetime.now()
            
            tasks = []
            for i in range(3):
                task = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Test message {i+1}"}],
                    max_tokens=5
                )
                tasks.append(task)
            
            # Execute concurrently
            responses = await asyncio.gather(*asyncio.to_thread, *tasks, return_exceptions=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            
            return {
                "success": len(successful_responses) >= 2,  # At least 2 should succeed
                "requests_sent": len(tasks),
                "successful_requests": len(successful_responses),
                "duration_seconds": duration,
                "message": "Rate limits handled properly" if len(successful_responses) >= 2 else "Rate limits too restrictive"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Rate limit test failed",
                "details": str(e)
            }
    
    async def _test_token_usage(self) -> Dict[str, Any]:
        """Test token usage tracking."""
        try:
            # Test with known token count
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Count the tokens in this response."}
                ],
                max_tokens=50
            )
            
            usage = response.usage
            
            return {
                "success": True,
                "token_usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": response.model,
                "message": "Token usage tracking working"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Token usage test failed",
                "details": str(e)
            }
    
    async def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling with invalid requests."""
        try:
            # Test with invalid model
            try:
                response = self.client.chat.completions.create(
                    model="invalid-model-name",
                    messages=[{"role": "user", "content": "Test"}]
                )
                return {
                    "success": False,
                    "error": "Should have failed with invalid model",
                    "response": response
                }
            except openai.NotFoundError as e:
                # This is expected
                return {
                    "success": True,
                    "error_handled": "invalid_model",
                    "message": "Proper error handling for invalid model"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": "Unexpected error type",
                    "details": str(e)
                }
        except Exception as e:
            return {
                "success": False,
                "error": "Error handling test failed",
                "details": str(e)
            }
    
    def generate_onboarding_report(self, test_results: Dict[str, Any]) -> str:
        """Generate comprehensive onboarding report."""
        report = []
        report.append("=" * 60)
        report.append("🚀 OPENAI API CONNECTION & ONBOARDING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {test_results['timestamp']}")
        report.append(f"Connection Status: {test_results['connection_status'].upper()}")
        report.append(f"Tests Passed: {test_results['tests_passed']}/{test_results['total_tests']}")
        report.append(f"Success Rate: {test_results['success_rate']}")
        report.append("")
        
        # Detailed test results
        report.append("📋 DETAILED TEST RESULTS:")
        report.append("-" * 40)
        
        for test_name, result in test_results['test_results'].items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            report.append(f"{status} {test_name.upper()}")
            
            if result.get("success", False):
                for key, value in result.items():
                    if key != "success":
                        report.append(f"    • {key}: {value}")
            else:
                report.append(f"    • Error: {result.get('error', 'Unknown')}")
                if 'details' in result:
                    report.append(f"    • Details: {result['details']}")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 20)
        
        if test_results['connection_status'] == 'connected':
            report.append("✅ API connection is fully functional")
            report.append("✅ Ready for production use")
            report.append("✅ All core features working")
        else:
            report.append("⚠️ Some issues detected - review failed tests")
            report.append("🔧 Check API key and permissions")
            report.append("📚 Review OpenAI API documentation")
        
        report.append("")
        report.append("🔗 USEFUL LINKS:")
        report.append("• API Docs: https://platform.openai.com/docs/overview")
        report.append("• Models: https://platform.openai.com/docs/models")
        report.append("• Pricing: https://platform.openai.com/pricing")
        report.append("=" * 60)
        
        return "\n".join(report)

async def main():
    """Main onboarding test function."""
    print("🚀 OpenAI API Connection Test & Client Onboarding")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("💡 Set it in your environment or .env file")
        return
    
    # Initialize tester
    tester = OpenAIConnectionTester(api_key)
    
    if not tester.client:
        print("❌ Failed to initialize OpenAI client")
        return
    
    # Run comprehensive test
    print("🧪 Running comprehensive API test suite...")
    results = await tester.run_comprehensive_test()
    
    # Generate and display report
    report = tester.generate_onboarding_report(results)
    print(report)
    
    # Save report to file
    report_file = f"openai_onboarding_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")
    
    # Test direct API communication
    if results['connection_status'] == 'connected':
        print("\n🔌 Testing direct API communication...")
        try:
            # Simple test message
            response = tester.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Confirm the API is working with a brief message."}
                ],
                max_tokens=50
            )
            
            print(f"✅ Direct API Response: {response.choices[0].message.content}")
            print(f"📊 Tokens Used: {response.usage.total_tokens}")
            
        except Exception as e:
            print(f"❌ Direct API test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
