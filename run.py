from app import create_app
from extensions import db

app = create_app()

def init_database():
    """สร้างฐานข้อมูลและตารางทั้งหมด"""
    with app.app_context():
        db.create_all()
        print("✓ สร้างฐานข้อมูลเรียบร้อย")

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
