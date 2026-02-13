# ⚡ QUICKSTART GUIDE - Bot Tiên Nghịch

Hướng dẫn nhanh để chạy bot trong **5 phút**!

---

## 🎯 Prerequisites

- ✅ Python 3.8+ đã cài đặt
- ✅ MongoDB đang chạy (local hoặc cloud)
- ✅ Telegram Bot Token (từ @BotFather)
- ✅ Telegram User ID của bạn (từ @userinfobot)

---

## 📦 Bước 1: Cài đặt

### Windows:

```cmd
# Giải nén file tien_nghich_bot.tar.gz
# Hoặc clone từ git

cd tien_nghich_bot

# Tạo virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt
```

### Linux/Mac:

```bash
# Giải nén
tar -xzf tien_nghich_bot.tar.gz
cd tien_nghich_bot

# Tạo virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

---

## ⚙️ Bước 2: Cấu hình

### 2.1 Tạo file `.env`

```bash
cp .env.example .env
```

### 2.2 Chỉnh sửa `.env`

Mở file `.env` và điền thông tin:

```env
# 1. Bot Token từ @BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# 2. User ID từ @userinfobot
ADMIN_ID=6189828613

# 3. MongoDB (chọn một trong hai)

# Option A: Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=tien_nghich_bot

# Option B: MongoDB Atlas (Cloud)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
# MONGODB_DATABASE=tien_nghich_bot
```

**Lưu ý:**
- Thay `TELEGRAM_BOT_TOKEN` bằng token thật
- Thay `ADMIN_ID` bằng User ID của bạn
- Uncomment (bỏ #) dòng MongoDB bạn dùng

---

## 🚀 Bước 3: Chạy Bot

```bash
python main.py
```

### ✅ Thành công khi thấy:

```
✅ Settings validated successfully
✅ Connected to MongoDB: tien_nghich_bot
✅ Database indexes created successfully
✅ All handlers registered successfully
🚀 Starting bot polling...
```

### ❌ Lỗi thường gặp:

**1. ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**2. MongoDB connection failed**
- Kiểm tra MongoDB đang chạy
- Kiểm tra MONGODB_URI trong .env

**3. Invalid token**
- Kiểm tra TELEGRAM_BOT_TOKEN trong .env
- Đảm bảo không có khoảng trắng thừa

---

## 🧪 Bước 4: Kiểm tra

### 4.1 Mở Telegram, tìm bot của bạn

### 4.2 Test commands:

```
/start          ← Xem menu chính
/help           ← Xem hướng dẫn
/chapter 1      ← Test tra cứu (sẽ không có data)
/contribute     ← Test đóng góp
```

### 4.3 Test admin commands (với tài khoản admin):

```
/stats          ← Xem thống kê (ban đầu sẽ là 0)
/pending        ← Xem đóng góp chờ duyệt
/adminhelp      ← Hướng dẫn admin
```

---

## 📝 Bước 5: Thêm dữ liệu mẫu (Optional)

### Sử dụng MongoDB Shell hoặc MongoDB Compass

```javascript
// Connect to: mongodb://localhost:27017/tien_nghich_bot

// Thêm novel chapter
db.novels.insertOne({
  chapter_number: 1,
  title: "Chương 1: Khởi đầu",
  links: [
    {
      source_name: "TruyenFull",
      url: "https://truyenfull.vn/tien-nghich/chuong-1/"
    }
  ],
  created_at: new Date(),
  updated_at: new Date()
})

// Thêm episode 3D
db.episodes_3d.insertOne({
  episode_number: 1,
  title: "Tập 1: Ra đời",
  links: [
    {
      source_name: "YouTube",
      url: "https://youtube.com/watch?v=..."
    }
  ],
  created_at: new Date(),
  updated_at: new Date()
})

// Thêm mapping
db.mappings.insertOne({
  novel_chapters: [1, 2, 3],
  episode_3d: 1,
  episode_2d: null,
  created_at: new Date(),
  updated_at: new Date()
})
```

### Hoặc đóng góp qua bot:

```
/contribute
→ Chọn "Mapping"
→ Nhập "1-3"
→ Nhập "1" (tập 3D)
→ Bỏ qua tập 2D
```

Sau đó dùng tài khoản admin:
```
/pending
/approve_<ID>
```

---

## 🎉 Done!

Bot của bạn đã hoạt động!

### 📚 Đọc thêm:

- **README.md** - Hướng dẫn đầy đủ
- **ARCHITECTURE.md** - Giải thích kiến trúc
- **Cấu trúc thư mục** - Xem code trong các folder

### 🔧 Customize:

1. **Thay đổi emoji** - Sửa `utils/constants.py`
2. **Thay đổi messages** - Sửa các handler trong `handlers/`
3. **Thêm chức năng** - Tạo handler mới và đăng ký trong `main.py`

---

## 💡 Tips

### Development:

```bash
# Xem logs real-time
python main.py

# Ctrl+C để dừng
```

### Production:

```bash
# Chạy background (Linux)
nohup python main.py > bot.log 2>&1 &

# Hoặc dùng systemd (xem README.md)
```

### Debug:

```python
# Thêm vào đầu main.py
logging.basicConfig(level=logging.DEBUG)
```

---

## 🆘 Cần giúp?

1. Đọc **README.md** - Section Troubleshooting
2. Check logs: `journalctl -u tien_nghich_bot -f`
3. Xem MongoDB data: MongoDB Compass
4. Test commands riêng lẻ

---

## 🚀 Next Steps

1. ✅ Bot chạy được → Đọc **README.md** để deploy production
2. ✅ Thêm data mẫu → Test đầy đủ chức năng
3. ✅ Customize → Chỉnh sửa theo ý muốn
4. ✅ Deploy → VPS/Heroku/Docker

---

**Happy coding! 🎊**
