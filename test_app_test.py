import os
import json
import unittest
import tempfile
from test_app import app

class TestAIOrchestration(unittest.TestCase):
    def setUp(self):
        # สร้างไฟล์ฐานข้อมูลชั่วคราว
        self.temp_dir = tempfile.mkdtemp()
        app.config['TESTING'] = True
        self.client = app.test_client()

        # สร้างไฟล์ข้อมูลตัวอย่าง
        self.agents_file = os.path.join(self.temp_dir, 'agents.json')
        self.webhooks_file = os.path.join(self.temp_dir, 'webhooks.json')
        
        # กำหนดพาธของไฟล์ข้อมูลใน app
        app.config['AGENTS_FILE'] = self.agents_file
        app.config['WEBHOOKS_FILE'] = self.webhooks_file
        
        # ข้อมูลตัวอย่างสำหรับทดสอบ
        self.sample_agent = {
            'name': 'Test Agent',
            'description': 'Test Description',
            'type': 'customer_service'
        }

    def tearDown(self):
        # ลบไฟล์ทดสอบหลังจากทดสอบเสร็จ
        if os.path.exists(self.agents_file):
            os.remove(self.agents_file)
        if os.path.exists(self.webhooks_file):
            os.remove(self.webhooks_file)
        os.rmdir(self.temp_dir)

    def test_index_page(self):
        """ทดสอบหน้าหลัก"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Orchestration', response.data)
        self.assertIn(b'\xe0\xb8\xa3\xe0\xb8\xb0\xe0\xb8\x9a\xe0\xb8\x9a\xe0\xb8\x88\xe0\xb8\xb1\xe0\xb8\x94\xe0\xb8\x81\xe0\xb8\xb2\xe0\xb8\xa3 AI', response.data)  # "ระบบจัดการ AI" in UTF-8

    def test_agents_page(self):
        """ทดสอบหน้าจัดการ AI Agents"""
        # สร้าง Agent ตัวอย่าง
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump([{'id': 1, **self.sample_agent}], f)

        response = self.client.get('/agents')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Agent', response.data)
        self.assertIn(b'Test Description', response.data)

    def test_create_agent(self):
        """ทดสอบการสร้าง Agent ใหม่"""
        # ทดสอบหน้าฟอร์มสร้าง Agent
        response = self.client.get('/agents/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'\xe0\xb8\xaa\xe0\xb8\xa3\xe0\xb9\x89\xe0\xb8\xb2\xe0\xb8\x87 Agent \xe0\xb9\x83\xe0\xb8\xab\xe0\xb8\xa1\xe0\xb9\x88', response.data)  # "สร้าง Agent ใหม่" in UTF-8

        # ทดสอบการส่งข้อมูลสร้าง Agent
        response = self.client.post('/agents/new', data=self.sample_agent)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # ตรวจสอบว่าข้อมูลถูกบันทึก
        with open(self.agents_file, 'r', encoding='utf-8') as f:
            agents = json.load(f)
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]['name'], self.sample_agent['name'])

    def test_edit_agent(self):
        """ทดสอบการแก้ไข Agent"""
        # สร้าง Agent ตัวอย่าง
        initial_agent = {'id': 1, **self.sample_agent}
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump([initial_agent], f)

        # ทดสอบหน้าแก้ไข Agent
        response = self.client.get('/agents/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Agent', response.data)
        self.assertIn(b'Test Description', response.data)

        # ทดสอบการแก้ไขข้อมูล
        updated_data = {
            'name': 'Updated Agent',
            'description': 'Updated Description',
            'type': 'customer_service'
        }
        response = self.client.post('/agents/1/edit', data=updated_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # ตรวจสอบว่าข้อมูลถูกอัพเดท
        with open(self.agents_file, 'r', encoding='utf-8') as f:
            agents = json.load(f)
            self.assertEqual(agents[0]['name'], 'Updated Agent')
            self.assertEqual(agents[0]['description'], 'Updated Description')

    def test_delete_agent(self):
        """ทดสอบการลบ Agent"""
        # สร้าง Agent ตัวอย่าง
        initial_agent = {'id': 1, **self.sample_agent}
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump([initial_agent], f)

        # ทดสอบการลบ Agent
        response = self.client.post('/agents/1/delete')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # ตรวจสอบว่าข้อมูลถูกลบ
        with open(self.agents_file, 'r', encoding='utf-8') as f:
            agents = json.load(f)
            self.assertEqual(len(agents), 0)

    def test_invalid_agent_id(self):
        """ทดสอบการเข้าถึง Agent ที่ไม่มีอยู่"""
        response = self.client.get('/agents/999/edit')
        self.assertEqual(response.status_code, 302)  # Should redirect to agents page

if __name__ == '__main__':
    unittest.main()
