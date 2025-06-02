import subprocess
import sys
import os
import importlib.util
from typing import List, Tuple

TEST_FILE: str = "tests.py"
COVERAGE_MODULE: str = "app"


def check_required_files() -> bool:
    """
    Checks for the presence of essential files for the tests to run
    """
    print("Checking for required files")
    env_description_lines = [
        "Environment configuration file (.env) is missing.",
        "Please create a '.env' file in the root directory, you can use '.env.example' as a template.",
    ]
    env_full_description = "\n   ".join(env_description_lines)

    required_files: List[Tuple[str, str, bool]] = [
        (".env", env_full_description, True),
        ("schema.sql", "Database schema definition ('schema.sql') not found.", False),
        ("app.py", "Flask application file ('app.py') not found.", False),
        (TEST_FILE, f"Pytest test file ('{TEST_FILE}') not found.", False),
    ]
    all_present: bool = True
    missing_file_details: List[str] = []

    for filename, description_if_missing, _ in required_files:
        if not os.path.exists(filename):
            if filename == ".env":
                missing_file_details.append(f"Error: {description_if_missing}")
            else:
                missing_file_details.append(
                    f"Error: {description_if_missing}\n   Please ensure '{filename}' exists."
                )
            all_present = False

    if not all_present:
        print("\n" + "=" * 50)
        print("Error: Missing one or more essential files required for testing:")
        for detail in missing_file_details:
            print(detail)
        print("=" * 50)
    else:
        print("All required files found.")
    return all_present


def check_test_dependencies() -> bool:
    """
    Checks if required dependencies are installed.
    """
    print("Checking for required dependencies.")
    dependencies_to_check: List[str] = ["pytest", "pytest_cov"]
    missing_deps: List[str] = []

    for dep_name in dependencies_to_check:
        spec = importlib.util.find_spec(dep_name)
        if spec is None:
            missing_deps.append(dep_name)

    if missing_deps:
        print("\n" + "=" * 50)
        print("Error: Missing required dependencies.")
        for dep in missing_deps:
            print(f"{dep} is not installed.")
        print(
            "\nPlease install the required dependencies. This can be done by running:"
        )
        print("pip install -r requirements-test.txt")
        print("\n" + "=" * 50)
        return False

    print("All dependencies found.")
    return True


def run_tests() -> bool:
    """
    Run the tests with proper output formatting.
    """
    print("\n" + "=" * 50)
    print("Running Flask Job Tracker Tests")
    print("=" * 50)

    try:
        cmd: List[str] = [
            sys.executable,
            "-m",
            "pytest",
            TEST_FILE,
            "-v",
            "--tb=short",
            "--color=yes",
        ]

        print(f"Executing command: {' '.join(cmd)}")
        result: subprocess.CompletedProcess[str] = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )

        if result.stdout:
            print(result.stdout.strip())

        if result.stderr:
            print("\nTest Process Warnings/Errors:")
            print("-" * 50)
            print(result.stderr.strip())
            print("-" * 50)

        if result.returncode == 0:
            return True
        else:
            print("\n" + "=" * 50)
            print("Some tests failed!")
            print(f"Pytest exited with code: {result.returncode}")
            print("Please review the output above for details.")
            print("=" * 50)
            return False

    except FileNotFoundError:
        print("Error: Could not execute pytest.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while trying to run tests: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> None:
    """Main function to run the tests."""
    print("Flask Job Tracker - Testing")
    print("=" * 10 + "\n")

    if not check_test_dependencies():
        sys.exit(1)

    if not check_required_files():
        print("\nAborting tests due to missing files or configuration.")
        sys.exit(1)

    success: bool = run_tests()

    if success:
        print("\nTests completed successfully!")
        sys.exit(0)
    else:
        print("\nTests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
