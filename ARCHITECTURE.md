# 🏗 KIẾN TRÚC HỆ THỐNG - TELEGRAM BOT TIÊN NGHỊCH

## 📐 Tổng quan kiến trúc

Hệ thống được xây dựng theo mô hình **Layered Architecture** với sự tách biệt rõ ràng giữa các layer:

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                  (Telegram Bot Interface)                    │
│                         main.py                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      HANDLER LAYER                           │
│        (Process user requests & bot commands)                │
│   start_handler | search_handler | contribute_handler        │
│                    admin_handler                             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                     SERVICE LAYER                            │
│                (Business Logic & Rules)                      │
│  SearchService | ContributionService | AdminService          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   REPOSITORY LAYER                           │
│              (Data Access & Persistence)                     │
│  NovelRepo | EpisodeRepo | MappingRepo | ContributionRepo   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      DATA LAYER                              │
│                     MongoDB Database                         │
│  novels | episodes_3d | episodes_2d | mappings | contributions│
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Các Layer chi tiết

### 1. **Presentation Layer** (main.py)

**Trách nhiệm:**
- Khởi tạo Telegram Bot Application
- Đăng ký các handlers
- Quản lý lifecycle (startup, shutdown)
- Kết nối database

**Luồng hoạt động:**
```python
1. Validate settings (.env)
2. Create Telegram Application
3. Setup handlers (commands, conversations)
4. Connect to MongoDB
5. Start polling (nhận messages từ Telegram)
6. Route messages to appropriate handlers
```

---

### 2. **Handler Layer** (handlers/)

Xử lý tương tác với người dùng qua Telegram.

#### **start_handler.py**
- `/start` - Welcome message
- `/help` - Hướng dẫn sử dụng

#### **search_handler.py**
- `/chapter <số>` - Tra chương
- `/3d <số>` - Tra tập 3D
- `/2d <số>` - Tra tập 2D

**Flow:**
```
User sends: /chapter 123
↓
Validate input (validators.py)
↓
Call SearchService.search_by_chapter(123)
↓
Format result (formatters.py)
↓
Send back to user
```

#### **contribute_handler.py**
- `/contribute` - Bắt đầu đóng góp

**ConversationHandler States:**
```
CHOOSE_TYPE → Chọn loại đóng góp
  ├─ MAPPING → MAPPING_CHAPTERS → MAPPING_EP_3D → MAPPING_EP_2D
  ├─ NOVEL_LINK → LINK_NUMBER → LINK_SOURCE → LINK_URL
  ├─ 3D_LINK → LINK_NUMBER → LINK_SOURCE → LINK_URL
  └─ 2D_LINK → LINK_NUMBER → LINK_SOURCE → LINK_URL
```

**Flow đóng góp Mapping:**
```
1. User: /contribute
2. Bot: Chọn loại → User chọn "Mapping"
3. Bot: Nhập chương → User: "121-123"
4. Bot: Nhập tập 3D → User: "10"
5. Bot: Nhập tập 2D → User: "Bỏ qua"
6. ContributionService.submit_mapping_contribution()
7. Save to DB với status="pending"
8. Notify admin ngay lập tức
9. Confirm với user
```

#### **admin_handler.py**
- `/stats` - Thống kê
- `/pending` - Danh sách đóng góp chờ duyệt
- `/review_<id>` - Xem chi tiết
- `/approve_<id>` - Duyệt đóng góp
- `/reject_<id>` - Từ chối đóng góp

**Flow duyệt đóng góp:**
```
1. Admin: /approve_<id>
2. Get contribution from DB
3. Validate status = "pending"
4. Apply contribution:
   - If mapping → Create new Mapping
   - If link → Add link to Novel/Episode
5. Update contribution status = "approved"
6. Notify contributor
7. Confirm to admin
```

---

### 3. **Service Layer** (services/)

Chứa business logic, không biết về Telegram hay Database details.

#### **SearchService**
```python
search_by_chapter(chapter_number):
  1. Find novel chapter
  2. Find mappings containing this chapter
  3. Extract episode numbers from mappings
  4. Find episodes (3D & 2D)
  5. Return comprehensive result
```

