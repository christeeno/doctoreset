import sqlite3
import random
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime

@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    height: float
    gender: str
    blood_group: str
    weight: float
    created_at: Optional[datetime] = None

class DatabaseDriver:
    def __init__(self, db_path: str = "health_assistant.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create patients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    height REAL NOT NULL,
                    gender TEXT NOT NULL,
                    blood_group TEXT NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _generate_patient_id(self) -> str:
        """Generate a unique patient ID in format P12345678"""
        while True:
            # Generate 8-digit random number
            random_number = random.randint(10000000, 99999999)
            patient_id = f"P{random_number}"
            
            # Check if ID already exists
            if not self.get_patient_by_id(patient_id):
                return patient_id

    def create_patient(self, name: str, age: int, height: float, gender: str, 
                      blood_group: str, weight: float, patient_id: Optional[str] = None) -> Patient:
        """Create a new patient with auto-generated ID if not provided"""
        if not patient_id:
            patient_id = self._generate_patient_id()
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO patients (patient_id, name, age, height, gender, blood_group, weight) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (patient_id, name, age, height, gender, blood_group, weight)
            )
            conn.commit()
            
            # Get the created patient with timestamp
            return self.get_patient_by_id(patient_id)

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient by their patient ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse the timestamp
            created_at = None
            if row[7]:  # created_at column
                try:
                    created_at = datetime.fromisoformat(row[7])
                except ValueError:
                    # Handle different timestamp formats if needed
                    created_at = None
            
            return Patient(
                patient_id=row[0],
                name=row[1],
                age=row[2],
                height=row[3],
                gender=row[4],
                blood_group=row[5],
                weight=row[6],
                created_at=created_at
            )
