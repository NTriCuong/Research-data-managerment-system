# 14. Search Architecture & Sync Worker Convention

Mục tiêu của module search không chỉ phục vụ tính năng tìm kiếm, mà còn hỗ trợ nghiên cứu so sánh hiệu năng giữa PostgreSQL Full-Text Search và Elasticsearch/OpenSearch, đồng thời làm nền cho mở rộng semantic search.

---

## 14.1 Search Architecture Direction

Hệ thống sử dụng 3 hướng tìm kiếm:

```text
1. PostgreSQL Full-Text Search
   → baseline trong MVP
   → dùng để so sánh hiệu năng

2. Elasticsearch / OpenSearch
   → search engine mở rộng
   → dùng cho ranking, highlight, fuzzy search, autocomplete

3. Semantic Search
   → hướng nghiên cứu mở rộng
   → dùng embedding/vector search
```

PostgreSQL vẫn là source of truth.

```text
PostgreSQL
  ↓
Outbox Event
  ↓
RabbitMQ/Kafka
  ↓
Search Sync Worker
  ↓
Elasticsearch/OpenSearch
```

Không ghi dữ liệu nghiệp vụ trực tiếp vào Elasticsearch.

---

## 14.2 PostgreSQL FTS Baseline Rules

PostgreSQL Full-Text Search được dùng làm baseline để đo:

```text
response time
index size
query complexity
Vietnamese search quality
resource usage
```

FTS phải index tối thiểu:

```text
title
abstract
description
authors
keywords
domains
identifier
```

Khuyến nghị:

```sql
CREATE EXTENSION IF NOT EXISTS unaccent;
```

Dùng:

```text
search_text
search_vector
GIN index
trigger update
```

Ví dụ:

```sql
CREATE INDEX idx_core_research_search_vector
ON core.research_objects
USING GIN (search_vector);
```

Không dùng `ILIKE '%keyword%'` làm baseline chính, vì nó không đại diện cho full-text search.

---

## 14.3 Elasticsearch Comparison Rules

Elasticsearch/OpenSearch được dùng để so sánh với PostgreSQL FTS trên cùng dataset.

Phải đảm bảo cùng một tập dữ liệu:

```text
same records
same fields
same filters
same access rules
same test queries
```

Index chính:

```text
rdms_research_objects_v1
```

Dùng alias:

```text
rdms_research_objects
```

Document ID phải dùng:

```text
core.research_id
```

Không dùng auto-generated Elasticsearch ID.

---

## 14.4 Search Benchmark Rules

Khi benchmark PostgreSQL FTS và Elasticsearch, phải đo cùng kịch bản.

### Dataset Size

Tối thiểu:

```text
1,000 records
5,000 records
10,000 records nếu có thời gian
```

### Query Types

Phải có các nhóm query:

```text
1. Search title
2. Search abstract
3. Search author
4. Search keyword
5. Search Vietnamese with accent
6. Search Vietnamese without accent
7. Search with year filter
8. Search with department filter
9. Search with access_level filter
10. Multi-field search
```

### Metrics

Cần đo:

```text
P50 response time
P95 response time
P99 response time
average response time
index size
CPU usage
RAM usage
precision@k nếu đánh giá chất lượng
recall@k nếu có ground truth
```

### NFR Target

Theo SRS:

```text
P95 search response time <= 2 giây với 5,000 metadata records
```

---

## 14.5 RabbitMQ/Kafka Sync Worker Rules

Search index không được update trực tiếp trong request chính nếu có thể tránh.

Không tốt:

```text
API approve
  ↓
save PostgreSQL
  ↓
call Elasticsearch trực tiếp
  ↓
response client
```

Tốt:

```text
API approve
  ↓
save PostgreSQL + insert outbox event trong cùng transaction
  ↓
response client
  ↓
worker consume event
  ↓
sync Elasticsearch
```

---

## 14.6 Outbox Pattern Rules

Mọi thay đổi ảnh hưởng search index phải sinh outbox event.

Áp dụng cho:

```text
core research created
core research updated
metadata approved
approved record revision approved
access_level changed
author changed
keyword changed
domain changed
file metadata changed nếu search file metadata
soft delete
```

Bảng gợi ý:

```sql
CREATE TABLE log.outbox_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    retry_count INT NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ
);
```

Ví dụ event:

```json
{
  "event_type": "research_object.approved",
  "aggregate_type": "research_object",
  "aggregate_id": "uuid",
  "payload": {
    "research_id": "uuid",
    "action": "index"
  }
}
```

---

## 14.7 Transaction Boundary Rules

Outbox event phải được ghi cùng transaction với thay đổi dữ liệu chính.

Ví dụ khi approve:

```text
transaction start
  ↓
insert/update core.research_objects
  ↓
insert metadata_versions
  ↓
insert workflow_history
  ↓
insert audit_log
  ↓
insert outbox_event
transaction commit
```

Không được:

```text
commit core trước
rồi mới insert outbox event
```

vì nếu lỗi giữa chừng, Elasticsearch sẽ không được sync.

---

## 14.8 Worker Processing Rules

Worker phải xử lý event theo nguyên tắc:

```text
idempotent
retryable
observable
dead-letter supported
```

### Idempotent

Cùng một event chạy nhiều lần không được tạo duplicate document.

Dùng:

```text
research_id làm document _id
```

Khi index:

```text
PUT /rdms_research_objects/_doc/{research_id}
```

Không dùng:

```text
POST /_doc
```

---

### Retry

Nếu Elasticsearch lỗi tạm thời:

```text
retry với backoff
```

Ví dụ:

```text
retry_count < 5
```

Sau đó đưa vào:

```text
dead letter queue
```

hoặc set:

```text
status = failed
```