#### **ContributionService**
```python
submit_mapping_contribution():
  1. Validate input (at least one episode)
  2. Create Contribution object (status=pending)
  3. Save to contributions collection
  4. Return success/failure

approve_contribution():
  1. Get contribution by ID
  2. Validate status = pending
  3. Apply based on type:
     - mapping → _apply_mapping_contribution()
     - link → _apply_link_contribution()
  4. Mark as approved
  5. Return success/failure
```

#### **AdminService**
```python
get_statistics():
  Count from all collections
  Return summary
```

---

### 4. **Repository Layer** (repositories/)

Trực tiếp tương tác với MongoDB. Mỗi repository quản lý một collection.

#### **NovelRepository**
```python
Collection: novels

Methods:
- find_by_chapter_number(chapter_number)
- find_by_chapter_numbers([121, 122, 123])
- create(novel)
- update(novel)
- add_link(chapter_number, link)
```

#### **EpisodeRepository**
```python
Collection: episodes_3d / episodes_2d

Constructor: EpisodeRepository("3d") or EpisodeRepository("2d")

Methods:
- find_by_episode_number(episode_number)
- find_by_episode_numbers([10, 11, 12])
- create(episode)
- update(episode)
- add_link(episode_number, link)
```

#### **MappingRepository**
```python
Collection: mappings

Methods:
- find_by_chapter(chapter_number)
- find_by_episode_3d(episode_number)
- find_by_episode_2d(episode_number)
- create(mapping)
```

#### **ContributionRepository**
```python
Collection: contributions

Methods:
- create(contribution)
- find_by_id(contribution_id)
- find_pending()
- approve(contribution_id, admin_id)
- reject(contribution_id, admin_id)
```

---

## 🔄 Luồng dữ liệu chính

### 1. **Tra cứu chương 123**

```
User: /chapter 123
  ↓
search_handler.search_chapter_command()
  ↓ validate_chapter_number("123")
  ↓ SearchService.search_by_chapter(123)
    ↓ NovelRepository.find_by_chapter_number(123)
    ↓ MappingRepository.find_by_chapter(123)
    ↓ EpisodeRepository.find_by_episode_numbers([10])
  ↓ format_search_result(novels, episodes_3d, episodes_2d, mappings)
  ↓
Bot: [Formatted result with all info]
```

### 2. **Đóng góp Mapping**

```
User: /contribute
  ↓
contribute_handler.contribute_start()
  ↓ Show options
User: "Mapping"
  ↓
State: MAPPING_CHAPTERS
User: "121-123"
  ↓ validate_chapter_list("121-123")
  ↓ Store: chapters = [121, 122, 123]
State: MAPPING_EP_3D
User: "10"
  ↓ validate_episode_number("10")
  ↓ Store: episode_3d = 10
State: MAPPING_EP_2D
User: "Bỏ qua"
  ↓ Store: episode_2d = None
  ↓ ContributionService.submit_mapping_contribution()
    ↓ Create Contribution(status="pending")
    ↓ ContributionRepository.create()
  ↓ notify_admin_new_contribution()
    ↓ Send message to ADMIN_ID
  ↓
Bot → User: "Đã gửi, chờ admin duyệt"
Bot → Admin: [Detailed contribution with approve/reject buttons]
```

### 3. **Admin duyệt đóng góp**

```
Admin: /approve_<id>
  ↓
admin_handler.admin_approve_command()
  ↓ ContributionService.approve_contribution(id, admin_id)
    ↓ ContributionRepository.find_by_id(id)
    ↓ Validate status == "pending"
    ↓ Apply contribution:
      - For mapping: MappingRepository.create(mapping)
      - For link: NovelRepository.add_link() / EpisodeRepository.add_link()
    ↓ ContributionRepository.approve(id)
  ↓ notify_contributor()
    ↓ Send message to contributor's user_id
  ↓
Bot → Admin: "Đã duyệt thành công"
Bot → Contributor: "Đóng góp của bạn đã được duyệt!"
```

---

## 📊 Database Design Rationale

### **Tại sao tách thành 5 collections?**

