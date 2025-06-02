#!/usr/bin/env python3
"""
Test script for microservices communication.
This script tests the communication between all services.
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Service URLs
AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
HISTORY_URL = os.getenv("HISTORY_SERVICE_URL", "http://localhost:8002")
ELI5_URL = os.getenv("ELI5_SERVICE_URL", "http://localhost:8000")

# Test user data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
}


async def test_service_health():
    """Test health endpoints of all services."""
    print("🔍 Testing service health...")

    services = [
        (AUTH_URL, "/auth/health", "Auth Service"),
        (HISTORY_URL, "/history/health", "History Service"),
        (ELI5_URL, "/docs", "ELI5 Service"),  # ELI5 doesn't have health endpoint yet
    ]

    async with httpx.AsyncClient() as client:
        for base_url, endpoint, name in services:
            try:
                response = await client.get(f"{base_url}{endpoint}", timeout=5.0)
                if response.status_code == 200:
                    print(f"✅ {name} is healthy")
                else:
                    print(f"⚠️ {name} returned status {response.status_code}")
            except Exception as e:
                print(f"❌ {name} is not accessible: {str(e)}")


async def test_user_registration():
    """Test user registration through ELI5 service."""
    print("\\n👤 Testing user registration...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ELI5_URL}/api/auth/signup", json=TEST_USER, timeout=10.0
            )

            if response.status_code == 200:
                print("✅ User registration successful")
                return True
            elif response.status_code == 400:
                print("⚠️ User already exists (this is normal for repeated tests)")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ User registration error: {str(e)}")
            return False


async def test_user_login():
    """Test user login and return access token."""
    print("\\n🔑 Testing user login...")

    async with httpx.AsyncClient() as client:
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
            }

            response = await client.post(
                f"{ELI5_URL}/api/auth/login", json=login_data, timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print("✅ User login successful")
                print(f"🎫 Token received: {token[:20]}...")
                return token
            else:
                print(f"❌ User login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ User login error: {str(e)}")
            return None


async def test_authenticated_explanation(token):
    """Test authenticated concept explanation."""
    print("\\n🧠 Testing authenticated concept explanation...")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.get(
                f"{ELI5_URL}/api/explain/authenticated",
                headers=headers,
                timeout=30.0,  # AI generation can take time
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Authenticated explanation successful")
                print(f"📚 Concept: {data.get('concept')}")
                print(f"💾 Saved to history: {data.get('saved_to_history')}")
                return True
            else:
                print(f"❌ Authenticated explanation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Authenticated explanation error: {str(e)}")
            return False


async def test_public_explanation():
    """Test public concept explanation."""
    print("\\n🌐 Testing public concept explanation...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{ELI5_URL}/api/explain",
                timeout=30.0,  # AI generation can take time
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Public explanation successful")
                print(f"📚 Concept: {data.get('concept')}")
                return True
            else:
                print(f"❌ Public explanation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Public explanation error: {str(e)}")
            return False


async def test_user_history(token):
    """Test retrieving user history."""
    print("\\n📜 Testing user history retrieval...")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.get(
                f"{ELI5_URL}/api/history", headers=headers, timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                history = data.get("history", [])
                print("✅ User history retrieval successful")
                print(f"📊 History entries: {len(history)}")
                return True
            else:
                print(f"❌ User history retrieval failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ User history retrieval error: {str(e)}")
            return False


async def main():
    """Run all microservice communication tests."""
    print("🚀 Starting Microservices Communication Tests")
    print("=" * 50)

    # Test 1: Service Health
    await test_service_health()

    # Test 2: User Registration
    registration_success = await test_user_registration()
    if not registration_success:
        print("\\n❌ Stopping tests due to registration failure")
        return

    # Test 3: User Login
    token = await test_user_login()
    if not token:
        print("\\n❌ Stopping tests due to login failure")
        return

    # Test 4: Public Explanation (no auth required)
    await test_public_explanation()

    # Test 5: Authenticated Explanation
    auth_explanation_success = await test_authenticated_explanation(token)

    # Test 6: User History (only if authenticated explanation worked)
    if auth_explanation_success:
        await test_user_history(token)

    print("\\n" + "=" * 50)
    print("🎉 Microservices communication tests completed!")
    print("\\n📋 Test Summary:")
    print("- Service health checks")
    print("- User registration via ELI5 service → Auth service")
    print("- User login via ELI5 service → Auth service")
    print("- Public concept explanation (ELI5 service only)")
    print("- Authenticated explanation (ELI5 → Auth → History)")
    print("- User history retrieval (ELI5 → History → Auth)")


if __name__ == "__main__":
    asyncio.run(main())
