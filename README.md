# Research Data Management System (RDMS)

RDMS là hệ thống quản lý dữ liệu nghiên cứu trong phạm vi trường đại học. Repository được tổ chức theo mô hình monorepo, gồm:

- frontend: Next.js, React, TypeScript và Tailwind CSS;
- backend: FastAPI, SQLAlchemy và Alembic;
- cơ sở dữ liệu chính: PostgreSQL;
- công cụ tìm kiếm: Elasticsearch;
- reverse proxy: Nginx;
- kiểm thử backend: Pytest.

> Dự án đang trong quá trình phát triển. Không sử dụng các mật khẩu và secret mẫu trong môi trường thật.

## Cấu trúc dự án

```text
Research-data-managerment-system/
├── apps/
│   ├── backend/
│   └── frontend/
├── deploy/
│   ├── elasticsearch/
│   ├── nginx/
│   └── scripts/
├── compose.yaml
├── compose.elasticsearch.yaml
├── compose.dev.yaml
├── .env.example
├── .env.elasticsearch.example
└── README.md
```

## Yêu cầu hệ thống

### Chạy toàn bộ bằng Docker

- Docker Desktop trên Windows hoặc macOS;
- Docker Engine và Docker Compose plugin trên Linux;
- khuyến nghị tối thiểu 8 GB RAM, dành khoảng 4 GB cho Docker;
- các cổng local còn trống: `3000`, `8000`, `8080`, `9200` và `5433`.

Kiểm tra Docker:

```bash
docker --version
docker compose version
```

### Chạy mã nguồn trực tiếp

- Python 3.11;
- Node.js 20 và npm;
- PostgreSQL 16 hoặc phiên bản tương thích;
- Docker được khuyến nghị để chạy Elasticsearch 8.17.

## Cách 1: Chạy toàn bộ bằng Docker

Đây là cách được khuyến nghị để cài đặt lần đầu trên Windows, macOS và Linux. Stack bao gồm PostgreSQL, Elasticsearch, backend, frontend và Nginx.

### 1. Tạo file môi trường

Windows PowerShell:

```powershell
Copy-Item .env.example .env
Copy-Item .env.elasticsearch.example .env.elasticsearch
```

macOS/Linux:

```bash
cp .env.example .env
cp .env.elasticsearch.example .env.elasticsearch
```

Nếu các file này đã tồn tại, không sao chép đè lên cấu hình hiện tại.

### 2. Cấu hình `.env`

Các giá trị quan trọng cho local development:

```dotenv
HTTP_PORT=8080
FRONTEND_PORT=3000
BACKEND_PORT=8000
POSTGRES_PORT=5433

POSTGRES_USER=rdms
POSTGRES_PASSWORD=rdms-local-postgres-password
POSTGRES_DB=rdms
DATABASE_URL=postgresql+asyncpg://rdms:rdms-local-postgres-password@postgres:5432/rdms

APP_ENV=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
FRONTEND_URL=http://localhost:8080
SECRET_KEY=replace-with-a-long-random-secret
OTP_SALT=replace-with-another-long-random-secret
BACKEND_WORKERS=1

ELASTIC_HOST=https://elasticsearch:9200
ELASTIC_USERNAME=rdms_backend
RDMS_ELASTIC_PASSWORD=rdms-local-elastic-backend-password
ELASTIC_INDEX=rdms_research_objects

NEXT_PUBLIC_API_URL=http://localhost:8000
```

`DATABASE_URL` phải dùng hostname `postgres` và cổng nội bộ `5432`. `POSTGRES_PORT=5433` chỉ là cổng truy cập từ máy host, giúp tránh xung đột nếu máy đã cài PostgreSQL ở cổng `5432`.

### 3. Cấu hình `.env.elasticsearch`