1. **novels, episodes_3d, episodes_2d**: Lưu thông tin cơ bản + links
   - Dễ query
   - Dễ thêm links mới
   - Tránh duplicate data

2. **mappings**: Quan hệ nhiều-nhiều
   - Một chương có thể trong nhiều tập
   - Một tập có thể có nhiều chương
   - Flexible: episode_3d và episode_2d đều nullable

3. **contributions**: Workflow riêng
   - Pending → Approved/Rejected
   - Lưu lịch sử đóng góp
   - Audit trail

### **Indexes**

```javascript
// Optimize searches
novels.createIndex({ chapter_number: 1 }, { unique: true })
episodes_3d.createIndex({ episode_number: 1 }, { unique: true })
episodes_2d.createIndex({ episode_number: 1 }, { unique: true })

// Optimize mapping lookups
mappings.createIndex({ novel_chapters: 1 })
mappings.createIndex({ episode_3d: 1 })
mappings.createIndex({ episode_2d: 1 })

// Optimize admin workflow
contributions.createIndex({ status: 1 })
contributions.createIndex({ submitted_at: -1 })
```

---

## 🛡 Error Handling & Validation

### **3-tier validation:**

1. **Input Validation** (utils/validators.py)
   ```python
   validate_chapter_number("abc") → (False, None, "Không hợp lệ")
   validate_url("invalid") → (False, "URL không hợp lệ")
   ```

2. **Business Logic Validation** (services/)
   ```python
   # Must have at least one episode
   if not episode_3d and not episode_2d:
       return False, "Phải có ít nhất một tập"
   ```

3. **Database Validation** (repositories/)
   ```python
   # Check duplicates
   existing = find_by_chapter_number(123)
   if existing:
       return existing  # Don't create duplicate
   ```

### **Error handling pattern:**

```python
try:
    # Main logic
    result = service.do_something()
    return success_response(result)
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return error_response("User-friendly message")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return error_response("Lỗi hệ thống")
```

---

## 🔐 Security Considerations

1. **Admin authorization:**
   ```python
   if user_id != settings.ADMIN_ID:
       return "Access denied"
   ```

2. **Environment variables:**
   - Sensitive data in `.env`
   - Never commit `.env` to git
   - Use `.env.example` for template

3. **Input sanitization:**
   - Validate all user inputs
   - Prevent SQL/NoSQL injection
   - URL validation

---

## 🚀 Scalability

### **Hiện tại:**
- Single bot instance
- MongoDB single server
- Polling mode

### **Mở rộng sau này:**

1. **Multiple bot instances:**
   - Switch to Webhook mode
   - Load balancer
   - Shared session storage (Redis)

2. **Database scaling:**
   - MongoDB replica set
   - Sharding by chapter_number/episode_number

3. **Caching:**
   - Redis cache cho frequently accessed data
   - Cache search results

4. **Message queue:**
   - Queue contributions for processing
   - Batch approval/rejection

---

## 📝 Best Practices Implemented

1. ✅ **Separation of Concerns**: Mỗi layer có trách nhiệm riêng
2. ✅ **DRY (Don't Repeat Yourself)**: Utilities, formatters tái sử dụng
3. ✅ **Single Responsibility**: Mỗi class/function một nhiệm vụ
4. ✅ **Dependency Injection**: Services nhận repositories
5. ✅ **Configuration Management**: Centralized trong settings.py
6. ✅ **Error Handling**: Try-catch ở mọi layer
7. ✅ **Logging**: Comprehensive logging
8. ✅ **Documentation**: Docstrings và comments
9. ✅ **Type Hints**: Python type annotations
10. ✅ **Constants**: Centralized constants

---

## 🧪 Testing Strategy (Recommended)

```python
# Unit tests
test_validators.py
test_repositories.py
test_services.py

# Integration tests
test_search_flow.py
test_contribution_flow.py

# End-to-end tests
test_bot_commands.py
```

---

**Kiến trúc này đảm bảo:**
- ✅ Dễ maintain
- ✅ Dễ mở rộng
- ✅ Dễ test
- ✅ Production-ready
- ✅ Scalable
