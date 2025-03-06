# AI Orchestration System

ระบบจัดการ AI แบบ Multi-tenant ที่มีความยืดหยุ่นและปลอดภัย สามารถจัดการ AI Sub-Agents และการประมวลผลข้อความได้อย่างมีประสิทธิภาพ

## คุณสมบัติหลัก

- **Multi-tenant Architecture**: รองรับหลายองค์กรในระบบเดียว พร้อมการแยกข้อมูลและการเข้าถึง
- **AI Sub-Agent Management**: จัดการและกำหนดค่า AI Sub-Agents ได้อย่างยืดหยุ่น
- **ความปลอดภัย**: ระบบ RBAC และการยืนยันตัวตนด้วย JWT
- **การติดตามและวิเคราะห์**: บันทึกและวิเคราะห์การใช้งานอย่างละเอียด
- **Webhook Integration**: รองรับการเชื่อมต่อกับระบบภายนอกผ่าน webhooks
- **Rate Limiting**: ควบคุมการใช้งาน API อย่างมีประสิทธิภาพ
- **Template Management**: จัดการ prompt templates สำหรับ AI Sub-Agents

## การติดตั้ง

1. Clone repository:
```bash
git clone https://github.com/yourusername/ai-orchestration.git
cd ai-orchestration
```

2. สร้าง virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

4. ตั้งค่า environment variables:
```bash
cp .env.example .env
# แก้ไขไฟล์ .env ตามการตั้งค่าของคุณ
```

5. สร้างฐานข้อมูล:
```bash
flask db upgrade
```

## การใช้งาน

1. รัน development server:
```bash
flask run
```

2. เข้าถึง API ที่:
- API Endpoint: `http://localhost:5000/api`
- Admin Dashboard: `http://localhost:5000/admin`

## API Endpoints

### Authentication
- `POST /api/auth/login`: เข้าสู่ระบบและรับ JWT token
- `POST /api/auth/register`: ลงทะเบียนผู้ใช้ใหม่

### AI Processing
- `POST /api/process`: ประมวลผลข้อความด้วย AI
- `GET /api/agents`: ดูรายการ AI Sub-Agents ที่มี

### Admin API
- `POST /api/admin/agents`: สร้าง AI Sub-Agent ใหม่
- `GET /api/admin/stats`: ดูสถิติการใช้งาน

## การ Deploy

### Deploy บน Render

1. เชื่อมต่อ GitHub repository กับ Render

2. Render จะตั้งค่าบริการต่อไปนี้อัตโนมัติ:
   - Web service สำหรับ AI Orchestration
   - MySQL database
   - Redis cache

3. ตั้งค่า Environment Variables บน Render ตามที่ระบุใน `.env.example`

### Deploy แบบ Manual

1. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

2. ตั้งค่า environment variables

3. รัน production server:
```bash
gunicorn app:create_app() --bind 0.0.0.0:$PORT
```

## การพัฒนา

### โครงสร้างโปรเจค

ดูรายละเอียดเพิ่มเติมได้ที่ [docs/project_structure.md](docs/project_structure.md)

### การทดสอบ

รันชุดทดสอบ:
```bash
pytest
```

รันพร้อม coverage report:
```bash
pytest --cov=app tests/
```

## License

MIT License - ดูรายละเอียดเพิ่มเติมได้ที่ [LICENSE](LICENSE)
