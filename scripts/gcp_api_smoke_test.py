#!/usr/bin/env python3
"""
GCP API Smoke Test Script

This script authenticates to Google Cloud Platform and runs minimal smoke tests
(read-only checks) for enabled services in the project.
"""

import json
import os
import sys
from typing import Dict, List, Tuple

from google.auth import default
from google.cloud import bigquery, pubsub_v1, secretmanager, storage
from googleapiclient.discovery import build


class GCPSmokeTest:
    """GCP API Smoke Test Runner"""

    def __init__(self, project_id: str = None):
        """Initialize the smoke test runner.

        Args:
            project_id: GCP project ID. If None, will be detected from environment.
        """
        self.project_id = project_id
        self.credentials = None
        self.enabled_services = []
        self.test_results = {}
        self.mapping_file = os.path.join(
            os.path.dirname(__file__), "gcp_api_mapping.json"
        )

    def authenticate(self) -> bool:
        """Authenticate to GCP and detect project ID.

        Returns:
            bool: True if authentication successful, False otherwise.
        """
        try:
            self.credentials, detected_project = default()
            if not self.project_id:
                self.project_id = detected_project

            if not self.project_id:
                print("ERROR: Unable to detect GCP project ID")
                return False

            print(f"✓ Authenticated to GCP project: {self.project_id}")
            return True
        except Exception as e:
            print(f"ERROR: Authentication failed: {e}")
            return False

    def load_service_mapping(self) -> Dict:
        """Load service mapping from JSON file.

        Returns:
            Dict: Service mapping dictionary.
        """
        try:
            with open(self.mapping_file, "r") as f:
                mapping = json.load(f)
            return mapping.get("services", {})
        except FileNotFoundError:
            print(f"WARNING: Mapping file not found: {self.mapping_file}")
            return {}
        except Exception as e:
            print(f"WARNING: Failed to load mapping file: {e}")
            return {}

    def get_enabled_services(self) -> List[str]:
        """Retrieve list of enabled services in the project.

        Returns:
            List[str]: List of enabled service names.
        """
        try:
            service = build("serviceusage", "v1", credentials=self.credentials)
            request = service.services().list(
                parent=f"projects/{self.project_id}",
                filter="state:ENABLED",
                pageSize=200,
            )

            enabled = []
            while request is not None:
                response = request.execute()
                services = response.get("services", [])
                for svc in services:
                    service_name = svc.get("config", {}).get("name", "")
                    if service_name:
                        enabled.append(service_name)

                request = service.services().list_next(request, response)

            self.enabled_services = enabled
            print(f"✓ Found {len(enabled)} enabled services")
            return enabled
        except Exception as e:
            print(f"ERROR: Failed to list enabled services: {e}")
            return []

    def test_storage(self) -> Tuple[bool, str]:
        """Test Cloud Storage API with read-only check.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            client = storage.Client(
                project=self.project_id, credentials=self.credentials
            )
            # List buckets (read-only operation)
            buckets = list(client.list_buckets(max_results=1))
            return True, f"Successfully listed buckets (found {len(buckets)})"
        except Exception as e:
            return False, f"Failed to list buckets: {str(e)}"

    def test_pubsub(self) -> Tuple[bool, str]:
        """Test Pub/Sub API with read-only check.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            publisher = pubsub_v1.PublisherClient(credentials=self.credentials)
            project_path = f"projects/{self.project_id}"
            # List topics (read-only operation)
            topics = list(publisher.list_topics(request={"project": project_path}))
            return True, f"Successfully listed topics (found {len(topics)})"
        except Exception as e:
            return False, f"Failed to list topics: {str(e)}"

    def test_secret_manager(self) -> Tuple[bool, str]:
        """Test Secret Manager API with read-only check.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            client = secretmanager.SecretManagerServiceClient(
                credentials=self.credentials
            )
            parent = f"projects/{self.project_id}"
            # List secrets (read-only operation)
            secrets = list(client.list_secrets(request={"parent": parent}))
            return True, f"Successfully listed secrets (found {len(secrets)})"
        except Exception as e:
            return False, f"Failed to list secrets: {str(e)}"

    def test_compute(self) -> Tuple[bool, str]:
        """Test Compute Engine API with read-only check.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            service = build("compute", "v1", credentials=self.credentials)
            # List zones (read-only operation)
            request = service.zones().list(project=self.project_id, maxResults=5)
            response = request.execute()
            zones = response.get("items", [])
            return True, f"Successfully listed zones (found {len(zones)})"
        except Exception as e:
            return False, f"Failed to list zones: {str(e)}"

    def test_bigquery(self) -> Tuple[bool, str]:
        """Test BigQuery API with read-only check.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            client = bigquery.Client(
                project=self.project_id, credentials=self.credentials
            )
            # List datasets (read-only operation)
            datasets = list(client.list_datasets(max_results=10))
            return True, f"Successfully listed datasets (found {len(datasets)})"
        except Exception as e:
            return False, f"Failed to list datasets: {str(e)}"

    def run_smoke_tests(self) -> bool:
        """Run smoke tests for all enabled and mapped services.

        Returns:
            bool: True if all tests passed, False if any failed.
        """
        service_mapping = self.load_service_mapping()
        if not service_mapping:
            print("ERROR: No service mapping available")
            return False

        print("\n" + "=" * 60)
        print("Running Smoke Tests")
        print("=" * 60)

        all_passed = True
        tested_count = 0

        for service_name in self.enabled_services:
            if service_name in service_mapping:
                service_info = service_mapping[service_name]
                friendly_name = service_info["friendly_name"]
                test_function_name = service_info["test_function"]

                print(f"\nTesting: {friendly_name} ({service_name})")

                # Get test function
                test_function = getattr(self, test_function_name, None)
                if test_function:
                    try:
                        success, message = test_function()
                        self.test_results[service_name] = {
                            "success": success,
                            "message": message,
                        }

                        if success:
                            print(f"  ✓ PASS: {message}")
                        else:
                            print(f"  ✗ FAIL: {message}")
                            all_passed = False

                        tested_count += 1
                    except Exception as e:
                        error_msg = f"Test execution error: {str(e)}"
                        print(f"  ✗ FAIL: {error_msg}")
                        self.test_results[service_name] = {
                            "success": False,
                            "message": error_msg,
                        }
                        all_passed = False
                        tested_count += 1
                else:
                    print(f"  ⚠ SKIP: Test function '{test_function_name}' not found")

        print("\n" + "=" * 60)
        print(f"Test Summary: {tested_count} tests run")
        print("=" * 60)

        if tested_count == 0:
            print("⚠ WARNING: No services were tested")
            return False

        return all_passed

    def print_summary(self) -> None:
        """Print test results summary."""
        passed = sum(1 for r in self.test_results.values() if r["success"])
        failed = len(self.test_results) - passed

        print(f"\n✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for service, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {service}: {result['message']}")


def main():
    """Main entry point for the smoke test script."""
    # Get project ID from environment or argument
    project_id = os.environ.get("GCP_PROJECT_ID")
    if len(sys.argv) > 1:
        project_id = sys.argv[1]

    print("GCP API Smoke Test")
    print("=" * 60)

    # Initialize smoke test runner
    runner = GCPSmokeTest(project_id=project_id)

    # Authenticate
    if not runner.authenticate():
        sys.exit(1)

    # Get enabled services
    enabled_services = runner.get_enabled_services()
    if not enabled_services:
        print("ERROR: No enabled services found")
        sys.exit(1)

    # Run smoke tests
    all_passed = runner.run_smoke_tests()

    # Print summary
    runner.print_summary()

    # Exit with appropriate code
    if all_passed:
        print("\n✓ All smoke tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some smoke tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
