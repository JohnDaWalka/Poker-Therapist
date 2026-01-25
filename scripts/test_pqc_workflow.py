#!/usr/bin/env python3
"""
Test script to validate PQC workflow configuration

This script performs pre-flight checks on the PQC signing workflow
to ensure it's properly configured and ready to run.

Usage:
    python scripts/test_pqc_workflow.py
"""

import sys
import yaml
from pathlib import Path


def print_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if details and not passed:
        print(f"  → {details}")


def test_workflow_exists() -> bool:
    """Test that workflow file exists"""
    workflow_path = Path(".github/workflows/pqc-artifact-signing.yml")
    return workflow_path.exists()


def test_workflow_yaml_valid() -> tuple[bool, str]:
    """Test that workflow YAML is valid"""
    workflow_path = Path(".github/workflows/pqc-artifact-signing.yml")
    try:
        with open(workflow_path) as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)


def test_workflow_triggers() -> tuple[bool, str]:
    """Test that workflow has correct triggers"""
    workflow_path = Path(".github/workflows/pqc-artifact-signing.yml")
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    # YAML parses "on" as boolean True, so check for True key
    if "on" not in workflow and True not in workflow:
        return False, "No triggers defined"

    triggers = workflow.get("on", workflow.get(True, {}))

    has_release = "release" in triggers
    has_dispatch = "workflow_dispatch" in triggers

    if not has_release:
        return False, "Missing 'release' trigger"
    if not has_dispatch:
        return False, "Missing 'workflow_dispatch' trigger"

    return True, ""


def test_documentation_exists() -> tuple[bool, str]:
    """Test that documentation files exist"""
    docs = [
        "PQC_SIGNING.md",
        "PQC_QUICKSTART.md",
        "PQC_SECURITY.md"
    ]

    missing = []
    for doc in docs:
        if not Path(doc).exists():
            missing.append(doc)

    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, ""


def test_verification_script() -> tuple[bool, str]:
    """Test that verification script exists and is executable"""
    script_path = Path("scripts/verify_pqc_signatures.py")

    if not script_path.exists():
        return False, "Script not found"

    # Check if executable (on Unix-like systems)
    import os
    if hasattr(os, 'access'):
        if not os.access(script_path, os.X_OK):
            return False, "Script not executable"

    return True, ""


def test_readme_updated() -> tuple[bool, str]:
    """Test that README mentions PQC signing"""
    readme_path = Path("README.md")

    if not readme_path.exists():
        return False, "README.md not found"

    content = readme_path.read_text()

    keywords = [
        "post-quantum",
        "Dilithium",
        "PQC_SIGNING.md"
    ]

    missing = []
    for keyword in keywords:
        if keyword.lower() not in content.lower():
            missing.append(keyword)

    if missing:
        return False, f"Missing keywords: {', '.join(missing)}"

    return True, ""


def test_workflow_jobs() -> tuple[bool, str]:
    """Test that workflow has required jobs"""
    workflow_path = Path(".github/workflows/pqc-artifact-signing.yml")
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    if "jobs" not in workflow:
        return False, "No jobs defined"

    jobs = workflow["jobs"]

    if "pqc-sign-artifacts" not in jobs:
        return False, "Missing 'pqc-sign-artifacts' job"

    job = jobs["pqc-sign-artifacts"]

    if "steps" not in job:
        return False, "Job has no steps"

    steps = job["steps"]
    step_names = [step.get("name", "") for step in steps]

    required_steps = [
        "Build liboqs",
        "Build OpenSSL",
        "Build oqs-provider",
        "Generate Dilithium3 keypair",
        "Sign artifacts",
        "Verify signatures"
    ]

    missing_steps = []
    for required in required_steps:
        if not any(required.lower() in name.lower() for name in step_names):
            missing_steps.append(required)

    if missing_steps:
        return False, f"Missing steps: {', '.join(missing_steps)}"

    return True, ""


def main() -> int:
    """Run all tests"""
    print("=" * 70)
    print("PQC Workflow Configuration Tests")
    print("=" * 70)
    print()

    all_passed = True

    # Test 1: Workflow exists
    passed = test_workflow_exists()
    print_result("Workflow file exists", passed)
    all_passed &= passed

    if not passed:
        print("\n✗ Cannot continue - workflow file not found")
        return 1

    # Test 2: YAML validity
    passed, details = test_workflow_yaml_valid()
    print_result("Workflow YAML is valid", passed, details)
    all_passed &= passed

    # Test 3: Workflow triggers
    passed, details = test_workflow_triggers()
    print_result("Workflow triggers configured", passed, details)
    all_passed &= passed

    # Test 4: Workflow jobs
    passed, details = test_workflow_jobs()
    print_result("Workflow jobs configured", passed, details)
    all_passed &= passed

    # Test 5: Documentation
    passed, details = test_documentation_exists()
    print_result("Documentation files exist", passed, details)
    all_passed &= passed

    # Test 6: Verification script
    passed, details = test_verification_script()
    print_result("Verification script ready", passed, details)
    all_passed &= passed

    # Test 7: README
    passed, details = test_readme_updated()
    print_result("README updated", passed, details)
    all_passed &= passed

    print()
    print("=" * 70)

    if all_passed:
        print("✓ All tests passed! Workflow is ready to use.")
        print()
        print("Next steps:")
        print("1. Push changes to GitHub")
        print("2. Go to Actions > Post-Quantum Artifact Signing")
        print("3. Click 'Run workflow' to test")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
