import unittest
import tempfile
import os
import shutil
from datetime import datetime
from unittest.mock import patch, mock_open
from report_generator import ReportGenerator, ReportData
from db_driver import Patient


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.report_gen = ReportGenerator(reports_folder=self.temp_dir)
        
        # Create sample patient for testing
        self.sample_patient = Patient(
            patient_id="P12345678",
            name="John Doe",
            age=30,
            height=175.5,
            gender="Male",
            blood_group="O+",
            weight=70.0,
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        self.sample_symptoms = [
            "Headache for 2 days",
            "Mild fever (38°C)",
            "Fatigue and weakness"
        ]
    
    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_diagnostic_report_content(self):
        """Test diagnostic report content generation"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 0)
        
        report_content = self.report_gen.generate_diagnostic_report(
            self.sample_patient, 
            self.sample_symptoms, 
            consultation_date
        )
        
        # Check that report contains expected sections
        self.assertIn("HEALTH ASSISTANT DIAGNOSTIC REPORT", report_content)
        self.assertIn("CONSULTATION DATE: 2024-02-01 14:30:00", report_content)
        self.assertIn("PATIENT ID: P12345678", report_content)
        self.assertIn("PATIENT INFORMATION:", report_content)
        self.assertIn("Name: John Doe", report_content)
        self.assertIn("Age: 30 years", report_content)
        self.assertIn("Height: 175.5 cm", report_content)
        self.assertIn("Weight: 70.0 kg", report_content)
        self.assertIn("Gender: Male", report_content)
        self.assertIn("Blood Group: O+", report_content)
        self.assertIn("Profile Created: 2024-01-15", report_content)
        self.assertIn("SYMPTOMS REPORTED:", report_content)
        self.assertIn("1. Headache for 2 days", report_content)
        self.assertIn("2. Mild fever (38°C)", report_content)
        self.assertIn("3. Fatigue and weakness", report_content)
        self.assertIn("REPORT GENERATED:", report_content)
        self.assertIn("NOTE: This is an initial assessment", report_content)
    
    def test_generate_diagnostic_report_no_symptoms(self):
        """Test diagnostic report generation with no symptoms"""
        report_content = self.report_gen.generate_diagnostic_report(
            self.sample_patient, 
            []
        )
        
        self.assertIn("SYMPTOMS REPORTED:", report_content)
        self.assertIn("No symptoms were reported during this consultation.", report_content)
    
    def test_generate_diagnostic_report_default_date(self):
        """Test diagnostic report generation with default consultation date"""
        with patch('report_generator.datetime') as mock_datetime:
            mock_now = datetime(2024, 2, 1, 15, 45, 30)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime  # Keep original strftime
            
            report_content = self.report_gen.generate_diagnostic_report(
                self.sample_patient, 
                self.sample_symptoms
            )
            
            self.assertIn("CONSULTATION DATE: 2024-02-01 15:45:30", report_content)
    
    def test_format_patient_info(self):
        """Test patient information formatting"""
        patient_info = self.report_gen._format_patient_info(self.sample_patient)
        
        expected_lines = [
            "PATIENT INFORMATION:",
            "Name: John Doe",
            "Age: 30 years",
            "Height: 175.5 cm",
            "Weight: 70.0 kg",
            "Gender: Male",
            "Blood Group: O+",
            "Profile Created: 2024-01-15"
        ]
        
        for line in expected_lines:
            self.assertIn(line, patient_info)
    
    def test_format_patient_info_no_created_date(self):
        """Test patient information formatting when created_at is None"""
        patient_no_date = Patient(
            patient_id="P87654321",
            name="Jane Smith",
            age=25,
            height=165.0,
            gender="Female",
            blood_group="A-",
            weight=60.0,
            created_at=None
        )
        
        patient_info = self.report_gen._format_patient_info(patient_no_date)
        self.assertIn("Profile Created: Unknown", patient_info)
    
    def test_format_symptoms_with_symptoms(self):
        """Test symptoms formatting with symptom list"""
        symptoms_section = self.report_gen._format_symptoms(self.sample_symptoms)
        
        self.assertIn("SYMPTOMS REPORTED:", symptoms_section)
        self.assertIn("1. Headache for 2 days", symptoms_section)
        self.assertIn("2. Mild fever (38°C)", symptoms_section)
        self.assertIn("3. Fatigue and weakness", symptoms_section)
    
    def test_format_symptoms_empty_list(self):
        """Test symptoms formatting with empty symptom list"""
        symptoms_section = self.report_gen._format_symptoms([])
        
        self.assertIn("SYMPTOMS REPORTED:", symptoms_section)
        self.assertIn("No symptoms were reported during this consultation.", symptoms_section)
    
    def test_generate_filename(self):
        """Test unique filename generation"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filename = self.report_gen._generate_filename("John Doe", consultation_date)
        
        self.assertEqual(filename, "John_Doe_20240201_143045_report.txt")
    
    def test_generate_filename_special_characters(self):
        """Test filename generation with special characters in name"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filename = self.report_gen._generate_filename("Mary O'Connor-Smith", consultation_date)
        
        # Should sanitize special characters
        self.assertEqual(filename, "Mary_OConnor-Smith_20240201_143045_report.txt")
    
    def test_generate_filename_invalid_characters(self):
        """Test filename generation with invalid filename characters"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filename = self.report_gen._generate_filename("John/Doe<>|", consultation_date)
        
        # Should remove invalid characters
        self.assertEqual(filename, "JohnDoe_20240201_143045_report.txt")
    
    def test_ensure_reports_folder_exists(self):
        """Test that reports folder is created if it doesn't exist"""
        # Remove the temp directory to test creation
        shutil.rmtree(self.temp_dir)
        self.assertFalse(os.path.exists(self.temp_dir))
        
        # This should create the folder
        self.report_gen._ensure_reports_folder_exists()
        
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.isdir(self.temp_dir))
    
    def test_ensure_reports_folder_exists_already_exists(self):
        """Test that existing reports folder is not affected"""
        # Folder already exists from setUp
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # This should not raise an error
        self.report_gen._ensure_reports_folder_exists()
        
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_save_report_success(self):
        """Test successful report saving"""
        report_content = "Test report content"
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filepath = self.report_gen.save_report(
            report_content, 
            "John Doe", 
            consultation_date
        )
        
        expected_filename = "John_Doe_20240201_143045_report.txt"
        expected_filepath = os.path.join(self.temp_dir, expected_filename)
        
        self.assertEqual(filepath, expected_filepath)
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as file:
            saved_content = file.read()
        
        self.assertEqual(saved_content, report_content)
    
    def test_save_report_default_date(self):
        """Test report saving with default consultation date"""
        report_content = "Test report content"
        
        with patch('report_generator.datetime') as mock_datetime:
            mock_now = datetime(2024, 2, 1, 15, 45, 30)
            mock_datetime.now.return_value = mock_now
            
            filepath = self.report_gen.save_report(report_content, "Jane Smith")
            
            expected_filename = "Jane_Smith_20240201_154530_report.txt"
            self.assertTrue(filepath.endswith(expected_filename))
    
    @patch('os.makedirs', side_effect=OSError("Permission denied"))
    def test_save_report_folder_creation_error(self, mock_makedirs):
        """Test error handling when folder creation fails"""
        # Create a new report generator that will trigger folder creation
        new_temp_dir = os.path.join(self.temp_dir, "new_folder")
        invalid_report_gen = ReportGenerator(reports_folder=new_temp_dir)
        
        with self.assertRaises(OSError) as context:
            invalid_report_gen.save_report("test content", "John Doe")
        
        self.assertIn("Failed to create reports folder", str(context.exception))
    
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_save_report_file_write_error(self, mock_open_func):
        """Test error handling when file writing fails"""
        with self.assertRaises(OSError) as context:
            self.report_gen.save_report("test content", "John Doe")
        
        self.assertIn("Failed to save report", str(context.exception))
    
    def test_generate_and_save_report_success(self):
        """Test complete report generation and saving workflow"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filepath = self.report_gen.generate_and_save_report(
            self.sample_patient,
            self.sample_symptoms,
            consultation_date
        )
        
        # Check that file was created
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verify report content
        self.assertIn("HEALTH ASSISTANT DIAGNOSTIC REPORT", content)
        self.assertIn("PATIENT ID: P12345678", content)
        self.assertIn("Name: John Doe", content)
        self.assertIn("1. Headache for 2 days", content)
        self.assertIn("CONSULTATION DATE: 2024-02-01 14:30:45", content)
    
    def test_generate_and_save_report_default_date(self):
        """Test complete workflow with default consultation date"""
        with patch('report_generator.datetime') as mock_datetime:
            mock_now = datetime(2024, 2, 1, 16, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime  # Keep original strftime
            
            filepath = self.report_gen.generate_and_save_report(
                self.sample_patient,
                self.sample_symptoms
            )
            
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.assertIn("CONSULTATION DATE: 2024-02-01 16:00:00", content)
    
    def test_multiple_reports_unique_filenames(self):
        """Test that multiple reports for same patient get unique filenames"""
        # Generate multiple reports with slight time differences
        filepaths = []
        
        for i in range(3):
            consultation_date = datetime(2024, 2, 1, 14, 30, i)  # Different seconds
            filepath = self.report_gen.generate_and_save_report(
                self.sample_patient,
                self.sample_symptoms,
                consultation_date
            )
            filepaths.append(filepath)
        
        # All filepaths should be unique
        self.assertEqual(len(set(filepaths)), 3)
        
        # All files should exist
        for filepath in filepaths:
            self.assertTrue(os.path.exists(filepath))
    
    def test_report_content_includes_all_patient_data(self):
        """Test that report includes all collected patient data as per requirement 3.2"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 0)
        
        # Test with comprehensive patient data
        comprehensive_patient = Patient(
            patient_id="P99887766",
            name="Alice Johnson",
            age=45,
            height=168.2,
            gender="Female",
            blood_group="AB+",
            weight=65.5,
            created_at=datetime(2024, 1, 10, 9, 15, 30)
        )
        
        comprehensive_symptoms = [
            "Persistent cough for 5 days",
            "Shortness of breath during exercise",
            "Chest tightness in the morning",
            "Low-grade fever (37.8°C)"
        ]
        
        report_content = self.report_gen.generate_diagnostic_report(
            comprehensive_patient,
            comprehensive_symptoms,
            consultation_date
        )
        
        # Verify all patient data is included (requirement 3.2)
        self.assertIn("PATIENT ID: P99887766", report_content)
        self.assertIn("Name: Alice Johnson", report_content)
        self.assertIn("Age: 45 years", report_content)
        self.assertIn("Height: 168.2 cm", report_content)
        self.assertIn("Weight: 65.5 kg", report_content)
        self.assertIn("Gender: Female", report_content)
        self.assertIn("Blood Group: AB+", report_content)
        self.assertIn("Profile Created: 2024-01-10", report_content)
        
        # Verify all symptoms are included (requirement 3.2)
        self.assertIn("1. Persistent cough for 5 days", report_content)
        self.assertIn("2. Shortness of breath during exercise", report_content)
        self.assertIn("3. Chest tightness in the morning", report_content)
        self.assertIn("4. Low-grade fever (37.8°C)", report_content)
        
        # Verify consultation date is included
        self.assertIn("CONSULTATION DATE: 2024-02-01 14:30:00", report_content)
    
    def test_report_saved_as_txt_file_in_doctor_folder(self):
        """Test that report is saved as .txt file in doctor folder as per requirement 3.3"""
        report_content = "Test diagnostic report content"
        consultation_date = datetime(2024, 2, 1, 14, 30, 45)
        
        filepath = self.report_gen.save_report(
            report_content,
            "Test Patient",
            consultation_date
        )
        
        # Verify file is saved in doctor folder (requirement 3.3)
        self.assertTrue(filepath.startswith(self.temp_dir))
        
        # Verify file has .txt extension (requirement 3.3)
        self.assertTrue(filepath.endswith(".txt"))
        
        # Verify file exists and contains correct content
        self.assertTrue(os.path.exists(filepath))
        with open(filepath, 'r', encoding='utf-8') as file:
            saved_content = file.read()
        self.assertEqual(saved_content, report_content)
    
    def test_filename_includes_patient_name_and_timestamp(self):
        """Test that filename includes patient name and timestamp as per requirement 4.2"""
        consultation_date = datetime(2024, 3, 15, 10, 25, 30)
        
        # Test with various patient names
        test_cases = [
            ("John Smith", "John_Smith_20240315_102530_report.txt"),
            ("Mary-Jane Watson", "Mary-Jane_Watson_20240315_102530_report.txt"),
            ("Dr. Robert Brown", "Dr_Robert_Brown_20240315_102530_report.txt")
        ]
        
        for patient_name, expected_filename in test_cases:
            with self.subTest(patient_name=patient_name):
                filename = self.report_gen._generate_filename(patient_name, consultation_date)
                
                # Verify filename includes patient name (requirement 4.2)
                self.assertIn("John_Smith" if "John" in patient_name else 
                            "Mary-Jane_Watson" if "Mary" in patient_name else 
                            "Dr_Robert_Brown", filename)
                
                # Verify filename includes timestamp (requirement 4.2)
                self.assertIn("20240315_102530", filename)
                
                # Verify complete expected filename
                self.assertEqual(filename, expected_filename)
    
    def test_doctor_folder_creation_requirement(self):
        """Test that doctor folder is created when report is generated as per requirement 4.1"""
        # Use a non-existent folder path
        new_folder_path = os.path.join(self.temp_dir, "new_doctor_folder")
        report_gen_new = ReportGenerator(reports_folder=new_folder_path)
        
        # Verify folder doesn't exist initially
        self.assertFalse(os.path.exists(new_folder_path))
        
        # Generate and save a report (requirement 4.1)
        filepath = report_gen_new.save_report(
            "Test report content",
            "Jane Doe",
            datetime(2024, 2, 1, 14, 30, 0)
        )
        
        # Verify doctor folder was created (requirement 4.1)
        self.assertTrue(os.path.exists(new_folder_path))
        self.assertTrue(os.path.isdir(new_folder_path))
        
        # Verify report was saved in the created folder
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.startswith(new_folder_path))
    
    def test_structured_report_format_requirement(self):
        """Test that report includes all data in structured format as per requirement 4.3"""
        consultation_date = datetime(2024, 2, 1, 14, 30, 0)
        
        report_content = self.report_gen.generate_diagnostic_report(
            self.sample_patient,
            self.sample_symptoms,
            consultation_date
        )
        
        # Verify structured format sections are present (requirement 4.3)
        required_sections = [
            "HEALTH ASSISTANT DIAGNOSTIC REPORT",
            "CONSULTATION DATE:",
            "PATIENT ID:",
            "PATIENT INFORMATION:",
            "SYMPTOMS REPORTED:",
            "REPORT GENERATED:",
            "NOTE: This is an initial assessment"
        ]
        
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, report_content)
        
        # Verify proper formatting with separators
        self.assertIn("=" * 50, report_content)
        
        # Verify patient data is properly structured
        lines = report_content.split('\n')
        patient_info_found = False
        symptoms_found = False
        
        for line in lines:
            if "PATIENT INFORMATION:" in line:
                patient_info_found = True
            elif "SYMPTOMS REPORTED:" in line:
                symptoms_found = True
        
        self.assertTrue(patient_info_found, "Patient information section not found")
        self.assertTrue(symptoms_found, "Symptoms section not found")


if __name__ == '__main__':
    unittest.main()