from uuid import UUID


class ResourceNotFoundException(Exception):
    def __init__(self, resouce_id: str | UUID, name: str = "Resource"):
        self.resource_id = resouce_id
        self.name = name


class PaperNotFoundException(ResourceNotFoundException):
    def __init__(self, paper_id: str | UUID):
        super().__init__(paper_id, "Paper")


class SessionNotFoundException(ResourceNotFoundException):
    def __init__(self, session_id: str):
        super().__init__(session_id, "Session")


class TaskNotFoundException(ResourceNotFoundException):
    def __init__(self, task_id: str):
        super().__init__(task_id, "Task")


class UserNotFoundException(ResourceNotFoundException):
    def __init__(self, user_id: str | UUID):
        super().__init__(user_id, "User")