```dotenv
ELASTIC_VERSION=8.17.0
ELASTIC_CLUSTER_NAME=rdms-cluster
ELASTIC_BIND_IP=127.0.0.1
ELASTIC_PORT=9200
ELASTIC_CERT_DNS=elasticsearch
ELASTIC_CERT_IP=127.0.0.1

ELASTIC_PASSWORD=rdms-local-elastic-admin-password
KIBANA_PASSWORD=rdms-local-kibana-password
RDMS_ELASTIC_PASSWORD=rdms-local-elastic-backend-password

ELASTIC_INDEX=rdms_research_objects_v1
ELASTIC_ALIAS=rdms_research_objects
KIBANA_BIND_IP=127.0.0.1
KIBANA_PORT=5601
```

Giá trị `RDMS_ELASTIC_PASSWORD` trong `.env` và `.env.elasticsearch` phải giống nhau.

### 4. Kiểm tra và khởi động

Windows PowerShell:

```powershell
$composeArgs = @(
  "--env-file", ".env",
  "--env-file", ".env.elasticsearch",
  "-f", "compose.yaml",
  "-f", "compose.elasticsearch.yaml",
  "-f", "compose.dev.yaml"
)

docker compose @composeArgs config --quiet
docker compose @composeArgs up -d --build
docker compose @composeArgs ps -a
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  config --quiet

docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  up -d --build

docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  ps -a
```

Các service `migrate`, `elasticsearch-setup` và `elasticsearch-init` kết thúc với trạng thái `Exited (0)` là bình thường. Các service `postgres`, `elasticsearch`, `backend`, `frontend` và `nginx` phải ở trạng thái `Up` hoặc `healthy`.

### 5. Seed dữ liệu mẫu vào PostgreSQL

Windows PowerShell:

```powershell
docker compose @composeArgs --profile tools run --rm seed
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  --profile tools run --rm seed
```

Sau khi seed, phải chạy tiếp bước 6 để đồng bộ dữ liệu sang Elasticsearch. Seed chỉ ghi vào PostgreSQL; nếu bỏ qua bước đồng bộ thì các màn hình dùng tìm kiếm/lọc qua Elasticsearch sẽ không có dữ liệu để trả về.

Tài khoản mẫu:

| Vai trò | Tên đăng nhập | Mật khẩu |
| --- | --- | --- |
| Super Admin | `admin` | `Admin@12345` |
| Data Entry | `dataentry01` | `Admin@12345` |
| Reviewer | `reviewer01` | `Admin@12345` |
| Approver | `approver01` | `Admin@12345` |
| Manager | `manager01` | `Admin@12345` |

Seed chỉ cần chạy một lần. Các lần chạy sau sẽ kiểm tra và bỏ qua dữ liệu đã tồn tại.

### 6. Đồng bộ dữ liệu seed sang Elasticsearch

Seed ghi trực tiếp vào PostgreSQL nên không kích hoạt background task lập chỉ mục của backend. Chạy bước này ngay sau bước seed để các bản ghi mẫu có thể được tìm kiếm và lọc bằng Elasticsearch.

Windows PowerShell:

```powershell
$postgresContainer = docker compose @composeArgs ps -q postgres
$elasticContainer = docker compose @composeArgs ps -q elasticsearch

docker cp ".\deploy\elasticsearch\init\export_research_objects_bulk.sql" `
  "${postgresContainer}:/tmp/export-research.sql"

