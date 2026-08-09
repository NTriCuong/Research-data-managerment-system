# Elasticsearch Mapping & Analysis Strategy

## 1. Phạm vi

Tài liệu này định nghĩa mapping và chiến lược analysis cho chỉ mục metadata nghiên cứu đã được phê duyệt:

```text
Physical index: rdms_research_objects_v1
Read/write alias: rdms_research_objects
Document _id: core.research_objects.research_id
Source of truth: PostgreSQL
Elasticsearch version: 8.17.x
```

Mapping thực thi nằm tại:

```text
deploy/elasticsearch/indices/rdms_research_objects_v1.json
```

Truy vấn xuất dữ liệu PostgreSQL thành Elasticsearch Bulk NDJSON nằm tại:

```text
deploy/elasticsearch/init/export_research_objects_bulk.sql
```

Chỉ index bản ghi hiện hành, chưa bị xóa mềm. Dữ liệu staging không nằm trong index này.

## 2. Mục tiêu analysis

Hệ thống phải hỗ trợ:

1. Stemming và loại English stop words cho tiêu đề, mô tả, tóm tắt, lĩnh vực và từ khóa tiếng Anh.
2. Tìm tên tác giả, tên đơn vị và metadata hỗn hợp có hoặc không có dấu.
3. Tìm chính xác và lọc theo UUID, mã danh mục, DOI/identifier, năm và quyền truy cập.
4. Autocomplete cho tiêu đề, tác giả và identifier.
5. Giữ cấu hình đủ đơn giản để benchmark công bằng với PostgreSQL FTS.

Stopword và stemming chỉ áp dụng cho các field nghiệp vụ được xác định là tiếng Anh. Tên tác giả, tên đơn vị và metadata có thể chứa tiếng Việt tiếp tục dùng analyzer không dấu và không stemming.

## 3. Analyzer

| Tên | Cấu hình | Dùng cho |
| --- | --- | --- |
| `rdms_vietnamese` | `standard` → `lowercase` → `asciifolding` | Full-text mặc định, tìm có/không dấu |
| `rdms_vietnamese_accent` | `standard` → `lowercase` | Subfield giữ dấu để boost exact-language match |
| `rdms_english` | possessive stemmer → lowercase → English stop words → English stemmer | `title`, `description`, `abstract`, `keywords.text`, `domains.name`, `search_text` |
| `rdms_autocomplete_index` | standard + lowercase + asciifolding + edge-ngram 2–20 | Index autocomplete |
| `rdms_autocomplete_search` | standard + lowercase + asciifolding | Query autocomplete, không tạo n-gram |
| `rdms_keyword_normalizer` | lowercase + asciifolding | Giá trị `keyword` cần so khớp không phân biệt hoa/dấu |

Ví dụ kỳ vọng:

```text
"Researchers' studies of neural networks" → possessive được chuẩn hóa, stop words bị loại và từ được stem
```

`title.accent`, `authors.full_name.accent`, `keywords.text.accent` và `domains.name.accent` giữ token có dấu. Các field này chỉ nên dùng như nhánh boost, không thay field không dấu.

## 4. Mapping strategy

### 4.1 Text và multi-field

- `title`, `abstract`, `description`: `text` với `rdms_english`.
- `title.exact`: sort/so khớp chính xác sau chuẩn hóa.
- `title.autocomplete`: prefix autocomplete.
- `identifier`: `keyword`; không token hóa DOI hoặc mã định danh.
- `keywords.text` và `domains.name`: dùng `rdms_english`; `publisher`, tên khoa, loại công trình và tác giả giữ analyzer không dấu.
- `search_text`: field tổng hợp nhận dữ liệu qua `copy_to` và dùng `rdms_english` cho truy vấn chính.

### 4.2 Field phục vụ filter/aggregation

UUID, enum, mã danh mục và `access_level` dùng `keyword`. `year` dùng `short`; bộ đếm dùng `long`; ngày dùng `date`; điểm chất lượng dùng `scaled_float`.

Không dùng `text` cho UUID hoặc enum vì sẽ làm sai exact filter và tăng kích thước index.

### 4.3 Object so với nested

`authors`, `keywords` và `domains` dùng `object`, không dùng `nested`, vì use case hiện tại chỉ:

- tìm tên/text trên toàn danh sách;
- lọc độc lập theo ID;
- không yêu cầu điều kiện nhiều thuộc tính phải thuộc cùng một phần tử.

Nếu sau này có truy vấn như “tác giả X đồng thời có vai trò Y trên cùng một author object”, cần đổi `authors` thành `nested` và reindex sang phiên bản mới.

### 4.4 Dynamic mapping

