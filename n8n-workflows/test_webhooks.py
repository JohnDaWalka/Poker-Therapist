#!/usr/bin/env python3
"""
Test script for n8n webhook integration.

This script demonstrates how to test the n8n webhook endpoints
without requiring the full backend dependencies.
"""

import json
import requests
import sys
from typing import Dict, Any


def test_endpoint(url: str, method: str = "GET", data: Dict[str, Any] = None) -> None:
    """Test a single endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            print(f"Payload:\n{json.dumps(data, indent=2)}")
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"Unsupported method: {method}")
            return
        
        print(f"\nStatus Code: {response.status_code}")
        
        # Try to parse JSON response
        try:
            json_response = response.json()
            print(f"Response:\n{json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response (non-JSON):\n{response.text}")
        
        if response.status_code < 400:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server")
        print("Make sure the FastAPI server is running:")
        print("  uvicorn backend.api.main:app --reload")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def main():
    """Run all tests."""
    base_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Testing n8n webhook integration at: {base_url}")
    
    # Test 1: Status endpoint
    test_endpoint(f"{base_url}/api/webhooks/n8n/status", "GET")
    
    # Test 2: Test endpoint
    test_endpoint(f"{base_url}/api/webhooks/n8n/test", "POST")
    
    # Test 3: Poker analysis webhook
    poker_analysis_payload = {
        "event_type": "poker_analysis",
        "user_id": "test_user_123",
        "email": "test@example.com",
        "data": {
            "hand_data": {
                "position": "BTN",
                "cards": ["As", "Kd"],
                "action": "raise",
                "pot_size": 100,
                "stack_size": 2000
            }
        }
    }
    test_endpoint(f"{base_url}/api/webhooks/n8n", "POST", poker_analysis_payload)
    
    # Test 4: Triage session webhook
    triage_payload = {
        "event_type": "triage_session",
        "user_id": "test_user_123",
        "email": "test@example.com",
        "data": {
            "session_data": {
                "tilt_level": 7,
                "trigger": "manual",
                "notes": "Feeling frustrated after bad beat"
            }
        }
    }
    test_endpoint(f"{base_url}/api/webhooks/n8n", "POST", triage_payload)
    
    # Test 5: Deep session webhook
    deep_session_payload = {
        "event_type": "deep_session",
        "user_id": "test_user_123",
        "email": "test@example.com",
        "data": {
            "session_data": {
                "topic": "mental_game",
                "duration_minutes": 60,
                "focus_areas": ["tilt_control", "decision_making"]
            }
        }
    }
    test_endpoint(f"{base_url}/api/webhooks/n8n", "POST", deep_session_payload)
    
    # Test 6: User notification webhook
    notification_payload = {
        "event_type": "user_notification",
        "user_id": "test_user_123",
        "email": "test@example.com",
        "data": {
            "notification": {
                "type": "reminder",
                "message": "Time for your daily poker session review!",
                "priority": "medium"
            }
        }
    }
    test_endpoint(f"{base_url}/api/webhooks/n8n", "POST", notification_payload)
    
    # Test 7: Custom event webhook
    custom_payload = {
        "event_type": "custom",
        "user_id": "test_user_123",
        "data": {
            "custom_action": "log_session",
            "session_info": {
                "hands_played": 150,
                "win_rate": 5.2,
                "duration_minutes": 120
            }
        }
    }
    test_endpoint(f"{base_url}/api/webhooks/n8n", "POST", custom_payload)
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
