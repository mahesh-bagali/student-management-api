
class StudentNotFoundError(Exception):
    def __init__(self, student_id: int):
        self.student_id = student_id
        super().__init__(
            f"Student with ID {student_id} was not found"
        )
