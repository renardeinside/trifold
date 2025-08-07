"""
Performance testing for Trifold API desserts CRUD operations using Locust.

This test suite performs load testing on the desserts API endpoints:
- GET /api/desserts (list desserts)
- POST /api/desserts (create dessert)
- PUT /api/desserts/{id} (update dessert)
- DELETE /api/desserts/{id} (delete dessert)

Usage:
    locust -f ops/locust_test.py --host=http://localhost:8080

Example with specific users and spawn rate:
    locust -f ops/locust_test.py --host=http://localhost:8080 -u 10 -r 2
"""

import random
import json
from typing import Dict, List
from locust import HttpUser, task, between
from databricks.sdk import WorkspaceClient
from locust.clients import ResponseContextManager


def get_auth_headers() -> dict[str, str]:
    """Returns dict of format {'Authorization': 'Bearer <token>'}"""
    ws = WorkspaceClient()
    return ws.config.authenticate()


try:
    auth_headers = get_auth_headers()
except Exception as e:
    print(f"Error getting auth headers: {e} - using empty headers")
    auth_headers = {}


class DessertAPIUser(HttpUser):
    """
    A Locust user that simulates API interactions with the desserts endpoints.

    This user performs realistic CRUD operations with proper data management:
    - Creates desserts that can be later updated/deleted
    - Maintains a local cache of created dessert IDs
    - Uses realistic test data with variations
    - Uses authenticated requests via Databricks SDK
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize user state when starting."""
        self.created_desserts: List[int] = []
        self.test_desserts = self._get_test_dessert_data()

    def _get_test_dessert_data(self) -> List[Dict]:
        """Generate realistic test data for desserts."""
        return [
            {
                "name": "Chocolate Lava Cake",
                "price": 8.99,
                "description": "Rich chocolate cake with molten center",
                "leftInStock": random.randint(5, 20),
            },
            {
                "name": "Tiramisu",
                "price": 7.50,
                "description": "Classic Italian coffee-flavored dessert",
                "leftInStock": random.randint(3, 15),
            },
            {
                "name": "Crème Brûlée",
                "price": 9.25,
                "description": "Vanilla custard with caramelized sugar top",
                "leftInStock": random.randint(4, 12),
            },
            {
                "name": "Apple Pie",
                "price": 6.75,
                "description": "Traditional apple pie with cinnamon",
                "leftInStock": random.randint(8, 25),
            },
            {
                "name": "Cheesecake",
                "price": 8.50,
                "description": "New York style cheesecake with berry sauce",
                "leftInStock": random.randint(6, 18),
            },
            {
                "name": "Ice Cream Sundae",
                "price": 5.99,
                "description": "Vanilla ice cream with hot fudge and nuts",
                "leftInStock": random.randint(10, 30),
            },
        ]

    @task(3)
    def list_desserts(self):
        """
        Test GET /api/desserts endpoint.
        This is weighted higher (3) as listing is typically the most common operation.
        """
        with self.client.get(
            "/api/desserts", headers=auth_headers, catch_response=True
        ) as response:
            assert isinstance(response, ResponseContextManager)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure(f"Expected list, got {type(data)}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def create_dessert(self):
        """
        Test POST /api/desserts endpoint.
        Creates a new dessert and stores its ID for later operations.
        """
        dessert_data = random.choice(self.test_desserts).copy()

        # Add randomization to make each request unique
        dessert_data["name"] = f"{dessert_data['name']} #{random.randint(1000, 9999)}"
        dessert_data["leftInStock"] = random.randint(1, 50)

        headers = {**auth_headers, "Content-Type": "application/json"}
        with self.client.post(
            "/api/desserts",
            json=dessert_data,
            headers=headers,
            catch_response=True,
        ) as response:
            assert isinstance(response, ResponseContextManager)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "id" in data:
                        self.created_desserts.append(data["id"])
                        response.success()
                    else:
                        response.failure("No ID in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def update_dessert(self):
        """
        Test PUT /api/desserts/{id} endpoint.
        Updates a previously created dessert.
        """
        if not self.created_desserts:
            return  # Skip if no desserts to update

        dessert_id = random.choice(self.created_desserts)
        updated_data = random.choice(self.test_desserts).copy()

        # Modify data to simulate updates
        updated_data["name"] = f"Updated {updated_data['name']}"
        updated_data["price"] = round(
            updated_data["price"] * random.uniform(0.8, 1.2), 2
        )
        updated_data["leftInStock"] = random.randint(0, 100)

        headers = {**auth_headers, "Content-Type": "application/json"}
        with self.client.put(
            f"/api/desserts/{dessert_id}",
            json=updated_data,
            headers=headers,
            catch_response=True,
            name="/api/desserts/{id}",  # Group all PUT requests under this name
        ) as response:
            assert isinstance(response, ResponseContextManager)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("id") == dessert_id:
                        response.success()
                    else:
                        response.failure("ID mismatch in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Remove from our list if it was deleted by another user
                if dessert_id in self.created_desserts:
                    self.created_desserts.remove(dessert_id)
                response.failure("Dessert not found")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def delete_dessert(self):
        """
        Test DELETE /api/desserts/{id} endpoint.
        Deletes a previously created dessert.
        """
        if not self.created_desserts:
            return  # Skip if no desserts to delete

        dessert_id = self.created_desserts.pop(
            random.randint(0, len(self.created_desserts) - 1)
        )
        with self.client.delete(
            f"/api/desserts/{dessert_id}",
            headers=auth_headers,
            catch_response=True,
            name="/api/desserts/{id}",  # Group all DELETE requests under this name
        ) as response:
            assert isinstance(response, ResponseContextManager)
            if response.status_code == 204:
                response.success()
            elif response.status_code == 404:
                response.failure("Dessert not found")
            else:
                response.failure(f"HTTP {response.status_code}")


class HighVolumeUser(HttpUser):
    """
    A more aggressive user for stress testing.
    This user focuses on high-frequency read operations with occasional writes.
    Uses authenticated requests via Databricks SDK.
    """

    wait_time = between(0.1, 0.5)  # Very short wait times for stress testing

    @task(10)
    def rapid_list_desserts(self):
        """Rapid-fire dessert listing for stress testing."""
        self.client.get("/api/desserts", headers=auth_headers)

    @task(1)
    def quick_create(self):
        """Quick dessert creation."""
        dessert_data = {
            "name": f"Stress Test Dessert {random.randint(1, 10000)}",
            "price": round(random.uniform(5.0, 15.0), 2),
            "description": "Generated for stress testing",
            "leftInStock": random.randint(1, 100),
        }

        headers = {**auth_headers, "Content-Type": "application/json"}
        self.client.post(
            "/api/desserts",
            json=dessert_data,
            headers=headers,
        )


# Configuration for different test scenarios
class TestScenarios:
    """
    Different test configurations for various performance testing scenarios.
    """

    @staticmethod
    def normal_load():
        """
        Normal load test configuration.
        Use: locust -f ops/locust_test.py --host=http://localhost:8080 -u 5 -r 1
        """
        return {"users": 5, "spawn_rate": 1, "run_time": "5m"}

    @staticmethod
    def stress_test():
        """
        Stress test configuration.
        Use: locust -f ops/locust_test.py --host=http://localhost:8080 -u 50 -r 5
        """
        return {"users": 50, "spawn_rate": 5, "run_time": "10m"}

    @staticmethod
    def spike_test():
        """
        Spike test configuration.
        Use: locust -f ops/locust_test.py --host=http://localhost:8080 -u 100 -r 10
        """
        return {"users": 100, "spawn_rate": 10, "run_time": "2m"}


if __name__ == "__main__":
    print(
        """
    Trifold API Performance Test Suite
    =================================
    
    This script tests the performance of desserts CRUD operations.
    
    Basic usage:
        locust -f ops/locust_test.py --host=http://localhost:8080
    
    Test scenarios:
        Normal Load:  locust -f ops/locust_test.py --host=http://localhost:8080 -u 5 -r 1 -t 5m
        Stress Test:  locust -f ops/locust_test.py --host=http://localhost:8080 -u 50 -r 5 -t 10m
        Spike Test:   locust -f ops/locust_test.py --host=http://localhost:8080 -u 100 -r 10 -t 2m
    
    Parameters:
        -u: Number of concurrent users
        -r: Spawn rate (users per second)
        -t: Test duration
        --headless: Run without web UI
        --csv: Save results to CSV files
    
    Example with CSV output:
        locust -f ops/locust_test.py --host=http://localhost:8080 -u 10 -r 2 -t 3m --headless --csv=results
    """
    )
