from django.db import models


class Task(models.Model):
    """Model representing a task with a title, description, and status."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("done", "Done"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Task(id={self.id}: {self.title}, {self.status})"
