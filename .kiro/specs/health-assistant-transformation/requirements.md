# Requirements Document

## Introduction

Transform the existing call center manager system for a car dealership into a health assistant system that collects patient information, gathers symptoms, and generates initial diagnostic reports. The system should maintain the same conversational interface but adapt the data collection and processing logic for healthcare use cases.

## Requirements

### Requirement 1

**User Story:** As a patient, I want to provide my basic personal information to the health assistant, so that my medical consultation can be properly documented and personalized.

#### Acceptance Criteria

1. WHEN a patient starts a conversation THEN the system SHALL greet them as a health assistant and request their patient ID or offer to create a new profile
2. WHEN collecting patient information THEN the system SHALL gather name, age, height, gender, blood group, and weight
3. WHEN creating a new patient profile THEN the system SHALL generate a unique patient ID number
4. IF any required personal information is missing THEN the system SHALL prompt the patient to provide the missing details
5. WHEN all basic information is collected THEN the system SHALL confirm the details with the patient

### Requirement 2

**User Story:** As a patient, I want to describe my symptoms to the health assistant, so that I can receive an initial assessment of my condition.

#### Acceptance Criteria

1. WHEN basic information is complete THEN the system SHALL ask the patient to describe their symptoms
2. WHEN the patient describes symptoms THEN the system SHALL ask follow-up questions to gather comprehensive symptom information
3. WHEN symptom collection is ongoing THEN the system SHALL maintain context of previously mentioned symptoms
4. IF symptoms are unclear or incomplete THEN the system SHALL ask clarifying questions

### Requirement 3

**User Story:** As a patient, I want to receive an initial diagnostic report after my consultation, so that I have documentation of my health assessment.

#### Acceptance Criteria

1. WHEN the patient indicates the conversation is complete THEN the system SHALL generate an initial diagnostic report
2. WHEN generating the report THEN the system SHALL include all collected patient information and symptoms
3. WHEN the report is generated THEN the system SHALL save it as a .txt file in a "doctor" folder
4. WHEN the consultation ends THEN the system SHALL thank the patient and inform them about the generated report

### Requirement 4

**User Story:** As a healthcare provider, I want patient reports to be systematically stored, so that I can access and review patient consultations.

#### Acceptance Criteria

1. WHEN a report is generated THEN the system SHALL create a "doctor" folder if it doesn't exist
2. WHEN saving the report THEN the system SHALL use a unique filename that includes patient name and timestamp
3. WHEN the report is saved THEN the system SHALL include all collected patient data in a structured format
4. IF the save operation fails THEN the system SHALL notify the patient and attempt to retry

### Requirement 5

**User Story:** As a health assistant system, I want to maintain patient data during the conversation, so that I can provide contextual responses and generate accurate reports.

#### Acceptance Criteria

1. WHEN patient information is provided THEN the system SHALL store it in memory for the duration of the conversation
2. WHEN all required information is collected THEN the system SHALL indicate readiness to proceed with symptom collection
3. WHEN the conversation progresses THEN the system SHALL maintain context of all previously collected information
4. IF the patient wants to correct information THEN the system SHALL allow updates to previously provided data

### Requirement 6

**User Story:** As a patient, I want to be able to look up my existing profile using my patient ID, so that I don't have to re-enter my information for follow-up consultations.

#### Acceptance Criteria

1. WHEN a patient provides an existing patient ID THEN the system SHALL look up their profile in the database
2. IF the patient ID exists THEN the system SHALL load the patient's information and proceed to symptom collection
3. IF the patient ID does not exist THEN the system SHALL inform the patient and offer to create a new profile
4. WHEN looking up a patient THEN the system SHALL display the retrieved patient information for confirmation