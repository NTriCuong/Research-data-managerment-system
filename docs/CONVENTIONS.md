# Project Convention Guide

Tài liệu này quy định coding convention, naming convention và workflow để đảm bảo codebase đồng nhất, dễ maintain và dễ review.

---

# 1. General Principles

## 1.1. Clean Code

Code phải:

- Readable > Clever
- Explicit > Implicit
- Simple > Complex
- Maintainable > Short

Ưu tiên code dễ đọc hơn code ngắn.

❌ Không tốt

```python
x = a if b else c
```

(nếu logic dài, khó đọc)

✅ Tốt

```python
if has_permission:
    role = admin_role
else:
    role = guest_role
```

---

## 1.2. Single Responsibility

Mỗi function chỉ nên làm **một nhiệm vụ**.

❌ Không tốt

```python
async def create_user():
    validate_input()
    hash_password()
    send_email()
    create_jwt()
    save_database()
```

✅ Tốt

```python
validate_user_payload()
hashed_password = hash_password()
user = await repository.create()
await send_welcome_email()
```

---

# 2. Folder Structure Convention

```text
app/
│
├── api/
│   └── v1/
│       └── endpoints/
│
├── core/
│
├── database/
│
├── models/
│
├── repositories/
│
├── schemas/
│
├── services/
│
└── utils/
```

## Quy tắc

### `api/`

Chỉ chứa:

- Router
- HTTP status
- Depends
- Request/Response

Không viết business logic.

---

### `services/`

Chứa:

- Business logic
- Validation logic
- Workflow logic

Không query database trực tiếp bằng raw SQL.

---

### `repositories/`

Chỉ xử lý:

- Query database
- CRUD
- Select/Insert/Update/Delete

Không chứa business logic.

---

### `schemas/`

Chỉ chứa:

- Request model
- Response model
- Validation model

Không chứa logic xử lý dữ liệu.

---

### `models/`

Chỉ chứa:

- SQLAlchemy ORM model
- Relationship
- Table mapping

Không viết logic nghiệp vụ.

---

# 3. Naming Convention

## 3.1 File naming

Dùng:

```text
snake_case.py
```

✅ Đúng

```text
research_object.py
staging_metadata.py
refresh_token.py
research_domain.py
```

❌ Sai

```text
ResearchObject.py
researchObject.py
research-object.py
```

---

## 3.2 Class naming

Dùng:

```text
PascalCase
```

✅ Đúng

```python
User
RefreshToken
StagingResearchObject
ResearchDomain
```

---

## 3.3 Variable naming

Dùng:

```text
snake_case
```

✅ Đúng

```python
current_user
access_token
research_object
department_id
```

❌ Sai

```python
currentUser
DepartmentID
```

---

## 3.4 Constant naming

Dùng:

```text
UPPER_SNAKE_CASE
```

✅ Đúng

```python
MAX_FILE_SIZE
JWT_EXPIRE_MINUTES
DEFAULT_LANGUAGE
```

---

## 3.5 Database naming

Table:

```text
snake_case plural
```

✅

```text
users
research_objects
refresh_tokens
field_comments
```

Column:

```text
snake_case
```

✅

```text
created_at
updated_at
department_id
access_level
```

---

# 4. API Convention

## 4.1 URL naming

Dùng:

```text
plural resource
```

✅

```text
/api/v1/users
/api/v1/research-objects
/api/v1/staging-metadata
```

❌

```text
/getUser
/createResearch
```

---

## 4.2 HTTP Method

### GET

Lấy dữ liệu

```http
GET /users
GET /users/{id}
```

### POST

Tạo dữ liệu

```http
POST /users
```

### PUT

Update toàn bộ

```http
PUT /users/{id}
```

### PATCH

Update một phần

```http
PATCH /users/{id}
```

### DELETE

Soft delete hoặc delete

```http
DELETE /users/{id}
```

---

## 4.3 Response format

Success:

```json
{
  "success": true,
  "data": {}
}
```

Pagination:

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

Error:

```json
{
  "success": false,
  "message": "Unauthorized"
}
```

---

# 5. Schema Convention

## Request schema

Tên:

```text
<Entity>Create
<Entity>Update
<Entity>Filter
```