---

### Ordering

Nếu dùng Kafka:

```text
partition key = research_id
```

để giữ thứ tự event theo từng research object.

Nếu dùng RabbitMQ:

```text
cần xử lý version hoặc updated_at
```

để tránh event cũ ghi đè event mới.

---

## 14.9 RabbitMQ vs Kafka Usage Convention

### RabbitMQ phù hợp khi:

```text
project MVP
team nhỏ
workflow task queue
retry đơn giản
dễ triển khai
ít event volume
```

Use case:

```text
sync Elasticsearch
send email notification
generate export
background file processing
```

### Kafka phù hợp khi:

```text
muốn event streaming
cần replay event
benchmark/research log
nhiều consumer group
event volume lớn
cần mở rộng semantic pipeline
```

Use case:

```text
search indexing
analytics pipeline
semantic embedding generation
audit event streaming
```

Khuyến nghị cho đồ án:

```text
MVP: RabbitMQ
Research extension: Kafka
```

Nếu bài báo cần nhấn mạnh architecture event-driven và replayable pipeline, Kafka có giá trị nghiên cứu cao hơn.

---

## 14.10 Search Consistency Rules

Search index là eventually consistent.

Nghĩa là sau khi approve:

```text
PostgreSQL updated immediately
Elasticsearch updated shortly after by worker
```

API search phải chấp nhận độ trễ nhỏ.

Nếu nghiệp vụ cần đọc ngay bản ghi vừa approve:

```text
đọc từ PostgreSQL
```

Không phụ thuộc Elasticsearch cho consistency tức thời.

---

## 14.11 Reconciliation Job Rules

Phải có job kiểm tra lệch dữ liệu giữa PostgreSQL và Elasticsearch.

Job chạy:

```text
daily
manual before benchmark
manual before demo
```

Kiểm tra:

```text
count mismatch
missing document
stale document
deleted document still indexed
access_level mismatch
```

Nếu lệch:

```text
reindex affected document
```

---

## 14.12 Reindex Rules

Khi đổi mapping/analyzer hoặc cần benchmark lại:

```text
1. Tạo index mới rdms_research_objects_v2
2. Bulk index từ PostgreSQL
3. So sánh count
4. Chạy sample queries
5. Switch alias
6. Ghi lại thời gian reindex
```

Không sửa mapping production trực tiếp.

---

## 14.13 Semantic Search Extension Rules

Semantic search là hướng mở rộng, không thay thế keyword search ngay từ MVP.

Pipeline đề xuất:

```text
PostgreSQL
  ↓
Outbox Event
  ↓
Embedding Worker
  ↓
Vector Store
  ↓
Hybrid Search API
```

Vector store có thể là:

```text
pgvector
Elasticsearch dense_vector
OpenSearch k-NN
Qdrant
Milvus
Weaviate
```

Với phạm vi đồ án, ưu tiên:

```text
pgvector
```

vì dễ tích hợp với PostgreSQL.

---

## 14.14 Semantic Document Text Rules

Text dùng để tạo embedding phải chuẩn hóa từ metadata:

```text
title
abstract
description
authors
keywords
domains
department
year
identifier
```

Ví dụ document text:

```text
Title: ...
Abstract: ...
Authors: ...
Keywords: ...
Domains: ...
Department: ...
Year: ...
```

Không embedding dữ liệu nhạy cảm nếu user không có quyền truy cập.

---

## 14.15 Hybrid Search Direction

Hướng nghiên cứu tốt:

```text
Keyword Search + Semantic Search
```

Ví dụ:

```text
BM25 score từ Elasticsearch
+
Vector similarity score từ embedding
```

Có thể so sánh:

```text
PostgreSQL FTS
Elasticsearch BM25
Semantic Search
Hybrid Search
```

Research question tốt hơn:

```text
How do PostgreSQL Full-Text Search, Elasticsearch BM25, and hybrid semantic search compare in response time and retrieval quality for metadata-driven research data management systems?
```

---

## 14.16 Benchmark Data Integrity Rules

Trước khi đo hiệu năng:

```text
1. Reset dataset
2. Rebuild PostgreSQL FTS index
3. Reindex Elasticsearch
4. Verify document count
5. Warm-up queries
6. Run benchmark multiple rounds
7. Export result as CSV
```

Không benchmark khi:

```text
index đang sync dở
worker đang retry nhiều
dataset PostgreSQL và Elasticsearch lệch nhau
```

---

## 14.17 Benchmark Report Rules

Báo cáo benchmark phải có:

```text
hardware/software environment
dataset size
number of queries
query categories
index configuration
analyzer configuration
sync architecture
result table
chart P50/P95/P99
discussion
limitations
```

Kết quả nên lưu tại:

```text
docs/research/search-benchmark/
```

Cấu trúc:

```text
docs/research/search-benchmark/
├── README.md
├── benchmark-plan.md
├── queries.json
├── results-postgres-fts.csv
├── results-elasticsearch.csv
├── charts/
└── analysis.md
```

---

## 14.18 Security Rules for Search

Search API phải filter quyền ở backend.

Không được để Elasticsearch quyết định quyền cuối cùng.

Bắt buộc filter theo:

```text
access_level
department_id
role
owner nếu cần
```

Public user chỉ thấy:

```text
access_level = public
```

Internal user thấy:

```text
public + internal + dữ liệu được phép theo department
```

Manager/Super Admin thấy theo quyền hệ thống.

---

## 14.19 Final Decision Rule

Trong hệ thống RDMS:

```text
PostgreSQL = source of truth
PostgreSQL FTS = baseline search
Elasticsearch = optimized keyword search engine
RabbitMQ/Kafka = asynchronous sync pipeline
Semantic Search = research extension
```