`dynamic: strict` được bật ở root và các object nghiệp vụ. Worker gửi sai tên field hoặc field mới chưa được thiết kế sẽ thất bại rõ ràng thay vì âm thầm tạo mapping sai.

## 5. Document contract

Worker phải dùng `research_id` làm `_id` và gửi document theo dạng:

```json
{
  "schema_version": 1,
  "research_id": "9b4d0f2c-1ef1-4f21-b76c-1d4538f09cc1",
  "source_staging_id": "cbcaaf07-38db-45b0-85ea-e94af909eae7",
  "title": "Research Data Management in Universities",
  "description": "A study of institutional research data workflows",
  "abstract": "This research evaluates metadata and discovery methods",
  "output_type": {
    "id": "d624812e-5124-4346-88c8-7bdc553ef703",
    "code": "PUBLICATION",
    "name": "Bài báo khoa học"
  },
  "department": {
    "id": "e038e5a0-d157-494a-85d3-e12d76ef40bd",
    "code": "CNTT",
    "name": "Khoa Công nghệ thông tin"
  },
  "year": 2026,
  "start_date": "2025-01-01",
  "end_date": "2026-06-30",
  "date_issued": "2026-07-01",
  "publisher": "STU",
  "language": "vi",
  "identifier": "10.1234/rdms.2026.01",
  "external_url": "https://example.edu/research/01",
  "source": null,
  "relation": null,
  "coverage": null,
  "rights": null,
  "access_level": "public",
  "authors": [
    {
      "researcher_id": "663179cd-c9e2-43cf-bc90-1c7929139939",
      "full_name": "Nguyễn Văn An",
      "email": "an@example.edu",
      "affiliation": "STU",
      "author_order": 1,
      "author_role": "creator"
    }
  ],
  "keywords": [
    {
      "id": "26f286f2-67c5-44e4-b353-e3b188749428",
      "text": "Dữ liệu nghiên cứu",
      "normalized_text": "du lieu nghien cuu"
    }
  ],
  "domains": [
    {
      "id": "ef811ba2-2777-4b1b-b7ce-bf56c267c9cb",
      "code": "CS",
      "name": "Khoa học máy tính"
    }
  ],
  "metadata_quality_score": 92.5,
  "view_count": 0,
  "download_count": 0,
  "version_no": 1,
  "is_current": true,
  "approved_by": "b8a13e26-68b2-4381-bc69-77189cb4566d",
  "approved_at": "2026-07-29T08:00:00Z",
  "created_at": "2026-07-29T08:00:00Z",
  "updated_at": null,
  "deleted_at": null
}
```

Không cần gửi `search_text`; Elasticsearch tự tổng hợp field này bằng `copy_to`.

## 6. Tạo index và alias

Service `elasticsearch-init` trong `compose.elasticsearch.yaml` tự tạo index và alias theo cách idempotent trên server Elasticsearch. Có thể chạy lại thủ công từ thư mục gốc:

```bash
docker compose --env-file .env.elasticsearch \
  -f compose.elasticsearch.yaml \
  run --rm elasticsearch-init
```

### 6.1 Xuất và bulk index dữ liệu hiện có

Tại thư mục gốc trên máy chủ Linux:

```bash
docker compose exec -T postgres sh -lc \
  'psql -X -A -t -q -v ON_ERROR_STOP=1 \
  -v es_index=rdms_research_objects_v1 \
  -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < deploy/elasticsearch/init/export_research_objects_bulk.sql \
  > /tmp/rdms_research_objects_v1.ndjson
```

Mỗi document có hai dòng NDJSON: action `index` và source document. Lệnh `index` là idempotent vì `_id` luôn là `research_id`.

Nạp bằng Bulk API:

```bash
curl --fail-with-body -sS \
  -X POST "http://localhost:9200/_bulk?refresh=false" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary "@/tmp/rdms_research_objects_v1.ndjson" \
  -o /tmp/rdms_bulk_response.json
```

Kiểm tra lỗi từng item trước khi tiếp tục:

```bash
jq '{errors, failed: [.items[] | select(.index.status >= 300)] | length}' \
  /tmp/rdms_bulk_response.json
```

Kết quả bắt buộc là:

```json
{
  "errors": false,
  "failed": 0
}
```

Sau đó refresh và kiểm tra count:

```bash
curl --fail-with-body -sS -X POST \
  "http://localhost:9200/rdms_research_objects_v1/_refresh"

curl --fail-with-body -sS \
  "http://localhost:9200/rdms_research_objects_v1/_count"
```

## 7. Query strategy

### 7.1 Truy vấn production

