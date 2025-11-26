"""
Test runner for the Toxicity-Score project.
This script runs all unit tests and displays a summary.
"""
import unittest
import sys
import os

# Add parent directory to path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_all_tests():
    """Discover and run all unit tests in the tests directory."""
    # Discover all tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


def run_specific_test_file(test_file):
    """Run tests from a specific test file.

    Args:
        test_file: Name of the test file (e.g., 'test_models.py')
    """
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern=test_file)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


def run_specific_test_class(test_module, test_class):
    """Run tests from a specific test class.

    Args:
        test_module: Name of the test module (e.g., 'test_models')
        test_class: Name of the test class (e.g., 'TestCommentModel')
    """
    # Import the module dynamically
    module = __import__(f'tests.{test_module}', fromlist=[test_class])

    # Get the test class
    test_cls = getattr(module, test_class)

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(test_cls)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 70)
    print("Running Toxicity-Score Unit Tests")
    print("=" * 70)
    print()

    if len(sys.argv) > 1:
        # Run specific test file if provided
        test_file = sys.argv[1]
        if not test_file.startswith('test_'):
            test_file = f'test_{test_file}'
        if not test_file.endswith('.py'):
            test_file = f'{test_file}.py'

        print(f"Running tests from: {test_file}")
        print()
        exit_code = run_specific_test_file(test_file)
    else:
        # Run all tests
        print("Running all tests...")
        print()
        exit_code = run_all_tests()

    print()
    print("=" * 70)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("=" * 70)

    sys.exit(exit_code)

