class Company:
    def __init__(self, name, address, email, phone, latitude, longitude,sdtAdmin, created_at, updated_at, ):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.latitude = latitude
        self.longitude = longitude
        self.updated_at = updated_at
        self.created_at = created_at
        self.sdtAdmin = sdtAdmin

    @staticmethod
    def from_dict(data):
        return Company(
            name=data.get('name'),
            address=data.get('address'),
            email=data.get('email'),
            phone=data.get('phone'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            updated_at=data.get('updated_at'),
            created_at=data.get('created_at'),
            sdtAdmin=data.get('sdtAdmin')
        )

def to_dict(self):
    return {
        "name": self.name,
        "address": self.address,
        "email": self.email,
        "phone": self.phone,
        "latitude": self.latitude,
        "longitude": self.longitude,
        "sdtAdmin": self.sdtAdmin,
        "created_at": self.created_at,
        "updated_at": self.updated_at
    }