docker compose @composeArgs exec -T postgres sh -lc `
  'psql -X -A -t -q -v ON_ERROR_STOP=1 -v es_index=rdms_research_objects_v1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" < /tmp/export-research.sql > /tmp/research.ndjson'

docker cp "${postgresContainer}:/tmp/research.ndjson" ".\research.ndjson"
docker cp ".\research.ndjson" "${elasticContainer}:/tmp/research.ndjson"

$elasticAdminPassword = (Select-String -Path ".env.elasticsearch" -Pattern "^ELASTIC_PASSWORD=").Line.Split("=",2)[1]

docker compose @composeArgs exec -T elasticsearch curl --fail --silent --show-error `
  --cacert config/certs/ca/ca.crt `
  --user "elastic:$elasticAdminPassword" `
  -X POST `
  -H "Content-Type: application/x-ndjson" `
  --data-binary "@/tmp/research.ndjson" `
  "https://localhost:9200/_bulk?refresh=true&filter_path=errors,items.*.error"
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  exec -T postgres sh -lc \
  'psql -X -A -t -q -v ON_ERROR_STOP=1 -v es_index=rdms_research_objects_v1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < deploy/elasticsearch/init/export_research_objects_bulk.sql \
  > research.ndjson

elastic_container=$(docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml ps -q elasticsearch)

docker cp research.ndjson "${elastic_container}:/tmp/research.ndjson"

docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  exec -T elasticsearch sh -lc \
  'curl --fail --silent --show-error --cacert config/certs/ca/ca.crt --user "elastic:$ELASTIC_PASSWORD" -X POST -H "Content-Type: application/x-ndjson" --data-binary @/tmp/research.ndjson "https://localhost:9200/_bulk?refresh=true&filter_path=errors,items.*.error"'
```

Kết quả thành công:

```json
{"errors":false}
```

### 7. Truy cập ứng dụng

| Dịch vụ | Địa chỉ |
| --- | --- |
| Ứng dụng qua Nginx | <http://localhost:8080> |
| Frontend trực tiếp | <http://localhost:3000> |
| Backend trực tiếp | <http://localhost:8000> |
| Swagger UI | <http://localhost:8000/docs> |
| OpenAPI JSON | <http://localhost:8000/api/v1/openapi.json> |
| Elasticsearch | <https://localhost:9200> |

Kiểm tra nhanh:

Windows PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/health-elastic
Invoke-WebRequest http://localhost:8080/nginx-health -UseBasicParsing
Invoke-RestMethod "http://localhost:8000/api/v1/public/researches?page=1&page_size=10"
```

macOS/Linux:

```bash
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/test-elastic
curl --fail http://localhost:8080/nginx-health
curl --fail "http://localhost:8000/api/v1/public/researches?page=1&page_size=10"
```

### 8. Kibana tùy chọn

Windows PowerShell:

```powershell
docker compose @composeArgs --profile ops up -d kibana
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  --profile ops up -d kibana
```

Kibana chạy tại <http://localhost:5601>.

### 9. Dừng hệ thống

Windows PowerShell:

```powershell
docker compose @composeArgs down
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml down
```

Các lệnh trên giữ lại dữ liệu trong Docker volumes. Chỉ dùng `down -v` khi muốn xóa hoàn toàn PostgreSQL, Elasticsearch, index và chứng chỉ local.

## Cách 2: Chạy source để phát triển

Trong chế độ này, backend và frontend chạy trực tiếp trên máy. PostgreSQL có thể chạy trên máy host; Elasticsearch chạy riêng bằng Docker.

### 1. Chạy Elasticsearch

Windows, macOS và Linux:

```bash
docker compose --env-file .env.elasticsearch -f compose.elasticsearch.yaml up -d
docker compose --env-file .env.elasticsearch -f compose.elasticsearch.yaml ps -a
```

Elasticsearch chạy tại `https://localhost:9200`.

### 2. Cấu hình backend

Windows PowerShell:

```powershell
Set-Location apps/backend
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cd apps/backend
cp .env.example .env
```

Cấu hình `apps/backend/.env` theo PostgreSQL trên máy:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/rdms
TEST_DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/rdms_test

SECRET_KEY=local-development-secret
OTP_SALT=local-development-otp-salt
CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_URL=http://localhost:3000

