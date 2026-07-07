from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    """Serializer for representing a Task in responses and validating creation inputs.

    Handles standard validation for tasks, ensuring title isn't blank and properly
    formatting timestamps and status fields as read-only.
    """

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        max_length=255, trim_whitespace=True, allow_blank=False
    )
    description = serializers.CharField(
        max_length=2000,
        trim_whitespace=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )
    status = serializers.ChoiceField(
        choices=[("pending", "pending"), ("done", "done")], read_only=True
    )
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)


class TaskUpdateSerializer(serializers.Serializer):
    """Serializer strictly for validating partial updates to a Task.

    Ensures that at least one field is provided and enforces business logic
    on the status and title fields.
    """

    title = serializers.CharField(
        max_length=255, trim_whitespace=True, required=False, allow_blank=False
    )
    description = serializers.CharField(
        max_length=2000,
        trim_whitespace=True,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    status = serializers.ChoiceField(
        choices=[("pending", "pending"), ("done", "done")], required=False
    )

    def validate(self, attrs):
        """Validates that at least one field is being updated.

        Args:
            attrs: Dictionary of validated field values.

        Returns:
            The validated attributes dictionary.

        Raises:
            serializers.ValidationError: If no fields were provided for the update.
        """
        if not attrs:
            raise serializers.ValidationError(
                "At least one field must be provided for update."
            )
        return attrs
