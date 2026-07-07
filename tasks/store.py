import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple, Any


@dataclass
class Task:
    """Represents a single To-Do task.

    Attributes:
        id: Unique auto-incremented identifier.
        title: Title of the task.
        description: Detailed description of the task.
        status: Current status of the task ('pending' or 'done').
        createdAt: Timestamp when the task was created.
        updatedAt: Timestamp when the task was last updated.
    """

    id: int
    title: str
    description: str
    status: str
    createdAt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InMemoryTaskStore:
    """Thread-safe in-memory storage for Task objects using the Singleton pattern.

    Attributes:
        tasks: Dictionary mapping task IDs to Task objects.
        next_id: The next available ID for a new task.
        store_lock: Lock to ensure thread safety during CRUD operations.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "InMemoryTaskStore":
        """Creates a new instance or returns the existing singleton instance.

        Returns:
            The singleton InMemoryTaskStore instance.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.tasks: Dict[int, Task] = {}
                cls._instance.next_id = 1
                cls._instance.store_lock = threading.Lock()
        return cls._instance

    def create(self, title: str, description: str) -> Task:
        """Creates a new task and adds it to the store.

        Args:
            title: The title of the task.
            description: The description of the task.

        Returns:
            The newly created Task object.
        """
        with self.store_lock:
            task_id = self.next_id
            self.next_id += 1
            task = Task(
                id=task_id, title=title, description=description, status="pending"
            )
            self.tasks[task_id] = task
            return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieves a task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object if found, otherwise None.
        """
        with self.store_lock:
            return self.tasks.get(task_id)

    def get_all(
        self, status: Optional[str], sort_by: str, order: str, page: int, limit: int
    ) -> Tuple[List[Task], int]:
        """Retrieves a paginated, sorted, and optionally filtered list of tasks.

        Args:
            status: Optional status to filter tasks by ('pending' or 'done').
            sort_by: Field to sort the tasks by ('createdAt' or 'updatedAt').
            order: Sorting order ('asc' or 'desc').
            page: The page number to retrieve (1-indexed).
            limit: The maximum number of tasks to return per page.

        Returns:
            A tuple containing a list of Task objects for the requested page and the total number of filtered tasks.
        """
        with self.store_lock:
            filtered_tasks = list(self.tasks.values())

            if status:
                filtered_tasks = [t for t in filtered_tasks if t.status == status]

            total = len(filtered_tasks)

            reverse = order == "desc"

            if sort_by == "updatedAt":
                filtered_tasks.sort(key=lambda t: t.updatedAt, reverse=reverse)
            else:
                filtered_tasks.sort(key=lambda t: t.createdAt, reverse=reverse)

            start_index = (page - 1) * limit
            if start_index < 0:
                start_index = 0

            end_index = start_index + limit

            return filtered_tasks[start_index:end_index], total

    def update(self, task_id: int, data: Dict[str, Any]) -> Optional[Task]:
        """Updates an existing task with the provided data.

        Args:
            task_id: The ID of the task to update.
            data: A dictionary containing the fields to update.

        Returns:
            The updated Task object if the task exists, otherwise None.
        """
        with self.store_lock:
            task = self.tasks.get(task_id)
            if not task:
                return None

            updated = False
            for key, value in data.items():
                if hasattr(task, key) and key not in ("id", "createdAt", "updatedAt"):
                    setattr(task, key, value)
                    updated = True

            if updated:
                task.updatedAt = datetime.now(timezone.utc)

            return task

    def delete(self, task_id: int) -> bool:
        """Deletes a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the task was successfully deleted, False if the task was not found.
        """
        with self.store_lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False


# Global instance to be used across the app
store = InMemoryTaskStore()