Ví dụ:

```python
UserCreate
UserUpdate
ResearchObjectFilter
```

---

## Response schema

Tên:

```text
<Entity>Out
<Entity>DetailOut
```

Ví dụ:

```python
UserOut
ResearchObjectOut
ResearchObjectDetailOut
```

---

# 6. Service Convention

Tên function:

```text
verb + entity
```

✅

```python
create_user()
update_user()
get_user_by_id()
submit_staging_metadata()
```

❌

```python
handle()
process()
run()
```

---

Function không quá:

```text
50–80 dòng
```

Nếu dài → tách private helper.

Ví dụ:

```python
_create_authors()
_validate_before_submit()
_sync_domains()
```

---

# 7. Repository Convention

Repository chỉ query DB.

❌ Không tốt

```python
async def create_user():
    validate_email()
```

✅ Tốt

```python
async def create_user():
    self.db.add(user)
```

Validation phải ở service.

---

# 8. SQLAlchemy Convention

Luôn dùng:

```python
Mapped[]
mapped_column()
```

✅

```python
title: Mapped[str] = mapped_column(String(255))
```

Không dùng kiểu cũ:

❌

```python
title = Column(String)
```

---

Relationship phải explicit:

```python
relationship(
    back_populates="research_object",
    lazy="selectin"
)
```

---

# 9. Comment Convention

Chỉ comment:

- Why
- Business rule
- Complex logic

Không comment điều hiển nhiên.

❌

```python
# create user
user = User()
```

✅

```python
# refresh token bị revoke nếu login từ thiết bị mới
```

---

## TODO format

```python
# TODO(ttn): optimize bulk insert
```

---

# 10. Git Convention

## Branch naming

```text
feature/<feature-name>
fix/<bug-name>
hotfix/<bug-name>
refactor/<module>
```

Ví dụ:

```text
feature/auth-module
feature/staging-metadata
fix/login-bug
refactor/research-service
```

---

## Commit message

Format:

```text
type(scope): message
```

Ví dụ:

```text
feat(auth): add refresh token rotation
fix(staging): resolve N+1 query issue
refactor(user): extract validation logic
docs(api): update swagger examples
test(auth): add login integration test
```

Types:

```text
feat
fix
refactor
docs
style
test
chore
perf
```

---

# 11. Pull Request Convention

Title:

```text
[FEATURE] Add staging metadata module
```

Hoặc:

```text
[FIX] Resolve websocket connection issue
```

PR description:

## What changed

-

## Why

-

## Testing

-

# 12. Performance Rules

Mục tiêu:

- Đảm bảo đáp ứng NFR-PERF trong SRS
- Giữ API ổn định với 1.000–5.000 metadata records
- Hạn chế bottleneck khi workflow và search tăng dữ liệu

---

## 12.1 Database Query Rules

### Không query trong loop

❌ Không tốt

```python
for record in records:
    authors = await repo.get_authors(record.id)
```

Gây N+1 query.

✅ Tốt

```python
stmt = (
    select(StgResearchObject)
    .options(
        selectinload(StgResearchObject.authors),
        selectinload(StgResearchObject.keywords),
        selectinload(StgResearchObject.domains),
        selectinload(StgResearchObject.file_attachments),
    )
)
```

Bắt buộc dùng:

```python
selectinload()
joinedload()
```

khi trả nested response.

Áp dụng cho:

```text
staging.research_objects
core.research_objects
workflow_history
metadata_versions
```

---

### Không dùng SELECT *

❌

```sql
SELECT * FROM core.research_objects;
```

✅

```sql
SELECT
    research_id,
    title,
    year,
    access_level
FROM core.research_objects;
```

Chỉ select field cần dùng.

Giảm:

- network transfer
- memory
- serialization time

---

### API list bắt buộc pagination

Tất cả endpoint list:

```text
/mine
/research-objects
/workflow
/audit-logs
/search
```

phải có:

```text
limit
offset
```

hoặc:

```text
cursor pagination
```

Mặc định:

```python
limit=20
max_limit=100
```

Không cho phép:

```text
unlimited response
```

---

### Ưu tiên cursor pagination khi dữ liệu lớn

Không dùng:

```python
.offset(offset)
```

