"""
Test package for Personal Memory AI project.

This package contains comprehensive tests for all components of the application:
- Data loaders (Gmail, Notion, Calendar)
- Memory system (Vectorstore, QA Chain)
- Agent functionality
- Integration tests
- Docker configuration tests

To run all tests:
    python tests/run_all_tests.py

To run specific test suites:
    python tests/run_all_tests.py main
    python tests/run_all_tests.py loaders
    python tests/run_all_tests.py memory
    python tests/run_all_tests.py agent
    python tests/run_all_tests.py integration
    python tests/run_all_tests.py docker

To run individual test files:
    python -m unittest tests.test_main
    python -m unittest tests.test_loaders
    python -m unittest tests.test_memory_system
    python -m unittest tests.test_agent
    python -m unittest tests.test_integration
    python -m unittest tests.test_docker
"""

__version__ = "1.0.0"
__author__ = "Personal Memory AI Team"