ELASTIC_HOST=https://localhost:9200
ELASTIC_USERNAME=rdms_backend
ELASTIC_PASSWORD=rdms-local-elastic-backend-password
ELASTIC_VERIFY_CERTS=false
ELASTIC_CA_CERT=
ELASTIC_INDEX=rdms_research_objects
```

### 3. Cài đặt và chạy backend

Tạo môi trường ảo:

```bash
python -m venv .venv
```

Kích hoạt trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Kích hoạt trên Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Kích hoạt trên macOS/Linux:

```bash
source .venv/bin/activate
```

Cài dependency, migrate và chạy:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Cài đặt và chạy frontend

Mở terminal khác và vào `apps/frontend`.

Windows PowerShell:

```powershell
Set-Location apps/frontend
Copy-Item .env.example .env.local
npm.cmd install
npm.cmd run dev
```

macOS/Linux:

```bash
cd apps/frontend
cp .env.example .env.local
npm install
npm run dev
```

Đảm bảo `apps/frontend/.env.local` có:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Frontend chạy tại <http://localhost:3000>.

## Kiểm thử

Chạy từ thư mục `apps/backend` sau khi kích hoạt môi trường ảo.

```bash
# Unit test, không cần database thật
python -m pytest tests/unit -q

# Integration test, cần TEST_DATABASE_URL và database đã migrate
python -m pytest tests/integration -q

# Database test
python -m pytest tests/database -q

# End-to-end test
python -m pytest tests/e2e -q

# Non-functional test
python -m pytest tests/nfr -q

# Toàn bộ backend test
python -m pytest tests -q
```

Kiểm tra frontend:

```bash
npm run lint
npm run build
```

Frontend hiện chưa có test runner tự động riêng.

## Xử lý lỗi thường gặp

### PowerShell chặn `npm.ps1` hoặc `Activate.ps1`

Dùng `npm.cmd` thay cho `npm`. Với môi trường Python, có thể dùng Command Prompt và chạy `.venv\Scripts\activate.bat`, hoặc cấu hình Execution Policy phù hợp với chính sách máy.

### Cổng PostgreSQL đã được sử dụng

Nếu PostgreSQL trên máy đang dùng `5432`, đặt `POSTGRES_PORT=5433` trong `.env`. Container vẫn giao tiếp nội bộ qua `postgres:5432`.

### Elasticsearch không healthy

Xem log:

```bash
docker compose --env-file .env.elasticsearch -f compose.elasticsearch.yaml logs --tail 200 elasticsearch
```

Trên Linux, có thể cần cấu hình:

```bash
sudo sysctl -w vm.max_map_count=262144
```

Để giữ cấu hình sau khi khởi động lại, thêm `vm.max_map_count=262144` vào `/etc/sysctl.conf` theo quy định của hệ điều hành.

### Backend báo thiếu `OTP_SALT`

Thêm một chuỗi bí mật riêng vào file môi trường đang được sử dụng:

```dotenv
OTP_SALT=replace-with-a-long-random-secret
```

### Seed thành công nhưng tìm kiếm không có dữ liệu

Chạy bước “Đồng bộ dữ liệu seed sang Elasticsearch”. Những bản ghi được duyệt qua API sau đó sẽ được backend tự đồng bộ bằng background task.

### Xem log Docker

Windows PowerShell:

```powershell
docker compose @composeArgs logs --tail 200 backend frontend nginx postgres elasticsearch
```

macOS/Linux:

```bash
docker compose --env-file .env --env-file .env.elasticsearch \
  -f compose.yaml -f compose.elasticsearch.yaml -f compose.dev.yaml \
  logs --tail 200 backend frontend nginx postgres elasticsearch
```

## Dịch vụ ngoài

Ứng dụng vẫn khởi động khi chưa cấu hình các dịch vụ dưới đây, nhưng chức năng tương ứng sẽ không hoạt động đầy đủ:

- SMTP: gửi OTP và email thông báo;
- Cloudflare R2: tải lên và lưu trữ file;
- Firebase: push notification.

Hướng dẫn triển khai hai server và vận hành production nằm tại [deploy/README.md](deploy/README.md).