cho:

```text
> 10,000 records
```

Ưu tiên:

```text
cursor pagination
```

dựa trên:

```text
created_at
uuid
```

Ví dụ:

```text
GET /mine?cursor=...
```

Áp dụng đặc biệt cho:

```text
workflow queue
audit log
search result
dashboard data
```

---

## 12.2 Database Index Rules

Mọi cột dùng cho:

```text
WHERE
JOIN
ORDER BY
```

phải được đánh giá index.

### Bắt buộc index

#### Workflow

```sql
(created_by, workflow_status, created_at)
```

#### Search

```sql
GIN(search_vector)
```

Theo yêu cầu SRS FTS:

```text
title
abstract
description
authors
keywords
domains
identifier
```

phải được index vào search_vector.  
(SRS v1.1 yêu cầu trigger cập nhật search_vector) :contentReference[oaicite:1]{index=1}

---

#### Soft delete

Mọi bảng soft delete phải có:

```sql
WHERE deleted_at IS NULL
```

partial index.

Ví dụ:

```sql
CREATE INDEX idx_staging_active
ON staging.research_objects(created_at DESC)
WHERE deleted_at IS NULL;
```

---

#### Foreign Key

Tất cả foreign key bắt buộc có index.

Ví dụ:

```sql
created_by
department_id
reviewed_by
approved_by
research_id
staging_id
```

---

## 12.3 Upload Rules

Theo SRS:

```text
Max upload = 50MB/file
```

MVP chỉ hỗ trợ:

```text
PDF
evidence files
```

:contentReference[oaicite:2]{index=2}

### Không đọc toàn bộ file vào RAM

❌ Không tốt

```python
content = await file.read()
```

✅ Tốt

```python
while chunk := await file.read(CHUNK_SIZE):
```

Upload theo:

```text
stream
chunk
multipart upload
```

Bắt buộc validate:

```text
file size
mime type
extension
checksum
```

trước khi ghi metadata.

---

### Upload không block event loop

Cloud storage:

```text
Cloudflare R2
S3
MinIO
```

nếu dùng sync SDK phải chạy:

```python
asyncio.to_thread()
```

Không block FastAPI event loop.

---

## 12.4 Transaction Rules

Các workflow critical bắt buộc transaction.

Ví dụ:

```text
approve metadata
create revision
move staging → core
```

Phải atomic.

❌ Không tốt

```python
save_core()
save_version()
save_workflow()
```

nếu fail giữa chừng → data inconsistency.

✅ Tốt

```python
async with db.begin():
```

để rollback toàn bộ.

Theo SRS:

```text
approval phải chuyển staging → core bằng transaction
```

:contentReference[oaicite:3]{index=3}

---

## 12.5 Search Rules

MVP dùng:

```text
PostgreSQL Full-Text Search
```

Không query kiểu:

```sql
ILIKE '%keyword%'
```

cho production search.

Phải dùng:

```sql
tsvector
tsquery
GIN index
```

Theo SRS:

```text
search theo
title
abstract
description
author
keyword
domain
identifier
```

:contentReference[oaicite:4]{index=4}

---

### Vietnamese Search

SHOULD dùng:

```sql
unaccent
```

để hỗ trợ:

```text
có dấu / không dấu
```

Ví dụ:

```text
trí tuệ nhân tạo
tri tue nhan tao
```

đều tìm được.

---

## 12.6 Response Performance Rules

Response list:

```text
không trả nested sâu quá 2 level
```

❌

```json
research
  authors
    researcher
      department
```

✅

```json
research
authors
keywords
```

Dùng:

```python
response_model_exclude_none=True
```

để giảm payload.

---

## 12.7 Logging Rules

Không log:

```text
JWT
password
refresh token
cookie
secret
```

Log phải async hoặc structured logging.

Không dùng:

```python
print()
```

Production dùng:

```python
loguru
structlog
logging
```

---

## 12.8 NFR Performance Thresholds

Mọi tối ưu phải đảm bảo:

### Search

```text
P95 <= 2 giây
```

### GET API

```text
P95 <= 1.5 giây
```

### POST/PUT workflow

```text
P95 <= 2 giây
```

### Upload

