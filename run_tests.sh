#!/bin/bash
# Standalone test runner that works reliably
# Usage: ./run_tests.sh [backend|all|unit|integration]

TEST_TYPE=${1:-backend}

case $TEST_TYPE in
    backend)
        echo "Running backend tests..."
        python -m pytest tests/backend/ -v --tb=short
        ;;
    all)
        echo "Running all tests..."
        python -m pytest tests/ -q --tb=line
        ;;
    unit)
        echo "Running unit tests..."
        python -m pytest tests/backend/ tests/ue5_client/ -v
        ;;
    integration)
        echo "Running integration tests..."
        python -m pytest tests/integration/ -v
        ;;
    *)
        echo "Unknown test type: $TEST_TYPE"
        echo "Usage: ./run_tests.sh [backend|all|unit|integration]"
        exit 1
        ;;
esac
