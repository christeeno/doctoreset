# Implementation Plan

- [x] 1. Update data models and database schema

  - Replace Car model with Patient model in db_driver.py
  - Update database schema from cars table to patients table
  - Implement patient ID generation logic similar to VIN handling
  - _Requirements: 1.3, 6.1, 6.2_

- [x] 2. Transform core API functions for health assistant

- [x] 2.1 Update AssistantFnc class to HealthAssistantFnc

  - Rename class and update patient-related attributes
  - Replace car detail tracking with patient information tracking
  - Add symptom collection capabilities
  - _Requirements: 1.2, 5.1, 5.3_

- [x] 2.2 Implement patient lookup and creation functions

  - Replace lookup_car with lookup_patient function
  - Replace create_car with create_patient function
  - Update function parameters for patient data (name, age, height, gender, blood_group, weight)
  - _Requirements: 1.2, 1.3, 6.1, 6.2_

- [x] 2.3 Add symptom collection functionality

  - Implement add_symptom function for collecting patient symptoms
  - Add get_symptoms function to retrieve collected symptoms
  - Implement conversation completion tracking
  - _Requirements: 2.2, 2.3, 5.3_

- [x] 3. Create report generation system

- [x] 3.1 Implement diagnostic report generator

  - Create ReportGenerator class with generate_diagnostic_report method
  - Format patient information and symptoms into structured report
  - Include timestamp and patient ID in report content
  - _Requirements: 3.1, 3.2_

- [x] 3.2 Implement report file saving functionality

  - Create save_report method to write reports to doctor folder
  - Generate unique filenames using patient name and timestamp
  - Create doctor folder if it doesn't exist
  - Handle file system errors gracefully
  - _Requirements: 3.3, 4.1, 4.2, 4.4_

- [x] 3.3 Add report generation trigger to conversation flow

  - Implement end_consultation function to generate and save reports
  - Add conversation completion detection logic
  - Integrate report generation with conversation end
  - _Requirements: 3.1, 3.4_

- [x] 4. Update conversation prompts and instructions

- [x] 4.1 Replace call center prompts with health assistant prompts

  - Update INSTRUCTIONS constant for health assistant role
  - Modify WELCOME_MESSAGE for patient greeting and ID collection
  - Update LOOKUP_VIN_MESSAGE to LOOKUP_PATIENT_MESSAGE
  - _Requirements: 1.1, 6.1_

- [x] 4.2 Add symptom collection prompts

  - Create prompts for symptom gathering phase
  - Add follow-up question prompts for symptom clarification
  - Implement conversation completion prompts
  - _Requirements: 2.1, 2.2_

- [x] 5. Update main agent logic for health assistant workflow

- [x] 5.1 Modify conversation flow in agent.py

  - Update has_car() to has_patient() logic
  - Modify find_profile to handle patient lookup instead of VIN
  - Update handle_query to include symptom collection and report generation
  - _Requirements: 5.2, 6.4_

- [x] 5.2 Implement conversation phase management

  - Add logic to track conversation phases (info collection, symptoms, completion)
  - Implement state transitions between phases
  - Add conversation completion detection and report generation trigger
  - _Requirements: 2.4, 3.1, 5.3_

- [x] 6. Create unit tests for new functionality


- [x] 6.1 Write tests for Patient model and database operations

  - Test patient creation, lookup, and validation
  - Test patient ID generation uniqueness
  - Test database CRUD operations for patients
  - _Requirements: 1.3, 6.1, 6.2_

- [x] 6.2 Write tests for report generation system

- [x] 6.2 Write tests for report generation system

  - Test diagnostic report content generation
  - Test file saving functionality and unique filename generation
  - Test doctor folder creation and error handling

  - _Requirements: 3.2, 3.3, 4.1, 4.2_

- [ ] 6.3 Write tests for health assistant functions











  - Test patient lookup and creation functions
  - Test symptom collection and retrieval

  - Test conversation completion and report generation integration
  - _Requirements: 2.2, 2.3, 3.1_

- [ ] 7. Update database initialization and migration
  - Create database migration script to convert existing cars table to patients table
  - Update database initialization to create patients table instead of cars table
  - Ensure backward compatibility during transition
  - _Requirements: 4.1, 6.1_