```text
50MB ổn định
51MB trả lỗi rõ ràng
```

Theo NFR SRS v1.1. :contentReference[oaicite:5]{index=5}

---

# 13. Security Rules

Mục tiêu:

- Đảm bảo RBAC
- Không rò rỉ dữ liệu nghiên cứu
- Đúng workflow governance của RDMS

---

## 13.1 Authentication Rules

Bắt buộc:

```text
JWT access token
refresh token rotation
token revoke
```

Theo SRS:

```text
access token <= 30 phút
refresh token <= 7 ngày
```

:contentReference[oaicite:6]{index=6}

Không hardcode:

```python
SECRET_KEY
DATABASE_URL
R2_SECRET
```

Dùng:

```text
.env
```

Không commit:

```text
.env
secrets.json
credentials
```

---

## 13.2 Password Rules

Password phải:

```text
hash bcrypt hoặc argon2
```

Không lưu:

```text
plain text
encrypted reversible password
```

Theo SRS:

```text
NFR-SEC-02
```

:contentReference[oaicite:7]{index=7}

Không log password.

Không trả:

```text
invalid password
```

Chi tiết lỗi auth.

Chỉ trả:

```text
Invalid credentials
```

---

## 13.3 RBAC Rules

100% API thay đổi dữ liệu:

```text
POST
PUT
PATCH
DELETE
```

bắt buộc check quyền:

```python
Depends(require_roles())
```

Không chỉ check frontend.

Theo SRS:

```text
RBAC phải server-side
```

:contentReference[oaicite:8]{index=8}

---

### Role Matrix

#### Data Entry

Được:

```text
create draft
edit draft
submit review
request approved update
```

Không được:

```text
approve
edit core directly
manage users
```

---

#### Reviewer

Được:

```text
review metadata
request revision
move pending_review → pending_approval
```

---

#### Approver

Được:

```text
approve
reject
update access level
approve revision
```

---

#### Manager

Được:

```text
dashboard
search
export
analytics
```

Không được:

```text
approve workflow
```

---

#### Super Admin

Được:

```text
full access
```

---

## 13.4 Core Protection Rules

Không được update trực tiếp:

```text
core.research_objects
```

Mọi update approved record phải:

```text
core
↓
create staging revision
↓
review
↓
approval
↓
transaction update
↓
new metadata version
```

Theo FR-CORE-04. :contentReference[oaicite:9]{index=9}

---

## 13.5 File Upload Security

Bắt buộc validate:

```text
mime type
extension
file size
checksum
virus scan (future)
```

Không dùng:

```python
file.filename
```

làm storage filename.

Phải random:

```text
UUID filename
```

Ví dụ:

```text
c8e0c4ab.pdf
```

---

### Access Level

File phải inherit:

```text
public
internal
restricted
confidential
```

Không expose direct URL nếu:

```text
internal
restricted
```

Phải signed URL hoặc proxy download.

---

## 13.6 Audit Rules

100% hành động sau phải ghi audit:

```text
login
logout
create
update
submit
review
approve
reject
upload
export
role change
```

Theo:

```text
FR-LOG-01
```

:contentReference[oaicite:10]{index=10}

---

## 13.7 Workflow Integrity Rules

Workflow history không được orphan.

Bắt buộc:

```text
staging_id != NULL
OR
research_id != NULL
```

Không cho phép:

```text
from_status == to_status
```

Theo constraint SRS. :contentReference[oaicite:11]{index=11}

---

## 13.8 API Security Rules

Không expose:

```text
internal exception
stacktrace
SQL error
```

❌

```json
{
  "detail": "relation staging.research_objects does not exist"
}
```

✅

```json
{
  "message": "Internal server error"
}
```

Server log internal riêng.

---

### Rate Limiting

Nên có:

```text
login
refresh token
search
export
```

Ví dụ:

```text
5 login/minute/IP
```

---

## 13.9 Row-Level Security (Future)

Phase nâng cao:

```text
PostgreSQL RLS
```

theo:

```text
access_level
department_id
role
```

Public:

```text
public only
```

Department:

```text
same department
```

Manager/Admin:

```text
all
```

Theo SHOULD requirement trong SRS. :contentReference[oaicite:12]{index=12}