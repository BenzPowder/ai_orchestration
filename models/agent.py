class Agent:
    def __init__(self, id=None, name=None, description=None, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.webhooks = []  # รายการ webhook ที่เชื่อมต่อกับ agent นี้
        self.training_data = []  # รายการข้อมูลเทรนของ agent นี้
        self.type = None  # ประเภทของ agent

    def __iter__(self):
        """ทำให้ Agent สามารถแปลงเป็น list ได้"""
        yield self

    def to_dict(self):
        """แปลง Agent เป็น dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'webhooks': [webhook.to_dict() for webhook in self.webhooks] if self.webhooks else [],
            'training_data': self.training_data if self.training_data else [],
            'type': self.type
        }

    @property
    def type_display(self):
        """แสดงชื่อประเภท Agent เป็นภาษาไทย"""
        type_map = {
            'chat': 'แชทบอท',
            'task': 'ทำงานตามคำสั่ง',
            'manager': 'จัดการระบบ',
            'customer_service': 'บริการลูกค้า'
        }
        return type_map.get(self.type, 'ไม่ระบุประเภท')

    @property
    def description_short(self):
        """แสดงคำอธิบายแบบย่อ"""
        if not self.description:
            return ''
        if len(self.description) <= 100:
            return self.description
        return self.description[:97] + '...'
