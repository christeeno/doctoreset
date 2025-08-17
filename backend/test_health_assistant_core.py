import unittest
import tempfile
import os
import shutil
from datetime import datetime
from db_driver import DatabaseDriver, Patient
from report_generator import ReportGenerator
import enum


class PatientDetails(enum.Enum):
    """Enum for patient detail fields - copied from api.py for testing"""
    PATIENT_ID = "patient_id"
    NAME = "name"
    AGE = "age"
    HEIGHT = "height"
    GENDER = "gender"
    BLOOD_GROUP = "blood_group"
    WEIGHT = "weight"


class HealthAssistantCore:
    """Core health assistant functionality without livekit dependencies for testing"""
    
    def __init__(self, db_driver, report_generator):
        self.db = db_driver
        self.report_gen = report_generator
        
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
    
    def lookup_patient(self, patient_id: str):
        result = self.db.get_patient_by_id(patient_id)
        if result is None:
            return "Patient not found"
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: result.patient_id,
            PatientDetails.NAME: result.name,
            PatientDetails.AGE: result.age,
            PatientDetails.HEIGHT: result.height,
            PatientDetails.GENDER: result.gender,
            PatientDetails.BLOOD_GROUP: result