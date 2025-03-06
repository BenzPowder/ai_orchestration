# โครงสร้างโปรเจกต์ AI Orchestration

## โครงสร้างไดเรกทอรี

```
ai_orchestration/
├── app/
│   ├── __init__.py
│   ├── config.py              # การตั้งค่าแอปพลิเคชัน
│   ├── routes/
│   │   ├── __init__.py
│   │   └── line_webhook.py    # จัดการ webhook จาก LINE
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── manager.py         # AI Manager (Main Agent)
│   │   └── sub_agents/        # AI Sub-Agents ต่างๆ
│   │       ├── __init__.py
│   │       └── base.py        # คลาสพื้นฐานสำหรับ Sub-Agents
│   ├── models/
│   │   ├── __init__.py
│   │   └── conversation.py    # โมเดลข้อมูลการสนทนา
│   ├── services/
│   │   ├── __init__.py
│   │   ├── line_service.py    # บริการเชื่อมต่อกับ LINE API
│   │   ├── mongodb_service.py # บริการจัดการฐานข้อมูล MongoDB
│   │   └── openai_service.py  # บริการเชื่อมต่อกับ OpenAI
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # ฟังก์ชันช่วยเหลือต่างๆ
├── docs/
│   └── project_structure.md   # เอกสารนี้
├── tests/
│   └── __init__.py
├── .env.example              # ตัวอย่างไฟล์ตั้งค่าสภาพแวดล้อม
├── .gitignore
├── app.py                    # Entry point ของแอปพลิเคชัน
├── README.md
└── requirements.txt          # รายการ dependencies
```

## รายละเอียดของแต่ละโมดูล

### 1. app/config.py
- เก็บการตั้งค่าต่างๆ ของแอปพลิเคชัน
- โหลดค่าจาก environment variables
- กำหนดค่าคงที่ต่างๆ ที่ใช้ในระบบ

### 2. app/routes/
- **line_webhook.py**: จัดการการรับส่งข้อมูลผ่าน LINE Webhook
  - รับข้อความจากผู้ใช้
  - ส่งต่อไปยัง AI Manager
  - ส่งการตอบกลับไปยังผู้ใช้

### 3. app/agents/
- **manager.py**: AI Manager หลัก
  - วิเคราะห์ข้อความด้วย LangChain
  - ตัดสินใจเลือก Sub-Agent ที่เหมาะสม
  - ประสานงานระหว่าง Sub-Agents

- **sub_agents/base.py**: คลาสพื้นฐานสำหรับ Sub-Agents
  - กำหนดโครงสร้างและวิธีการทำงานพื้นฐาน
  - รองรับการเพิ่ม Sub-Agents ใหม่ในอนาคต

### 4. app/models/
- **conversation.py**: โมเดลข้อมูลการสนทนา
  - โครงสร้างข้อมูลสำหรับเก็บประวัติการสนทนา
  - เก็บข้อมูลการวิเคราะห์และการตอบกลับ

### 5. app/services/
- **line_service.py**: จัดการการเชื่อมต่อกับ LINE API
  - ส่งข้อความตอบกลับ
  - จัดการ rich menu และฟีเจอร์อื่นๆ ของ LINE

- **mongodb_service.py**: จัดการการเชื่อมต่อกับ MongoDB
  - CRUD operations
  - Full-Text Search
  - Vector Search ด้วย Atlas Vector

- **openai_service.py**: จัดการการเชื่อมต่อกับ OpenAI
  - สร้าง embeddings
  - เรียกใช้ AI models

### 6. app/utils/
- **helpers.py**: ฟังก์ชันช่วยเหลือต่างๆ
  - แปลงรูปแบบข้อมูล
  - Logging
  - Utility functions อื่นๆ

### 7. tests/
- เก็บ test cases ทั้งหมด
- Unit tests
- Integration tests

## การเพิ่ม Sub-Agent ใหม่

1. สร้างไฟล์ใหม่ใน `app/agents/sub_agents/`
2. Inherit จาก `base.py`
3. implement วิธีการทำงานเฉพาะของ agent
4. ลงทะเบียน agent ใหม่กับ AI Manager

## การจัดการ Dependencies

- ใช้ `requirements.txt` สำหรับจัดการ dependencies
- ระบุเวอร์ชันที่แน่นอนเพื่อป้องกันปัญหาความเข้ากันได้
- แยก dependencies สำหรับ development และ production

## การ Deploy

1. สร้าง project ใหม่บน Render.com
2. เชื่อมต่อกับ GitHub repository
3. ตั้งค่า environment variables
4. กำหนด build command และ start command
5. ตั้งค่า webhook URL ใน LINE Developer Console
