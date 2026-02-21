#!/usr/bin/env python3
"""
Final Checkpoint Test for Event Filter Builder
Task 12: Ensure all tests pass
"""

import subprocess
import sys

def run_test(test_name, test_file):
    """Run a test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        ['python', test_file],
        capture_output=True,
        text=True,
        cwd='.'
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    success = result.returncode == 0
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n{status}: {test_name}")
    
    return success

def main():
    print("="*60)
    print("FINAL CHECKPOINT - Event Filter Builder")
    print("Task 12: Ensure all tests pass")
    print("="*60)
    
    tests = [
        ("Backend Event Filters", "test_event_filters.py"),
        ("API Endpoint Filters", "test_endpoint_filters.py"),
        ("Task 8.1 Verification", "test_task_8_1_verification.py"),
        ("Preview List Logic", "test_preview_list.py"),
        ("Frontend Integration", "test_frontend_integration.py"),
        ("Task 11.1 Integration", "test_task_11_1_integration.py"),
    ]
    
    results = []
    for test_name, test_file in tests:
        success = run_test(test_name, test_file)
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL CHECKPOINT SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Event Filter Builder is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
