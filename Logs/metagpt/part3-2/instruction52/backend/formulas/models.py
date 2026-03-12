from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import sympy

User = get_user_model()

class Formula(models.Model):
    formula_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formulas')
    name = models.CharField(max_length=255)
    expression = models.TextField()  # SymPy-compatible string
    created_at = models.DateTimeField(default=timezone.now)

    def evaluate(self, variables: dict) -> float:
        """
        Evaluates the formula using the provided variables.
        :param variables: dict mapping variable names to values
        :return: float result of the formula
        """
        try:
            expr = sympy.sympify(self.expression)
            result = expr.evalf(subs=variables)
            return float(result)
        except Exception as e:
            raise ValueError(f"Error evaluating formula: {e}")

    @classmethod
    def load(cls, formula_id: int):
        """
        Loads a formula by its ID.
        """
        return cls.objects.get(formula_id=formula_id)

    def save(self, *args, **kwargs):
        """
        Saves the formula instance.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class FormulaResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='formula_results')
    input_data = models.JSONField()
    result = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Result of {self.formula.name} for {self.user.username} at {self.created_at}"