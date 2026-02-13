# 🤖 Telegram Bot Tiên Nghịch

Bot Telegram hỗ trợ tra cứu và đóng góp thông tin về tác phẩm **Tiên Nghịch** (Nhĩ Căn), bao gồm tiểu thuyết và cả hai phiên bản phim 3D & 2D.

---

## 📋 Mục lục

1. [Tính năng](#-tính-năng)
2. [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
3. [Cài đặt](#-cài-đặt)
4. [Cấu hình](#-cấu-hình)
5. [Chạy bot](#-chạy-bot)
6. [Sử dụng](#-sử-dụng)
7. [Quản trị (Admin)](#-quản-trị-admin)
8. [Database Schema](#-database-schema)
9. [Deploy Production](#-deploy-production)

---

## ✨ Tính năng

### Người dùng thường

- ✅ **Tra cứu thông tin:**
  - Tra theo chương tiểu thuyết
  - Tra theo tập phim 3D
  - Tra theo tập phim 2D
  - Hiển thị đầy đủ quan hệ giữa chương và tập phim
  
- ✅ **Đóng góp thông tin:**
  - Đóng góp mapping (liên kết chương - tập phim)
  - Đóng góp link đọc truyện
  - Đóng góp link xem phim 3D/2D
  - Tất cả đóng góp được kiểm duyệt trước khi áp dụng

### Admin

- ✅ **Quản lý đóng góp:**
  - Xem danh sách đóng góp chờ duyệt
  - Xem chi tiết từng đóng góp
  - Duyệt hoặc từ chối đóng góp
  - Thông báo tự động cho người đóng góp
  
- ✅ **Thống kê:**
  - Tổng số chương, tập phim
  - Số lượng mapping
  - Số đóng góp chờ duyệt

---

## 🏗 Kiến trúc hệ thống

```
┌─────────────────────────────────────┐
│       Telegram Bot (main.py)        │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │   Handlers    │
       │   (Routes)    │
       └───────┬───────┘
               │
       ┌───────┴───────┐
       │   Services    │
       │(Business Logic)│
       └───────┬───────┘
               │
       ┌───────┴───────┐
       │ Repositories  │
       │ (Data Access) │
       └───────┬───────┘
               │
       ┌───────┴───────┐
       │   MongoDB     │
       └───────────────┘
```

### Cấu trúc thư mục

```
tien_nghich_bot/
├── config/              # Cấu hình
├── database/            # Database models & connection
├── repositories/        # Data access layer
├── services/            # Business logic layer
├── handlers/            # Telegram handlers
├── utils/               # Utilities (validators, formatters)
├── main.py             # Entry point
├── requirements.txt    # Dependencies
├── .env               # Environment variables (không commit)
└── README.md          # Documentation
```

---

## 📦 Cài đặt

### Yêu cầu

- Python 3.8+
- MongoDB 4.4+
- Telegram Bot Token (từ [@BotFather](https://t.me/BotFather))

### Bước 1: Clone/Download code

```bash
# Nếu dùng git
git clone <repository-url>
cd tien_nghich_bot

# Hoặc giải nén file zip vào thư mục
```

### Bước 2: Cài đặt Python dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 3: Cài đặt MongoDB

**Option 1: MongoDB Local**

- Download và cài đặt MongoDB Community Edition từ [mongodb.com](https://www.mongodb.com/try/download/community)
- Khởi động MongoDB service

**Option 2: MongoDB Atlas (Cloud - Miễn phí)**

1. Đăng ký tài khoản tại [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Tạo free cluster
3. Tạo database user
4. Whitelist IP address (hoặc 0.0.0.0/0 cho development)
5. Lấy connection string

---

## ⚙️ Cấu hình

### Bước 1: Tạo Telegram Bot

1. Mở Telegram, tìm [@BotFather](https://t.me/BotFather)
2. Gửi lệnh `/newbot`
3. Đặt tên và username cho bot
4. Nhận **Bot Token** (dạng: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Bước 2: Lấy Admin ID

1. Mở Telegram, tìm [@userinfobot](https://t.me/userinfobot)
2. Gửi bất kỳ tin nhắn nào
3. Bot sẽ trả về **User ID** của bạn (ví dụ: `6189828613`)

### Bước 3: Tạo file .env

```bash
# Copy file .env.example
cp .env.example .env

# Hoặc tạo file .env mới
```

Nội dung file `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Admin Configuration
ADMIN_ID=6189828613

# MongoDB Configuration - Local
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=tien_nghich_bot

# MongoDB Configuration - Atlas (Cloud)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
# MONGODB_DATABASE=tien_nghich_bot
```

**⚠️ QUAN TRỌNG:**
- Thay `TELEGRAM_BOT_TOKEN` bằng token thực của bạn
- Thay `ADMIN_ID` bằng User ID của bạn
- Không commit file `.env` lên git

---

## 🚀 Chạy bot

### Development (Local)

```bash
# Activate virtual environment (nếu chưa)
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Chạy bot
python main.py
```

Nếu thành công, bạn sẽ thấy:

```
✅ Settings validated successfully
📦 Creating bot application...
✅ All handlers registered successfully
🚀 Starting bot polling...
👨‍💼 Admin ID: 6189828613
💾 Database: tien_nghich_bot
✅ Connected to MongoDB: tien_nghich_bot
✅ Database indexes created successfully
🚀 Bot is starting up...
✅ Database connected successfully
✅ Startup notification sent to admin
```

### Kiểm tra

1. Mở Telegram, tìm bot của bạn
2. Gửi `/start`
3. Bot sẽ trả lời với menu chính

---

## 📖 Sử dụng

### Lệnh người dùng

#### Tra cứu thông tin

```
/chapter 123        # Tra chương 123
/3d 10             # Tra tập 3D số 10
/2d 5              # Tra tập 2D số 5
```

**Kết quả hiển thị:**
- Thông tin chương/tập được tra
- Danh sách tập phim liên quan (nếu có)
- Danh sách chương liên quan (nếu có)
- Tất cả links có sẵn

#### Đóng góp thông tin

```
/contribute
```

Bot sẽ hướng dẫn qua các bước:

**1. Đóng góp Mapping:**
- Chọn "Mapping (Liên kết chương - tập phim)"
- Nhập chương (ví dụ: `121, 122, 123` hoặc `121-123`)
- Nhập tập 3D (hoặc bỏ qua)
- Nhập tập 2D (hoặc bỏ qua)
- Xác nhận

**2. Đóng góp Link:**
- Chọn loại link (Tiểu thuyết / 3D / 2D)
- Nhập số chương/tập
- Nhập tên website
- Nhập URL đầy đủ
- Xác nhận

**Lưu ý:**
- Tất cả đóng góp sẽ được admin kiểm duyệt
- Bạn sẽ nhận thông báo khi đóng góp được duyệt/từ chối

#### Lệnh khác

```
/help              # Xem hướng dẫn
/cancel            # Hủy thao tác đang làm
```

---

## 👨‍💼 Quản trị (Admin)

### Lệnh Admin

```
/stats                  # Xem thống kê hệ thống
/pending               # Danh sách đóng góp chờ duyệt
/review_<ID>           # Xem chi tiết đóng góp
/approve_<ID>          # Duyệt đóng góp
/reject_<ID>           # Từ chối đóng góp
/adminhelp            # Hướng dẫn admin
```

### Quy trình duyệt đóng góp

1. **Nhận thông báo:** Khi có đóng góp mới, admin sẽ nhận thông báo ngay lập tức

2. **Xem danh sách:**
   ```
   /pending
   ```

3. **Xem chi tiết:**
   ```
   /review_<ID>
   ```
   Thay `<ID>` bằng ID trong danh sách

4. **Duyệt hoặc từ chối:**
   ```
   /approve_<ID>      # Duyệt
   /reject_<ID>       # Từ chối
   ```

5. **Người đóng góp nhận thông báo tự động**

---

## 🗄 Database Schema

### Collection: `novels`

```javascript
{
  _id: ObjectId,
  chapter_number: 123,              // Unique
  title: "Chương 123: Tiêu đề",
  links: [
    {
      source_name: "TruyenFull",
      url: "https://truyenfull.vn/..."
    }
  ],
  created_at: ISODate,
  updated_at: ISODate
}
```

### Collection: `episodes_3d`

```javascript
{
  _id: ObjectId,
  episode_number: 10,               // Unique
  title: "Tập 10: Tiêu đề",
  links: [
    {
      source_name: "YouTube",
      url: "https://youtube.com/..."
    }
  ],
  created_at: ISODate,
  updated_at: ISODate
}
```

### Collection: `episodes_2d`

```javascript
{
  _id: ObjectId,
  episode_number: 5,                // Unique
  title: "Tập 5: Tiêu đề",
  links: [...],
  created_at: ISODate,
  updated_at: ISODate
}
```

### Collection: `mappings`

```javascript
{
  _id: ObjectId,
  novel_chapters: [121, 122, 123],  // Array
  episode_3d: 10,                   // Nullable
  episode_2d: 5,                    // Nullable
  created_at: ISODate,
  updated_at: ISODate
}
```

### Collection: `contributions`

```javascript
{
  _id: ObjectId,
  user_id: 123456789,
  username: "@user",
  contribution_type: "mapping",      // or "novel_link", "episode_3d_link", "episode_2d_link"
  data: {...},                      // Flexible structure
  status: "pending",                // pending, approved, rejected
  admin_note: "",
  submitted_at: ISODate,
  reviewed_at: ISODate,
  reviewed_by: 6189828613
}
```

---

## 🌐 Deploy Production

### Option 1: VPS (Ubuntu)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python & pip
sudo apt install python3 python3-pip python3-venv -y

# 3. Install MongoDB
# Follow: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

# 4. Clone code
git clone <repository-url>
cd tien_nghich_bot

# 5. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Configure .env
nano .env
# Paste cấu hình, save (Ctrl+O, Enter, Ctrl+X)

# 8. Test run
python main.py

# 9. Setup systemd service (chạy tự động)
sudo nano /etc/systemd/system/tien_nghich_bot.service
```

Nội dung file service:

```ini
[Unit]
Description=Tien Nghich Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tien_nghich_bot
Environment="PATH=/path/to/tien_nghich_bot/venv/bin"
ExecStart=/path/to/tien_nghich_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 10. Enable & start service
sudo systemctl daemon-reload
sudo systemctl enable tien_nghich_bot
sudo systemctl start tien_nghich_bot

# 11. Check status
sudo systemctl status tien_nghich_bot

# 12. View logs
sudo journalctl -u tien_nghich_bot -f
```

### Option 2: Heroku

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create tien-nghich-bot

# 4. Add MongoDB addon (mLab hoặc MongoDB Atlas)
heroku addons:create mongolab:sandbox
# Hoặc dùng MongoDB Atlas (free tier)

# 5. Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token_here
heroku config:set ADMIN_ID=6189828613
heroku config:set MONGODB_URI=your_mongodb_uri_here

# 6. Create Procfile
echo "worker: python main.py" > Procfile

# 7. Deploy
git add .
git commit -m "Initial commit"
git push heroku main

# 8. Scale worker
heroku ps:scale worker=1

# 9. View logs
heroku logs --tail
```

### Option 3: Docker

Tạo `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Tạo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    env_file:
      - .env
    depends_on:
      - mongodb
    restart: unless-stopped

  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

volumes:
  mongodb_data:
```

Chạy:

```bash
docker-compose up -d
```

---

## 🛠 Troubleshooting

### Bot không phản hồi

1. Kiểm tra bot đang chạy: `systemctl status tien_nghich_bot`
2. Xem logs: `journalctl -u tien_nghich_bot -f`
3. Kiểm tra token trong `.env`
4. Kiểm tra kết nối MongoDB

### Lỗi MongoDB

1. Kiểm tra MongoDB đang chạy: `systemctl status mongod`
2. Kiểm tra connection string trong `.env`
3. Nếu dùng Atlas, kiểm tra IP whitelist

### Đóng góp không được duyệt tự động

- Đóng góp cần admin duyệt thủ công
- Admin sẽ nhận thông báo ngay lập tức
- Sử dụng `/pending` để xem danh sách

---

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa.

---

## 👥 Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo Pull Request hoặc Issues.

---

## 📞 Liên hệ

- Telegram: [@your_username](https://t.me/your_username)
- Email: your.email@example.com

---

**Happy coding! 🚀**
