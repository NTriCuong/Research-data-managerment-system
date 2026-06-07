# Backend Test Suite

Tests được tổ chức thành 5 phần:

## `unit/`

Test logic nhỏ, không cần DB thật.

```powershell
python -m pytest tests/unit -q
```

## `integration/`

Test endpoint/service với DB test. Định nghĩa `TEST_DATABASE_URL` vào env trước khi chạy phần này.

```powershell
python -m pytest tests/integration -q
```

## `e2e/`

Test End-to-end.

```powershell
python -m pytest tests/e2e -q
```

## `database/`

Tests cho Alembic migrations, database constraints, triggers, and functions.

```powershell
python -m pytest tests/database -q
```

## `nfr/`

Test yêu cầu phi chức năng bao gồm performance, security, reliability, and load tests.

```powershell
python -m pytest tests/nfr -q
```

chạy tất cả tests:

```powershell
python -m pytest tests -q
```
