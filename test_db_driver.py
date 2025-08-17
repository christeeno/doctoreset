#!/usr/bin/env python3
"""Test script to verify the updated database driver functionality"""

from db_driver import DatabaseDriver, Patient
import os
import sys
sys.path.append('backend')


def test_patient_operations():
    # Use a test database
    test_db = "test_health_assistant.sqlite"

    # Clean up any existing test database
    if os.path.exists(test_db):
        os.remove(test_db)

    # Initialize database driver
    db = DatabaseDriver(test_db)

    print("Testing Patient database operations...")

    # Test 1: Create a patient with auto-generated ID
    print("\n1. Creating patient with auto-generated ID...")
    patient1 = db.create_patient(
        name="John Doe",
        age=35,
        height=175.5,
        gender="Male",
        blood_group="O+",
        weight=70.2
    )
    print(f"Created patient: {patient1}")

    # Test 2: Retrieve patient by ID
    print("\n2. Retrieving patient by ID...")
    retrieved_patient = db.get_patient_by_id(patient1.patient_id)
    print(f"Retrieved patient: {retrieved_patient}")

    # Test 3: Create patient with specific ID
    print("\n3. Creating patient with specific ID...")
    patient2 = db.create_patient(
        name="Jane Smith",
        age=28,
        height=165.0,
        gender="Female",
        blood_group="A-",
        weight=58.5,
        patient_id="P99999999"
    )
    print(f"Created patient with specific ID: {patient2}")

    # Test 4: Try to retrieve non-existent patient
    print("\n4. Testing non-existent patient lookup...")
    non_existent = db.get_patient_by_id("P00000000")
    print(f"Non-existent patient result: {non_existent}")

    # Test 5: Verify patient ID uniqueness
    print("\n5. Testing patient ID uniqueness...")
    patient3 = db.create_patient(
        name="Bob Johnson",
        age=42,
        height=180.0,
        gender="Male",
        blood_group="B+",
        weight=85.0
    )
    print(f"Third patient with unique ID: {patient3}")

    # Verify all IDs are different
    ids = [patient1.patient_id, patient2.patient_id, patient3.patient_id]
    print(f"All patient IDs: {ids}")
    print(f"All IDs are unique: {len(ids) == len(set(ids))}")

    # Clean up test database
    os.remove(test_db)
    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_patient_operations()
