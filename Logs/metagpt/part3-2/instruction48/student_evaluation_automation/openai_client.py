import os
import logging
from typing import Dict
import openai

class OpenAIClient:
    """
    Client to generate personalized academic pathways using the OpenAI API.
    """

    def __init__(self, api_key: str, model: str = "gpt-4", timeout: int = 30):
        """
        Initialize the OpenAIClient.

        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model to use.
            timeout (int): Timeout for API requests in seconds.
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger("OpenAIClient")
        openai.api_key = self.api_key

    def generate_pathway(self, student_data: Dict) -> str:
        """
        Generate a personalized academic pathway using the OpenAI API.

        Args:
            student_data (Dict): Dictionary containing student information and MachForm data.

        Returns:
            str: Generated academic pathway text.
        """
        prompt = self._build_prompt(student_data)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert academic advisor. Based on the student's background and goals, generate a personalized academic pathway including recommended courses, milestones, and next steps. Be clear, actionable, and professional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7,
                timeout=self.timeout
            )
            pathway = response.choices[0].message['content'].strip()
            self.logger.info("Generated academic pathway for student: %s", student_data.get("student_id", "unknown"))
            return pathway
        except Exception as e:
            self.logger.error(f"OpenAI API error for student {student_data.get('student_id', 'unknown')}: {e}")
            return "We were unable to generate a personalized academic pathway at this time. Please contact admissions for assistance."

    def _build_prompt(self, student_data: Dict) -> str:
        """
        Build a prompt for the OpenAI API based on student data.

        Args:
            student_data (Dict): Dictionary containing student information and MachForm data.

        Returns:
            str: Constructed prompt string.
        """
        name = student_data.get("name", "Student")
        background = student_data.get("machform_data", {})
        academic_goals = background.get("form1", {}).get("academic_goals", "")
        interests = background.get("form2", {}).get("interests", "")
        prior_courses = background.get("form3", {}).get("prior_courses", "")

        prompt = (
            f"Student Name: {name}\n"
            f"Academic Goals: {academic_goals}\n"
            f"Interests: {interests}\n"
            f"Prior Courses: {prior_courses}\n"
            "Please generate a personalized academic pathway for this student, including recommended courses, milestones, and next steps. "
            "Format the response in clear, actionable steps."
        )
        return prompt