class Employee:
    def __init__(self, maNhanVien, tenNhanVien, email, sdt, password, vaiTro, photo_reference, role, is_active, department_id, created_at=None):
        self.maNhanVien = maNhanVien
        self.tenNhanVien = tenNhanVien
        self.email = email
        self.sdt = sdt
        self.password = password
        self.vaiTro = vaiTro
        self.photo_reference = photo_reference
        self.role = role
        self.is_active = is_active
        self.department_id = department_id
        self.created_at = created_at

    @staticmethod
    def from_dict(data):
        return Employee(
            maNhanVien=data.get('maNhanVien'),
            tenNhanVien=data.get('tenNhanVien'),
            email=data.get('email'),
            sdt=data.get('sdt'),
            password=data.get('password'),
            vaiTro=data.get('vaiTro'),
            photo_reference=data.get('photo_reference'),
            role=data.get('role'),
            is_active=data.get('IsActive'),
            department_id=data.get('department_id'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            "maNhanVien": self.maNhanVien,
            "tenNhanVien": self.tenNhanVien,
            "email": self.email,
            "sdt": self.sdt,
            "password": self.password,
            "vaiTro": self.vaiTro,
            "photo_reference": self.photo_reference,
            "role": self.role,
            "is_active": self.is_active,
            "department_id": self.department_id,
            "created_at": self.created_at
        }
