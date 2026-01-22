"""
Redesigned Test Script for Phase 2: Transaction Receipt Generation
This script focuses solely on testing the receipt generation functionality.
"""

import requests
import os

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print(" "*20 + "PHASE 2 RECEIPT TEST")
print("="*80)

# Test: Receipt Generation Endpoint
print("\n✅ Test: Receipt Generation")
try:
    payload = {
        "transaction_id": 12345,
        "user_id": 1,
        "amount": 500,
        "currency": "USD",
        "recipient": "John Doe"
    }
    response = requests.post(
        f"{BASE_URL}/api/receipt",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        receipt_url = data.get("receipt_url")
        if receipt_url:
            print(f"   ✅ Receipt generated successfully: {receipt_url}")
            # Optionally, download the receipt to verify its content
            receipt_response = requests.get(receipt_url, timeout=10)
            if receipt_response.status_code == 200:
                with open("test_receipt.pdf", "wb") as f:
                    f.write(receipt_response.content)
                print("   ✅ Receipt downloaded and saved as 'test_receipt.pdf'")
            else:
                print(f"   ❌ Failed to download receipt: {receipt_response.status_code}")
        else:
            print("   ❌ Receipt URL not found in response.")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("🎉 PHASE 2 RECEIPT TEST COMPLETE")
print("="*80 + "\n")