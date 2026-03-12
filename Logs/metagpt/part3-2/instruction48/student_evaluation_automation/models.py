from typing import Dict, Optional


class StudentRecord:
    """
    Represents a student's evaluation record, including form data, generated pathway,
    document links, and status tracking.
    """

    def __init__(
        self,
        student_id: str,
        name: str,
        email: str,
        machform_data: Dict[str, Dict],
        academic_pathway: Optional[str] = None,
        pdf_path: Optional[str] = None,
        salesforce_id: Optional[str] = None,
        status: str = "pending"
    ):
        """
        Initialize a StudentRecord.

        Args:
            student_id (str): Unique identifier for the student.
            name (str): Student's full name.
            email (str): Student's email address.
            machform_data (Dict[str, Dict]): Data from each MachForm, keyed by form ID or name.
            academic_pathway (Optional[str]): Generated academic pathway text.
            pdf_path (Optional[str]): Path to the generated PDF document.
            salesforce_id (Optional[str]): Salesforce record/document ID.
            status (str): Current processing status.
        """
        self.student_id = student_id
        self.name = name
        self.email = email
        self.machform_data = machform_data  # e.g., {'form1': {...}, 'form2': {...}, 'form3': {...}}
        self.academic_pathway = academic_pathway
        self.pdf_path = pdf_path
        self.salesforce_id = salesforce_id
        self.status = status  # e.g., 'pending', 'data_collected', 'pathway_generated', 'pdf_sent', 'sf_uploaded', 'completed', 'error'

    def to_dict(self) -> Dict:
        """
        Serialize the student record to a dictionary for storage or transmission.

        Returns:
            Dict: Dictionary representation of the student record.
        """
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "machform_data": self.machform_data,
            "academic_pathway": self.academic_pathway,
            "pdf_path": self.pdf_path,
            "salesforce_id": self.salesforce_id,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StudentRecord":
        """
        Create a StudentRecord from a dictionary.

        Args:
            data (Dict): Dictionary containing student record data.

        Returns:
            StudentRecord: The constructed StudentRecord object.
        """
        return cls(
            student_id=data.get("student_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            machform_data=data.get("machform_data", {}),
            academic_pathway=data.get("academic_pathway"),
            pdf_path=data.get("pdf_path"),
            salesforce_id=data.get("salesforce_id"),
            status=data.get("status", "pending"),
        )