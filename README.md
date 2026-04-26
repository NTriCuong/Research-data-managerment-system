# Source Project

## Giới thiệu

Đây là dự án monorepo gồm frontend và backend.

## Công nghệ sử dụng

### Frontend

- Next.js
- TypeScript
- Tailwind CSS

### Backend

- Fast Api
- Python
- TypeORM
- PostgreSQL

### Monorepo

- npm workspaces
- concurrently

## Cấu trúc thư mục

```txt
source-project/
├── apps/
│   ├── frontend/              # Next.js
│   └── backend/               # Fast Api + TypeORM
│
├── packages/
│   ├── shared/                # enum, type, constant dùng chung
│   └── config/                # eslint, tsconfig dùng chung nếu cần
│
├── .env.example
├── package.json
├── package-lock.json
└── README.md
```
### cấu trúc thư mục cụ thể
``` backend
backend/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── auth_router.py
│   │   │   ├── auth_service.py
│   │   │   ├── auth_schema.py
│   │   │   └── auth_dependency.py
│   │   │
│   │   ├── users/
│   │   │   ├── user_router.py
│   │   │   ├── user_service.py
│   │   │   ├── user_repository.py
│   │   │   ├── user_entity.py
│   │   │   └── user_schema.py
│   │   │
│   │   └── research/
│   │       ├── research_router.py
│   │       ├── research_service.py
│   │       ├── research_repository.py
│   │       ├── research_entity.py
│   │       └── research_schema.py
```
``` frontend
```

## lệnh chạy cả dự án 
```
npm run dev

frontend: port 3000
backend: port 8000
```