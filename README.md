# AI Orchestration System

ระบบจัดการ AI ที่สามารถสร้างและจัดการ Sub-agents ได้ โดยมี AI Manager ทำหน้าที่วิเคราะห์และส่งต่องานให้ Sub-agents ที่เหมาะสม

## คุณสมบัติหลัก

- **AI Manager**: วิเคราะห์ข้อความและเลือก Sub-agent ที่เหมาะสม
- **Sub-agents**: AI ที่ถูกสร้างขึ้นเพื่อจัดการงานเฉพาะด้าน
- **Webhook System**: รองรับการเชื่อมต่อกับ LINE OA และระบบภายนอก
- **Training System**: สามารถเพิ่มข้อมูลสำหรับการเทรน Sub-agents
- **Web Interface**: จัดการระบบผ่าน Web UI

## การติดตั้ง

1. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

2. ตั้งค่าไฟล์ .env:
```env
DATABASE_URL=mssql+pyodbc://username:password@host/database?driver=ODBC+Driver+17+for+SQL+Server
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

3. สร้างฐานข้อมูล:
```python
python app.py
```

## โครงสร้างโปรเจกต์

```
ai_orchestration/
├── ai/                    # โค้ดส่วน AI
│   ├── __init__.py
│   ├── manager.py        # AI Manager
│   └── sub_agent.py      # Sub-agent class
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── webhook_routes.py # Webhook endpoints
│   └── agent_routes.py   # Agent management endpoints
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── project.py       # Project model
│   ├── ai_agent.py      # AI Agent model
│   ├── webhook.py       # Webhook model
│   └── training_data.py # Training data model
├── templates/           # Web UI templates
├── app.py              # Main application
├── extensions.py       # Flask extensions
└── requirements.txt    # Project dependencies
```

## การใช้งาน

1. **การสร้าง Sub-agent**:
   - เข้าสู่ระบบผ่าน Web UI
   - สร้างโปรเจกต์ใหม่
   - เพิ่ม Sub-agent และกำหนด prompt template

2. **การสร้าง Webhook**:
   - เลือก Sub-agent ที่ต้องการ
   - สร้าง Webhook URL
   - นำ URL และ Secret key ไปตั้งค่าใน LINE OA หรือระบบอื่นๆ

3. **การเทรน Sub-agent**:
   - เข้าไปที่หน้า Sub-agent
   - เพิ่มข้อมูลสำหรับการเทรน (input และ expected output)
   - อัพเดท prompt template ตามต้องการ

## API Endpoints

### Webhook
- `POST /api/webhook/<url_path>`: รับข้อมูลจาก webhook
- `GET /api/webhook/logs/<webhook_id>`: ดูประวัติการเรียกใช้ webhook

### Agent Management
- `POST /api/agents`: สร้าง Sub-agent ใหม่
- `POST /api/agents/<agent_id>/training-data`: เพิ่มข้อมูลสำหรับการเทรน
- `PUT /api/agents/<agent_id>/prompt`: อัพเดท prompt template
- `GET /api/agents/<agent_id>/training-data`: ดูข้อมูลการเทรนทั้งหมด

## การพัฒนาต่อ

1. เพิ่มความสามารถในการใช้ AI Model อื่นๆ นอกจาก OpenAI
2. เพิ่มระบบ monitoring และ analytics
3. เพิ่มความสามารถในการทำ A/B testing สำหรับ prompts
4. รองรับการทำงานแบบ multi-tenant
5. เพิ่มระบบ authentication สำหรับ API
