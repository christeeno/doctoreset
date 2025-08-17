# Design Document

## Overview

The health assistant transformation will convert the existing call center manager system from a car dealership context to a healthcare consultation system. The core conversational interface and real-time communication infrastructure will remain unchanged, while the data models, business logic, and user interactions will be adapted for healthcare use cases.

## Architecture

The system maintains the same high-level architecture with these components:
- **Frontend**: React-based web interface for patient interaction
- **Backend**: Python-based real-time agent using LiveKit for voice/video communication
- **Database**: SQLite database for patient profile storage
- **File System**: Local storage for generated diagnostic reports

### Key Architectural Changes
1. Replace car-focused data models with patient health models
2. Transform VIN-based lookup to patient ID-based lookup
3. Add symptom collection and diagnostic report generation capabilities
4. Implement file-based report storage in "doctor" folder

## Components and Interfaces

### 1. Patient Data Model (replaces Car model)
```python
@dataclass
class Patient:
    patient_id: str          # Unique identifier (replaces VIN)
    name: str               # Patient's full name
    age: int                # Patient's age
    height: float           # Height in cm
    gender: str             # Gender (Male/Female/Other)
    blood_group: str        # Blood group (A+, B-, O+, etc.)
    weight: float           # Weight in kg
    created_at: datetime    # Profile creation timestamp
```

### 2. Health Assistant Function Context (replaces AssistantFnc)
```python
class HealthAssistantFnc(llm.FunctionContext):
    def __init__(self):
        self._patient_details = {}
        self._symptoms = []
        self._conversation_complete = False
    
    # Core functions:
    # - lookup_patient(patient_id) -> Patient lookup
    # - create_patient(...) -> New patient profile creation
    # - add_symptom(symptom) -> Symptom collection
    # - generate_report() -> Create diagnostic report
    # - end_consultation() -> Mark consultation complete
```

### 3. Database Driver Updates
- Replace `cars` table with `patients` table
- Add patient ID generation logic (similar to VIN handling)
- Implement patient CRUD operations
- Add symptom storage capabilities (optional for future enhancement)

### 4. Report Generation System
```python
class ReportGenerator:
    def generate_diagnostic_report(patient: Patient, symptoms: List[str]) -> str:
        # Generate structured diagnostic report
        # Include patient information and symptoms
        # Return formatted report content
    
    def save_report(content: str, patient_name: str) -> str:
        # Save report to doctor folder
        # Generate unique filename with timestamp
        # Return file path
```

## Data Models

### Patient Information Schema
```sql
CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    height REAL NOT NULL,
    gender TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    weight REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Patient ID Generation
- Format: "P" + 8-digit random number (e.g., "P12345678")
- Ensure uniqueness by checking against existing IDs
- Similar to current VIN handling logic

### Symptom Data Structure
```python
@dataclass
class Symptom:
    description: str
    severity: Optional[str]  # mild, moderate, severe
    duration: Optional[str]  # how long patient has had symptom
    additional_notes: Optional[str]
```

## Error Handling

### Patient Lookup Errors
- Invalid patient ID format
- Patient not found in database
- Database connection failures

### Data Collection Errors
- Missing required patient information
- Invalid data formats (age, height, weight)
- Incomplete symptom descriptions

### Report Generation Errors
- File system permission issues
- Disk space limitations
- Report formatting failures

### Conversation Flow Errors
- Premature conversation termination
- Context loss during conversation
- Invalid state transitions

## Testing Strategy

### Unit Tests
1. **Patient Data Model Tests**
   - Patient creation and validation
   - Patient ID generation uniqueness
   - Data serialization/deserialization

2. **Database Operations Tests**
   - Patient CRUD operations
   - Database connection handling
   - Error scenarios (duplicate IDs, invalid data)

3. **Report Generation Tests**
   - Report content formatting
   - File creation and saving
   - Filename generation uniqueness

### Integration Tests
1. **Conversation Flow Tests**
   - Complete patient onboarding flow
   - Symptom collection scenarios
   - Report generation end-to-end

2. **Database Integration Tests**
   - Patient lookup and creation workflows
   - Data persistence verification
   - Concurrent access scenarios

### Functional Tests
1. **Voice Interface Tests**
   - Patient information collection via voice
   - Symptom description processing
   - Conversation completion detection

2. **Report Output Tests**
   - Generated report content accuracy
   - File system integration
   - Report accessibility and format

## Implementation Considerations

### Conversation State Management
- Track conversation phases: greeting → patient info → symptoms → report generation
- Maintain patient context throughout conversation
- Handle conversation interruptions and resumptions

### Data Validation
- Implement robust validation for patient information
- Sanitize symptom descriptions for report generation
- Validate patient ID format and uniqueness

### File System Management
- Create "doctor" folder if it doesn't exist
- Generate unique report filenames to prevent conflicts
- Handle file system permissions and errors gracefully

### Privacy and Security
- Ensure patient data is handled securely
- Implement appropriate data retention policies
- Consider encryption for sensitive patient information

### Scalability Considerations
- Database indexing for patient lookups
- Efficient report generation for large symptom lists
- File system organization for large numbers of reports