```json
{
  "from": 0,
  "size": 20,
  "track_total_hits": true,
  "_source": [
    "research_id",
    "title",
    "year",
    "access_level",
    "version_no",
    "approved_at"
  ],
  "query": {
    "bool": {
      "should": [
        {
          "multi_match": {
            "query": "du lieu nghien cuu",
            "type": "best_fields",
            "operator": "and",
            "fuzziness": "AUTO",
            "prefix_length": 2,
            "fields": [
              "title^6",
              "title.accent^2",
              "keywords.text^4",
              "authors.full_name^3",
              "domains.name^2.5",
              "abstract^2",
              "description",
              "department.name^1.5",
              "output_type.name"
            ]
          }
        },
        {
          "match": {
            "identifier": {
              "query": "du lieu nghien cuu",
              "boost": 6
            }
          }
        }
      ],
      "minimum_should_match": 1,
      "filter": [
        {
          "term": {
            "access_level": "public"
          }
        },
        {
          "term": {
            "is_current": true
          }
        }
      ],
      "must_not": [
        {
          "exists": {
            "field": "deleted_at"
          }
        }
      ]
    }
  },
  "highlight": {
    "pre_tags": [
      "<mark>"
    ],
    "post_tags": [
      "</mark>"
    ],
    "fields": {
      "title": {},
      "abstract": {
        "fragment_size": 160,
        "number_of_fragments": 2
      }
    }
  },
  "sort": [
    "_score",
    {
      "approved_at": "desc"
    }
  ]
}
```

Quyền truy cập phải được chuyển thành `bool.filter` ở backend. Public chỉ nhận `access_level=public`. Không nhận filter quyền trực tiếp từ client.

Không bật fuzzy cho query ngắn dưới 4 ký tự, DOI, email hoặc UUID. Với query thông thường, giới hạn `prefix_length: 2` để giảm số lượng candidate.

### 7.2 Autocomplete

Chỉ gọi khi người dùng nhập ít nhất 2 ký tự:

```json
{
  "size": 8,
  "_source": [
    "research_id",
    "title",
    "authors.full_name"
  ],
  "query": {
    "bool": {
      "must": {
        "multi_match": {
          "query": "quan ly du",
          "type": "bool_prefix",
          "fields": [
            "title.autocomplete^3",
            "authors.full_name.autocomplete^2",
            "identifier.autocomplete"
          ]
        }
      },
      "filter": {
        "term": {
          "access_level": "public"
        }
      }
    }
  }
}
```

### 7.3 Benchmark

Để so sánh công bằng với PostgreSQL FTS:

- dùng query trên `search_text` với BM25 mặc định;
- tắt fuzzy, autocomplete, popularity boost và recency boost;
- dùng cùng query, filter, dataset, số kết quả và warm-up;
- chạy nhánh có dấu và không dấu riêng;
- ghi rõ mapping/analyzer version trong kết quả.

Ví dụ baseline:

```json
{
  "query": {
    "bool": {
      "must": {
        "match": {
          "search_text": {
            "query": "du lieu nghien cuu",
            "operator": "and"
          }
        }
      },
      "filter": {
        "term": {
          "access_level": "public"
        }
      }
    }
  }
}
```

## 8. Kiểm tra analyzer

```http
POST /rdms_research_objects_v1/_analyze
Content-Type: application/json

{
  "analyzer": "rdms_english",
  "text": "Researchers' studies of neural networks"
}
```

Kết quả phải chuẩn hóa possessive, loại English stop words và stem các token tiếng Anh.

Kiểm tra mapping:

```http
GET /rdms_research_objects_v1/_mapping
GET /rdms_research_objects_v1/_settings
```

## 9. Versioning và vận hành

Không đổi analyzer của index đang chạy. Khi thay mapping/analyzer:

1. Tạo `rdms_research_objects_v2`.
2. Bulk index từ PostgreSQL.
3. So sánh count và chạy smoke query.
4. Chuyển alias bằng một lệnh `_aliases` nguyên tử.
5. Giữ `v1` để rollback trong thời gian xác nhận.

Môi trường development dùng một shard, không replica. Production có từ hai data node trở lên nên đặt ít nhất một replica. Số primary shard chỉ tăng sau khi đo dung lượng và tải thực tế.

## 10. Hướng mở rộng

- Synonym: dùng synonym set có quản trị và `synonym_graph` ở search analyzer; không hard-code synonym vào mapping `v1`.
- Semantic search: bổ sung vector trong index version mới hoặc dùng pgvector theo convention kiến trúc.
- Search-as-you-type nâng cao: cân nhắc completion suggester nếu cần popularity-weighted suggestions.
- Relevance: chỉ thêm function score theo lượt xem/độ mới sau khi đã có baseline BM25 và bộ đánh giá precision/recall.
