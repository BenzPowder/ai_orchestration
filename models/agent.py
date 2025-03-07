class Agent:
    def __init__(self, id=None, name=None, description=None, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.webhooks = []  # รายการ webhook ที่เชื่อมต่อกับ agent นี้
        self.training_data = []  # รายการข้อมูลเทรนของ agent นี้
