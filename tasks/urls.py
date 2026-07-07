from django.urls import path
from .views import TaskViewSet

urlpatterns = [
    path(
        "tasks",
        TaskViewSet.as_view({"get": "list", "post": "create"}),
        name="task-list",
    ),
    path(
        "tasks/<int:pk>",
        TaskViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="task-detail",
    ),
]
