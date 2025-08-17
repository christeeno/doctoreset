import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import sys

# Mock livekit.agents module before importing api
mock_llm = Mock()
mock_llm.FunctionContext = object  # Base class for HealthAssistantFnc
mock_llm.ai_callable = lambda description: lambda func: func  # Decorator that does nothing
mock_llm.TypeInfo = lambda description: str  # Simple type info mock

mock_agents = Mock()
mock_agents.llm = mock_llm

sys.modules['livekit'] = Mock()
sys.modules['livekit.agents'] = mock_agents
sys.modules['livekit.agents.llm'] = mock_llm

from api import HealthAssistantFnc, PatientDetails
from db_driver import DatabaseDriver, Patient
from report_generator import ReportGenerator


class TestHealthAssistantFunctions(unittest.TestCase):
    """Test cases for HealthAssistantFnc class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
        self.temp_db.close()
        
        # Create temporary reports directory
        self.temp_reports_dir = tempfile.mkdtemp()
        
        # Patch the global DB and REPORT_GEN objects
        self.db_patcher = patch('api.DB')
        self.report_gen_patcher = patch('api.REPORT_GEN')
        
        self.mock_db = self.db_patcher.start()
        self.mock_report_gen = self.report_gen_patcher.start()
        
        # Create real instances for testing
        self.real_db = DatabaseDriver(self.temp_db.name)
        self.real_report_gen = ReportGenerator(self.temp_reports_dir)
        
        # Configure mocks to use real instances
        self.mock_db.get_patient_by_id = self.real_db.get_patient_by_id
        self.mock_db.create_patient = self.real_db.create_patient
        self.mock_report_gen.generate_and_save_report = self.real_report_gen.generate_and_save_report
        
        # Create health assistant instance
        self.health_assistant = HealthAssistantFnc()
        
        # Create sample patient data
        self.sample_patient = self.real_db.create_patient(
            name="John Doe",
            age=30,
            height=175.5,
            gender="Male",
            blood_group="O+",
            weight=70.0
        )
    
    def tearDown(self):
        """Clean up test environment"""
        self.db_patcher.stop()
        self.report_gen_patcher.stop()
        
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        
        if os.path.exists(self.temp_reports_dir):
            shutil.rmtree(self.temp_reports_dir)
    
    def test_initial_state(self):
        """Test initial state of HealthAssistantFnc"""
        self.assertFalse(self.health_assistant.has_patient())
        self.assertFalse(self.health_assistant.is_consultation_complete())
        self.assertEqual(len(self.health_assistant._symptoms), 0)
        
        # Check that all patient details are empty initially
        for detail in PatientDetails:
            self.assertEqual(self.health_assistant._patient_details[detail], "")
    
    def test_lookup_patient_existing(self):
        """Test looking up an existing patient"""
        result = self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        
        self.assertIn("The patient details are:", result)
        self.assertTrue(self.health_assistant.has_patient())
        
        # Check that patient details are populated
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.PATIENT_ID], self.sample_patient.patient_id)
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.NAME], "John Doe")
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.AGE], 30)
    
    def test_lookup_patient_nonexistent(self):
        """Test looking up a non-existent patient"""
        result = self.health_assistant.lookup_patient("P00000000")
        
        self.assertEqual(result, "Patient not found")
        self.assertFalse(self.health_assistant.has_patient())
    
    def test_create_patient_success(self):
        """Test creating a new patient successfully"""
        result = self.health_assistant.create_patient(
            name="Jane Smith",
            age=25,
            height=165.0,
            gender="Female",
            blood_group="A-",
            weight=60.0
        )
        
        self.assertIn("Patient created! Your patient ID is:", result)
        self.assertTrue(self.health_assistant.has_patient())
        
        # Check that patient details are populated
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.NAME], "Jane Smith")
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.AGE], 25)
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.HEIGHT], 165.0)
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.GENDER], "Female")
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.BLOOD_GROUP], "A-")
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.WEIGHT], 60.0)
        
        # Patient ID should be generated and not empty
        self.assertNotEqual(self.health_assistant._patient_details[PatientDetails.PATIENT_ID], "")
    
    def test_create_patient_database_failure(self):
        """Test handling of database failure during patient creation"""
        # Mock database to return None (failure)
        with patch.object(self.real_db, 'create_patient', return_value=None):
            self.mock_db.create_patient = self.real_db.create_patient
            
            result = self.health_assistant.create_patient(
                name="Test Patient",
                age=30,
                height=170.0,
                gender="Male",
                blood_group="O+",
                weight=70.0
            )
            
            self.assertEqual(result, "Failed to create patient")
            self.assertFalse(self.health_assistant.has_patient())
    
    def test_get_patient_details_with_patient(self):
        """Test getting patient details when patient exists"""
        # First lookup a patient
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        
        result = self.health_assistant.get_patient_details()
        
        self.assertIn("The patient details are:", result)
        self.assertIn("patient_id: " + self.sample_patient.patient_id, result)
        self.assertIn("name: John Doe", result)
    
    def test_get_patient_details_no_patient(self):
        """Test getting patient details when no patient exists"""
        result = self.health_assistant.get_patient_details()
        
        # Should return empty details
        self.assertIn("The patient details are:", result)
        # Should not contain any actual patient information
        self.assertNotIn("John Doe", result)
    
    def test_add_symptom(self):
        """Test adding symptoms to the patient"""
        symptom1 = "Headache for 2 days"
        symptom2 = "Mild fever"
        
        result1 = self.health_assistant.add_symptom(symptom1)
        self.assertIn("Symptom added: Headache for 2 days", result1)
        self.assertIn("Total symptoms recorded: 1", result1)
        
        result2 = self.health_assistant.add_symptom(symptom2)
        self.assertIn("Symptom added: Mild fever", result2)
        self.assertIn("Total symptoms recorded: 2", result2)
        
        # Check internal state
        self.assertEqual(len(self.health_assistant._symptoms), 2)
        self.assertIn(symptom1, self.health_assistant._symptoms)
        self.assertIn(symptom2, self.health_assistant._symptoms)
    
    def test_get_symptoms_with_symptoms(self):
        """Test getting symptoms when symptoms exist"""
        # Add some symptoms first
        self.health_assistant.add_symptom("Headache")
        self.health_assistant.add_symptom("Fever")
        self.health_assistant.add_symptom("Fatigue")
        
        result = self.health_assistant.get_symptoms()
        
        self.assertIn("Recorded symptoms:", result)
        self.assertIn("1. Headache", result)
        self.assertIn("2. Fever", result)
        self.assertIn("3. Fatigue", result)
    
    def test_get_symptoms_no_symptoms(self):
        """Test getting symptoms when no symptoms exist"""
        result = self.health_assistant.get_symptoms()
        
        self.assertEqual(result, "No symptoms have been recorded yet.")
    
    def test_end_consultation_success(self):
        """Test successful consultation completion with report generation"""
        # Setup patient and symptoms
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        self.health_assistant.add_symptom("Headache")
        self.health_assistant.add_symptom("Fever")
        
        result = self.health_assistant.end_consultation()
        
        self.assertIn("Consultation complete!", result)
        self.assertIn("diagnostic report has been generated", result)
        self.assertTrue(self.health_assistant.is_consultation_complete())
        
        # Check that report was actually generated
        self.assertTrue(any("report.txt" in f for f in os.listdir(self.temp_reports_dir)))
    
    def test_end_consultation_no_patient(self):
        """Test ending consultation without patient information"""
        result = self.health_assistant.end_consultation()
        
        self.assertEqual(result, "Cannot end consultation: No patient information available.")
        self.assertFalse(self.health_assistant.is_consultation_complete())
    
    def test_end_consultation_report_generation_failure(self):
        """Test handling of report generation failure during consultation end"""
        # Setup patient
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        
        # Mock report generation to fail
        with patch.object(self.real_report_gen, 'generate_and_save_report', side_effect=Exception("File system error")):
            self.mock_report_gen.generate_and_save_report = self.real_report_gen.generate_and_save_report
            
            result = self.health_assistant.end_consultation()
            
            self.assertIn("Consultation marked as complete", result)
            self.assertIn("issue generating your report", result)
            self.assertIn("File system error", result)
            self.assertTrue(self.health_assistant.is_consultation_complete())
    
    def test_has_patient_true(self):
        """Test has_patient returns True when patient exists"""
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        self.assertTrue(self.health_assistant.has_patient())
    
    def test_has_patient_false(self):
        """Test has_patient returns False when no patient exists"""
        self.assertFalse(self.health_assistant.has_patient())
    
    def test_get_current_patient_success(self):
        """Test getting current patient as Patient object"""
        # Setup patient
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        
        current_patient = self.health_assistant.get_current_patient()
        
        self.assertIsInstance(current_patient, Patient)
        self.assertEqual(current_patient.patient_id, self.sample_patient.patient_id)
        self.assertEqual(current_patient.name, "John Doe")
        self.assertEqual(current_patient.age, 30)
        self.assertEqual(current_patient.height, 175.5)
        self.assertEqual(current_patient.gender, "Male")
        self.assertEqual(current_patient.blood_group, "O+")
        self.assertEqual(current_patient.weight, 70.0)
    
    def test_get_current_patient_no_patient(self):
        """Test getting current patient when no patient exists"""
        with self.assertRaises(ValueError) as context:
            self.health_assistant.get_current_patient()
        
        self.assertIn("No patient information available", str(context.exception))
    
    def test_get_patient_str_with_data(self):
        """Test patient string formatting with patient data"""
        # Setup patient
        self.health_assistant.lookup_patient(self.sample_patient.patient_id)
        
        patient_str = self.health_assistant.get_patient_str()
        
        self.assertIn("patient_id: " + self.sample_patient.patient_id, patient_str)
        self.assertIn("name: John Doe", patient_str)
        self.assertIn("age: 30", patient_str)
        self.assertIn("height: 175.5", patient_str)
        self.assertIn("gender: Male", patient_str)
        self.assertIn("blood_group: O+", patient_str)
        self.assertIn("weight: 70.0", patient_str)
    
    def test_get_patient_str_empty(self):
        """Test patient string formatting with no patient data"""
        patient_str = self.health_assistant.get_patient_str()
        
        # Should be empty or contain only empty values
        self.assertEqual(patient_str.strip(), "")
    
    def test_conversation_flow_integration(self):
        """Test complete conversation flow from patient creation to report generation"""
        # Step 1: Create patient
        create_result = self.health_assistant.create_patient(
            name="Integration Test Patient",
            age=35,
            height=180.0,
            gender="Male",
            blood_group="AB+",
            weight=75.0
        )
        self.assertIn("Patient created!", create_result)
        self.assertTrue(self.health_assistant.has_patient())
        
        # Step 2: Add symptoms
        self.health_assistant.add_symptom("Persistent cough")
        self.health_assistant.add_symptom("Shortness of breath")
        self.health_assistant.add_symptom("Chest pain")
        
        symptoms_result = self.health_assistant.get_symptoms()
        self.assertIn("3. Chest pain", symptoms_result)
        
        # Step 3: End consultation and generate report
        end_result = self.health_assistant.end_consultation()
        self.assertIn("Consultation complete!", end_result)
        self.assertTrue(self.health_assistant.is_consultation_complete())
        
        # Verify report was created
        report_files = [f for f in os.listdir(self.temp_reports_dir) if f.endswith('_report.txt')]
        self.assertEqual(len(report_files), 1)
        
        # Check report content
        report_path = os.path.join(self.temp_reports_dir, report_files[0])
        with open(report_path, 'r', encoding='utf-8') as file:
            report_content = file.read()
        
        self.assertIn("Integration Test Patient", report_content)
        self.assertIn("Persistent cough", report_content)
        self.assertIn("Shortness of breath", report_content)
        self.assertIn("Chest pain", report_content)
    
    def test_multiple_symptom_additions(self):
        """Test adding multiple symptoms and retrieving them in order"""
        symptoms = [
            "Morning headache",
            "Nausea after eating",
            "Dizziness when standing",
            "Blurred vision",
            "Fatigue throughout the day"
        ]
        
        # Add all symptoms
        for i, symptom in enumerate(symptoms):
            result = self.health_assistant.add_symptom(symptom)
            self.assertIn(f"Total symptoms recorded: {i + 1}", result)
        
        # Get all symptoms
        result = self.health_assistant.get_symptoms()
        
        # Check that all symptoms are present in order
        for i, symptom in enumerate(symptoms):
            self.assertIn(f"{i + 1}. {symptom}", result)
    
    def test_patient_lookup_after_creation(self):
        """Test that a created patient can be looked up by ID"""
        # Create patient
        create_result = self.health_assistant.create_patient(
            name="Lookup Test Patient",
            age=28,
            height=165.0,
            gender="Female",
            blood_group="B-",
            weight=58.0
        )
        
        # Extract patient ID from result
        patient_id = self.health_assistant._patient_details[PatientDetails.PATIENT_ID]
        
        # Clear the assistant state
        self.health_assistant = HealthAssistantFnc()
        
        # Lookup the created patient
        lookup_result = self.health_assistant.lookup_patient(patient_id)
        
        self.assertIn("The patient details are:", lookup_result)
        self.assertTrue(self.health_assistant.has_patient())
        self.assertEqual(self.health_assistant._patient_details[PatientDetails.NAME], "Lookup Test Patient")


if __name__ == '__main__':
    unittest.main()