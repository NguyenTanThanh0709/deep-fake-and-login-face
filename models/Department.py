class Department:
    def __init__(self, department_id, department_name, created_at=None):
        self.department_id = department_id
        self.department_name = department_name
        self.created_at = created_at

    @staticmethod
    def from_dict(data):
        return Department(
            department_id=data.get('department_id'),
            department_name=data.get('department_name'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            "department_id": self.department_id,
            "department_name": self.department_name,
            "created_at": self.created_at
        }
