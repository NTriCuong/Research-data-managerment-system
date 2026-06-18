# Research Data Management System

Research Data Management System (RDMS) là đồ án xây dựng hệ thống hỗ trợ quản lý dữ liệu nghiên cứu thuộc phạm vi trường đại học.

> **Lưu ý:** Dự án đang trong quá trình phát triển. Kiến trúc, tính năng, API, cấu trúc dữ liệu và cách cài đặt có thể tiếp tục thay đổi. Nội dung README này chỉ mô tả trạng thái hiện có trong mã nguồn, không đại diện cho một phiên bản hoàn chỉnh hoặc sẵn sàng triển khai thực tế.

## Thành phần hiện có

Repository được tổ chức theo mô hình monorepo và hiện gồm:

- frontend sử dụng Next.js, React, TypeScript và Tailwind CSS;
- backend sử dụng FastAPI, SQLAlchemy và Alembic;
- các model và migration dành cho PostgreSQL;
- cấu hình Docker Compose cho một số dịch vụ hỗ trợ;
- các thư mục kiểm thử backend.

Một số nhóm API và giao diện đã có mã nguồn ban đầu, nhưng mức độ hoàn thiện và tính ổn định của từng phần chưa được đảm bảo.

## Cấu trúc dự án

```text
Research-data-managerment-system/
├── apps/
│   ├── backend/
│   ├── frontend/
├── package.json
└── README.md
```

## Công nghệ đang sử dụng

| Thành phần | Công nghệ |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Cơ sở dữ liệu | PostgreSQL |
| Dịch vụ hỗ trợ | Elasticsearch, RabbitMQ |
| Kiểm thử backend | Pytest |

Danh sách trên phản ánh các dependency và cấu hình hiện có, không khẳng định mọi thành phần đã được tích hợp hoàn chỉnh.

## Chạy dự án để phát triển

### Yêu cầu

- Node.js và npm;
- Python;
- PostgreSQL hoặc Docker.

Phiên bản công cụ cụ thể chưa được chuẩn hóa cho toàn bộ dự án.

### Frontend

Từ thư mục gốc của repository:

```bash
npm install
npm run dev:frontend
```

Frontend mặc định chạy tại `http://localhost:3000`.

### Backend

Từ thư mục `apps/backend`, tạo môi trường ảo và cài dependency:

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Cài dependency và tạo file cấu hình môi trường:

```bash
pip install -r requirements.txt
```

```powershell
Copy-Item .env.example .env
```

Cập nhật các giá trị cần thiết trong `.env`, sau đó chạy migration và backend:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend mặc định chạy tại `http://localhost:8000`. Có thể kiểm tra bằng:

- `GET /`
- `GET /health`
- OpenAPI JSON tại `GET /api/v1/openapi.json`

### Docker Compose

Repository có file `apps/docker-compose.yml` dành cho môi trường phát triển. Cấu hình Docker và các biến môi trường liên quan vẫn đang được điều chỉnh, vì vậy cần kiểm tra lại đường dẫn, file `.env` và giá trị cấu hình trước khi sử dụng.

## Cơ sở dữ liệu

Backend hiện có SQLAlchemy model và Alembic migration. Các schema PostgreSQL xuất hiện trong mã nguồn gồm:

- `public`;
- `staging`;
- `core`;
- `log`.

Thiết kế bảng và quy trình xử lý dữ liệu vẫn có thể thay đổi trong quá trình phát triển.

## Kiểm thử

Các bài kiểm thử backend được đặt trong `apps/backend/tests`. Sau khi cài dependency backend, có thể chạy từ thư mục `apps/backend`:

```bash
pytest
```

Việc có test trong repository không đồng nghĩa toàn bộ luồng nghiệp vụ đã được bao phủ hoặc hoạt động ổn định.

## Trạng thái dự án

Dự án hiện là sản phẩm đang phát triển phục vụ đồ án tốt nghiệp. Chưa có bản phát hành ổn định, tài liệu API chính thức hoặc cam kết về tính tương thích giữa các phiên bản.

Các chức năng chỉ nên được xem là hoàn thành sau khi đã được kiểm thử và xác nhận trong phạm vi yêu cầu của đồ án.
