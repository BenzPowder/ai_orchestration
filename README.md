# AI Orchestration System

ระบบจัดการและประสานงานระหว่าง AI Agents เพื่อเพิ่มประสิทธิภาพในการทำงานและตอบสนองความต้องการของผู้ใช้

## โครงสร้างระบบ

### 1. AI Manager (Main Agent)
- ทำหน้าที่เป็นผู้จัดการหลักในการรับข้อความจากผู้ใช้
- วิเคราะห์และจำแนกประเภทข้อความว่าเกี่ยวข้องกับโปรเจกต์ใด
- ส่งต่อคำสั่งไปยัง AI Sub-Agents ที่เหมาะสม
- ใช้ LangChain Agent ในการวิเคราะห์ข้อความ

### 2. AI Sub-Agents (Specialized AI)
- AI เฉพาะทางที่มีความเชี่ยวชาญในแต่ละด้าน
- สามารถเพิ่มจำนวน Agents ได้ตามความต้องการ
- ทำงานร่วมกับ AI Manager เพื่อประมวลผลและตอบกลับผู้ใช้

### 3. Database & API Integration
- ใช้ MongoDB ในการจัดเก็บข้อมูล
  - เก็บประวัติการสนทนา คำถาม-คำตอบ
  - รองรับ Full-Text Search และ Vector Search (Atlas Vector)
- LINE Official Account API สำหรับการติดต่อกับผู้ใช้
- OpenAI API สำหรับการประมวลผลและตอบกลับ

## เทคโนโลยีที่ใช้
- Python Flask - Web Framework
- LangChain - AI Agent Framework
- MongoDB - ฐานข้อมูล
- OpenAI - AI Model
- LINE OA API - ช่องทางการสื่อสาร
- Render - Cloud Hosting Platform

## การติดตั้ง
1. ติดตั้ง Python 3.8 ขึ้นไป
2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

## การตั้งค่า
1. สร้างไฟล์ `.env` และกำหนดค่าต่อไปนี้:
```
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=your_mongodb_uri
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```

## การใช้งาน
1. รันเซิร์ฟเวอร์:
```bash
python app.py
```
2. เซิร์ฟเวอร์จะทำงานที่ `http://localhost:5000`

## การ Deploy
- ใช้ Render.com สำหรับ deployment
- ตั้งค่า environment variables ใน Render dashboard
- เชื่อมต่อกับ GitHub repository สำหรับ automatic deployment
