#!/usr/bin/env python3
"""
Comprehensive test runner for the Personal Memory AI project.
This script runs all tests and generates a detailed report.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.write(f"✅ {test._testMethodName} ... OK\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(f"❌ {test._testMethodName} ... ERROR\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(f"❌ {test._testMethodName} ... FAIL\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(f"⏭️  {test._testMethodName} ... SKIPPED ({reason})\n")


def run_test_suite(test_module_name, description):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {description}")
    print(f"{'='*60}")
    
    try:
        # Import the test module
        test_module = __import__(f"tests.{test_module_name}", fromlist=[test_module_name])
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests with custom result class
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            resultclass=ColoredTextTestResult
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Print results
        print(f"Tests run: {result.testsRun}")
        print(f"Successes: {result.success_count}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        print(f"Time: {end_time - start_time:.2f}s")
        
        # Print detailed output
        output = stream.getvalue()
        if output:
            print("\nDetailed Output:")
            print(output)
        
        # Print failures and errors
        if result.failures:
            print("\n❌ FAILURES:")
            for test, traceback in result.failures:
                print(f"\n{test}:")
                print(traceback)
        
        if result.errors:
            print("\n❌ ERRORS:")
            for test, traceback in result.errors:
                print(f"\n{test}:")
                print(traceback)
        
        return result
        
    except ImportError as e:
        print(f"❌ Could not import {test_module_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error running {test_module_name}: {e}")
        return None


def main():
    """Main test runner function"""
    print("🚀 Personal Memory AI - Comprehensive Test Suite")
    print("=" * 60)
    
    # Test suites to run
    test_suites = [
        ("test_main", "Main Application Flow Tests"),
        ("test_loaders", "Data Loader Tests"),
        ("test_memory_system", "Memory System Tests"),
        ("test_agent", "Agent and Chat Interface Tests"),
        ("test_integration", "Integration Tests"),
        ("test_docker", "Docker Configuration Tests")
    ]
    
    total_tests = 0
    total_successes = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    failed_suites = []
    
    start_time = time.time()
    
    # Run each test suite
    for test_module, description in test_suites:
        result = run_test_suite(test_module, description)
        
        if result:
            total_tests += result.testsRun
            total_successes += result.success_count
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
            
            if result.failures or result.errors:
                failed_suites.append(test_module)
        else:
            failed_suites.append(test_module)
    
    end_time = time.time()
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Suites: {len(test_suites)}")
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Successes: {total_successes}")
    print(f"❌ Failures: {total_failures}")
    print(f"💥 Errors: {total_errors}")
    print(f"⏭️  Skipped: {total_skipped}")
    print(f"⏱️  Total Time: {end_time - start_time:.2f}s")
    
    if failed_suites:
        print(f"\n❌ Failed Test Suites: {', '.join(failed_suites)}")
    else:
        print(f"\n🎉 All test suites passed!")
    
    # Calculate success rate
    if total_tests > 0:
        success_rate = (total_successes / total_tests) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Return exit code
    return 0 if not failed_suites and total_failures == 0 and total_errors == 0 else 1


def run_specific_test(test_name):
    """Run a specific test file"""
    if test_name.startswith("test_"):
        test_name = test_name[5:]  # Remove "test_" prefix
    
    test_suites = {
        "main": ("test_main", "Main Application Flow Tests"),
        "loaders": ("test_loaders", "Data Loader Tests"),
        "memory": ("test_memory_system", "Memory System Tests"),
        "agent": ("test_agent", "Agent and Chat Interface Tests"),
        "integration": ("test_integration", "Integration Tests"),
        "docker": ("test_docker", "Docker Configuration Tests")
    }
    
    if test_name in test_suites:
        test_module, description = test_suites[test_name]
        result = run_test_suite(test_module, description)
        return 0 if result and not result.failures and not result.errors else 1
    else:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_suites.keys())}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        exit_code = run_specific_test(sys.argv[1])
    else:
        # Run all tests
        exit_code = main()
    
    sys.exit(exit_code)
