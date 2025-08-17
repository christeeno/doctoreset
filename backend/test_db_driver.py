import unittest
import tempfile
import os
from datetime import datetime
from db_driver import DatabaseDriver, Patient


class TestPatientModel(unittest.TestCase):
    """Test cases for the Patient data model"""
    
    def test_patient_creation(self):
        """Test Patient dataclass creation and attributes"""
        patient = Patient(
            patient_id="P12345678",
            name="John Doe",
            age=30,
            height=175.5,
            gender="Male",
            blood_group="O+",
            weight=70.0,
            created_at=datetime.now()
        )
        
        self.assertEqual(patient.patient_id, "P12345678")
        self.assertEqual(patient.name, "John Doe")
        self.assertEqual(patient.age, 30)
        self.assertEqual(patient.height, 175.5)
        self.assertEqual(patient.gender, "Male")
        self.assertEqual(patient.blood_group, "O+")
        self.assertEqual(patient.weight, 70.0)
        self.assertIsInstance(patient.created_at, datetime)
    
    def test_patient_creation_without_timestamp(self):
        """Test Patient creation without created_at timestamp"""
        patient = Patient(
            patient_id="P87654321",
            name="Jane Smith",
            age=25,
            height=165.0,
            gender="Female",
            blood_group="A-",
            weight=60.0
        )
        
        self.assertEqual(patient.patient_id, "P87654321")
        self.assertEqual(patient.name, "Jane Smith")
        self.assertIsNone(patient.created_at)


class TestDatabaseDriver(unittest.TestCase):
    """Test cases for DatabaseDriver operations"""
    
    def setUp(self):
        """Set up test database with temporary file"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()
        self.db_driver = DatabaseDriver(self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database file"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test that database and patients table are created properly"""
        # Database should be initialized in setUp
        self.assertTrue(os.path.exists(self.temp_db.name))
        
        # Test that we can connect and query the table structure
        with self.db_driver._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'patients')
    
    def test_patient_id_generation(self):
        """Test patient ID generation uniqueness and format"""
        # Generate multiple patient IDs
        ids = set()
        for _ in range(100):
            patient_id = self.db_driver._generate_patient_id()
            self.assertTrue(patient_id.startswith('P'))
            self.assertEqual(len(patient_id), 9)  # P + 8 digits
            self.assertTrue(patient_id[1:].isdigit())
            ids.add(patient_id)
        
        # All IDs should be unique
        self.assertEqual(len(ids), 100)
    
    def test_create_patient_with_auto_id(self):
        """Test creating a patient with auto-generated ID"""
        patient = self.db_driver.create_patient(
            name="Alice Johnson",
            age=28,
            height=170.0,
            gender="Female",
            blood_group="B+",
            weight=65.0
        )
        
        self.assertIsNotNone(patient)
        self.assertTrue(patient.patient_id.startswith('P'))
        self.assertEqual(len(patient.patient_id), 9)
        self.assertEqual(patient.name, "Alice Johnson")
        self.assertEqual(patient.age, 28)
        self.assertEqual(patient.height, 170.0)
        self.assertEqual(patient.gender, "Female")
        self.assertEqual(patient.blood_group, "B+")
        self.assertEqual(patient.weight, 65.0)
        self.assertIsNotNone(patient.created_at)
    
    def test_create_patient_with_custom_id(self):
        """Test creating a patient with custom patient ID"""
        custom_id = "P99999999"
        patient = self.db_driver.create_patient(
            name="Bob Wilson",
            age=35,
            height=180.0,
            gender="Male",
            blood_group="AB-",
            weight=80.0,
            patient_id=custom_id
        )
        
        self.assertIsNotNone(patient)
        self.assertEqual(patient.patient_id, custom_id)
        self.assertEqual(patient.name, "Bob Wilson")
    
    def test_get_patient_by_id_existing(self):
        """Test retrieving an existing patient by ID"""
        # First create a patient
        created_patient = self.db_driver.create_patient(
            name="Charlie Brown",
            age=40,
            height=175.0,
            gender="Male",
            blood_group="O-",
            weight=75.0
        )
        
        # Then retrieve it
        retrieved_patient = self.db_driver.get_patient_by_id(created_patient.patient_id)
        
        self.assertIsNotNone(retrieved_patient)
        self.assertEqual(retrieved_patient.patient_id, created_patient.patient_id)
        self.assertEqual(retrieved_patient.name, "Charlie Brown")
        self.assertEqual(retrieved_patient.age, 40)
        self.assertEqual(retrieved_patient.height, 175.0)
        self.assertEqual(retrieved_patient.gender, "Male")
        self.assertEqual(retrieved_patient.blood_group, "O-")
        self.assertEqual(retrieved_patient.weight, 75.0)
        self.assertIsNotNone(retrieved_patient.created_at)
    
    def test_get_patient_by_id_nonexistent(self):
        """Test retrieving a non-existent patient by ID"""
        result = self.db_driver.get_patient_by_id("P00000000")
        self.assertIsNone(result)
    
    def test_patient_id_uniqueness_constraint(self):
        """Test that duplicate patient IDs are handled properly"""
        custom_id = "P11111111"
        
        # Create first patient
        patient1 = self.db_driver.create_patient(
            name="First Patient",
            age=25,
            height=160.0,
            gender="Female",
            blood_group="A+",
            weight=55.0,
            patient_id=custom_id
        )
        self.assertIsNotNone(patient1)
        
        # Attempt to create second patient with same ID should raise an exception
        with self.assertRaises(Exception):  # SQLite will raise IntegrityError
            self.db_driver.create_patient(
                name="Second Patient",
                age=30,
                height=170.0,
                gender="Male",
                blood_group="B+",
                weight=70.0,
                patient_id=custom_id
            )
    
    def test_database_crud_operations(self):
        """Test complete CRUD operations for patients"""
        # CREATE
        patient = self.db_driver.create_patient(
            name="CRUD Test Patient",
            age=33,
            height=168.0,
            gender="Female",
            blood_group="AB+",
            weight=62.0
        )
        self.assertIsNotNone(patient)
        patient_id = patient.patient_id
        
        # READ
        retrieved = self.db_driver.get_patient_by_id(patient_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "CRUD Test Patient")
        
        # UPDATE (Note: Current implementation doesn't have update method, 
        # but we can test that the data persists correctly)
        retrieved_again = self.db_driver.get_patient_by_id(patient_id)
        self.assertEqual(retrieved_again.patient_id, patient_id)
        
        # DELETE (Note: Current implementation doesn't have delete method,
        # but we can verify the patient exists in database)
        with self.db_driver._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id = ?", (patient_id,))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)
    
    def test_multiple_patients_creation(self):
        """Test creating multiple patients and ensuring they all have unique IDs"""
        patients = []
        patient_ids = set()
        
        for i in range(10):
            patient = self.db_driver.create_patient(
                name=f"Patient {i}",
                age=20 + i,
                height=160.0 + i,
                gender="Male" if i % 2 == 0 else "Female",
                blood_group="O+",
                weight=60.0 + i
            )
            patients.append(patient)
            patient_ids.add(patient.patient_id)
        
        # All patients should be created successfully
        self.assertEqual(len(patients), 10)
        
        # All patient IDs should be unique
        self.assertEqual(len(patient_ids), 10)
        
        # All patients should be retrievable
        for patient in patients:
            retrieved = self.db_driver.get_patient_by_id(patient.patient_id)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.patient_id, patient.patient_id)


if __name__ == '__main__':
    unittest.main()