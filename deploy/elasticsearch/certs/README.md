# Elasticsearch CA

Đặt file `ca.crt` được xuất từ server Elasticsearch vào thư mục này trên app server.

CA certificate là public certificate và có thể truyền qua SCP hoặc công cụ quản lý cấu hình. Không sao chép `ca.key`, node private key hoặc toàn bộ certificate volume sang app server.
