from livekit.agents import llm
import enum
from typing import Annotated, List
import logging
from db_driver import DatabaseDriver, Patient
from report_generator import ReportGenerator

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()
REPORT_GEN = ReportGenerator()

class PatientDetails(enum.Enum):
    PATIENT_ID = "patient_id"
    NAME = "name"
    AGE = "age"
    HEIGHT = "height"
    GENDER = "gender"
    BLOOD_GROUP = "blood_group"
    WEIGHT = "weight"
    

class HealthAssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: "",
            PatientDetails.NAME: "",
            PatientDetails.AGE: "",
            PatientDetails.HEIGHT: "",
            PatientDetails.GENDER: "",
            PatientDetails.BLOOD_GROUP: "",
            PatientDetails.WEIGHT: ""
        }
        self._symptoms = []
        self._conversation_complete = False
    
    def get_patient_str(self):
        patient_str = ""
        for key, value in self._patient_details.items():
            if value:  # Only include non-empty values
                patient_str += f"{key.value}: {value}\n"
            
        return patient_str
    
    @llm.ai_callable(description="lookup a patient by their patient ID")
    def lookup_patient(self, patient_id: Annotated[str, llm.TypeInfo(description="The patient ID to lookup")]):
        logger.info("lookup patient - patient_id: %s", patient_id)
        
        result = DB.get_patient_by_id(patient_id)
        if result is None:
            return "Patient not found"
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: result.patient_id,
            PatientDetails.NAME: result.name,
            PatientDetails.AGE: result.age,
            PatientDetails.HEIGHT: result.height,
            PatientDetails.GENDER: result.gender,
            PatientDetails.BLOOD_GROUP: result.blood_group,
            PatientDetails.WEIGHT: result.weight
        }
        
        return f"The patient details are: {self.get_patient_str()}"
    
    @llm.ai_callable(description="get the details of the current patient")
    def get_patient_details(self):
        logger.info("get patient details")
        return f"The patient details are: {self.get_patient_str()}"
    
    @llm.ai_callable(description="create a new patient")
    def create_patient(
        self, 
        name: Annotated[str, llm.TypeInfo(description="The patient's full name")],
        age: Annotated[int, llm.TypeInfo(description="The patient's age")],
        height: Annotated[float, llm.TypeInfo(description="The patient's height in cm")],
        gender: Annotated[str, llm.TypeInfo(description="The patient's gender")],
        blood_group: Annotated[str, llm.TypeInfo(description="The patient's blood group")],
        weight: Annotated[float, llm.TypeInfo(description="The patient's weight in kg")]
    ):
        logger.info("create patient - name: %s, age: %s, height: %s, gender: %s, blood_group: %s, weight: %s", 
                   name, age, height, gender, blood_group, weight)
        result = DB.create_patient(name, age, height, gender, blood_group, weight)
        if result is None:
            return "Failed to create patient"
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: result.patient_id,
            PatientDetails.NAME: result.name,
            PatientDetails.AGE: result.age,
            PatientDetails.HEIGHT: result.height,
            PatientDetails.GENDER: result.gender,
            PatientDetails.BLOOD_GROUP: result.blood_group,
            PatientDetails.WEIGHT: result.weight
        }
        
        return f"Patient created! Your patient ID is: {result.patient_id}"
    
    @llm.ai_callable(description="add a symptom to the patient's symptom list")
    def add_symptom(self, symptom: Annotated[str, llm.TypeInfo(description="Description of the symptom")]):
        logger.info("add symptom: %s", symptom)
        self._symptoms.append(symptom)
        return f"Symptom added: {symptom}. Total symptoms recorded: {len(self._symptoms)}"
    
    @llm.ai_callable(description="get all collected symptoms for the current patient")
    def get_symptoms(self):
        logger.info("get symptoms - count: %d", len(self._symptoms))
        if not self._symptoms:
            return "No symptoms have been recorded yet."
        
        symptoms_str = "Recorded symptoms:\n"
        for i, symptom in enumerate(self._symptoms, 1):
            symptoms_str += f"{i}. {symptom}\n"
        
        return symptoms_str
    
    @llm.ai_callable(description="mark the consultation as complete and generate diagnostic report")
    def end_consultation(self):
        logger.info("end consultation")
        
        # Check if we have patient information
        if not self.has_patient():
            return "Cannot end consultation: No patient information available."
        
        try:
            # Get current patient information
            patient = self.get_current_patient()
            
            # Generate and save the diagnostic report
            report_path = REPORT_GEN.generate_and_save_report(patient, self._symptoms)
            
            # Mark consultation as complete
            self._conversation_complete = True
            
            logger.info("Report generated and saved to: %s", report_path)
            
            return f"Consultation complete! Your diagnostic report has been generated and saved. Thank you for using our health assistant service. Report saved as: {report_path}"
            
        except Exception as e:
            logger.error("Failed to generate report: %s", str(e))
            # Still mark as complete even if report generation fails
            self._conversation_complete = True
            return f"Consultation marked as complete, but there was an issue generating your report: {str(e)}. Please contact support if needed."
    
    def is_consultation_complete(self):
        return self._conversation_complete
    
    def has_patient(self):
        return self._patient_details[PatientDetails.PATIENT_ID] != ""
    
    def get_current_patient(self) -> Patient:
        """Get the current patient as a Patient object"""
        if not self.has_patient():
            raise ValueError("No patient information available")
        
        return Patient(
            patient_id=self._patient_details[PatientDetails.PATIENT_ID],
            name=self._patient_details[PatientDetails.NAME],
            age=int(self._patient_details[PatientDetails.AGE]),
            height=float(self._patient_details[PatientDetails.HEIGHT]),
            gender=self._patient_details[PatientDetails.GENDER],
            blood_group=self._patient_details[PatientDetails.BLOOD_GROUP],
            weight=float(self._patient_details[PatientDetails.WEIGHT])
        )