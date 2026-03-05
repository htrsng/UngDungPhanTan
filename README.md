# Hệ thống Key–Value phân tán đơn giản

## 1. Giới thiệu

Đây là một hệ thống lưu trữ dữ liệu dạng **Key – Value** hoạt động trên nhiều node khác nhau.

Mỗi node là một server nhỏ chạy trên một port riêng và các node sẽ giao tiếp với nhau qua **XML-RPC**.

Hệ thống cho phép:

- Lưu dữ liệu (`PUT`)
- Đọc dữ liệu (`GET`)
- Xóa dữ liệu (`DELETE`)

Ngoài ra hệ thống còn có một số cơ chế đơn giản của hệ thống phân tán như:

- **Replication** – dữ liệu được sao chép sang các node khác
- **Recovery** – node mới khởi động sẽ cố gắng lấy dữ liệu từ node khác
- **Heartbeat** – kiểm tra xem node khác còn hoạt động hay không

Mục tiêu của dự án là mô phỏng cách các hệ thống lưu trữ phân tán hoạt động ở mức cơ bản.

## 2. Cấu trúc dự án

```text
UngDungPhanTan/
│
├── node.py
├── client.py
└── README.md
```

### `node.py`

Đây là server của hệ thống. Mỗi node sẽ:

- Lưu dữ liệu key-value
- Nhận request từ client
- Gửi dữ liệu sang các node hàng xóm
- Kiểm tra trạng thái các node khác

### `client.py`

Đây là chương trình client chạy trên terminal. Client dùng để gửi lệnh đến node:

- `PUT`
- `GET`
- `DELETE`

## 3. Yêu cầu hệ thống

- Python 3.x
- Không cần cài thêm thư viện ngoài
- Chỉ sử dụng thư viện chuẩn của Python

## 4. Cách chạy hệ thống

### Bước 1 — Mở nhiều terminal

Để mô phỏng hệ thống phân tán, cần chạy nhiều node cùng lúc.

Ví dụ chạy 3 node.

### Bước 2 — Khởi động các node

**Terminal 1**

```bash
python node.py 8000 8001 8002
```

**Terminal 2**

```bash
python node.py 8001 8000 8002
```

**Terminal 3**

```bash
python node.py 8002 8000 8001
```

Ý nghĩa:

| Node   | Port | Neighbors  |
|--------|------|------------|
| Node 1 | 8000 | 8001, 8002 |
| Node 2 | 8001 | 8000, 8002 |
| Node 3 | 8002 | 8000, 8001 |

Các node này biết nhau nên có thể replication dữ liệu.

### Lưu ý quan trọng

Nếu chạy node không truyền neighbors:

```bash
python node.py 8000
```

thì node này sẽ chạy độc lập, dữ liệu không đồng bộ sang node khác.

## 5. Chạy client

Mở terminal mới:

```bash
python client.py 8000
```

Client sẽ kết nối vào node port 8000.

Bạn cũng có thể kết nối sang node khác:

```bash
python client.py 8001
python client.py 8002
```

## 6. Các chức năng chính

### PUT – lưu dữ liệu

Ví dụ:

```text
Key: name
Value: 12345
```

Node sẽ lưu:

```text
name -> 12345
```

Sau đó replicate sang các node hàng xóm.

### GET – đọc dữ liệu

Ví dụ:

```text
GET name
```

Kết quả:

```text
Trang
```

### DELETE – xóa dữ liệu

Ví dụ:

```text
DELETE name
```

Key sẽ bị xóa khỏi node và được xóa ở các node khác.

## 7. Các kịch bản test

### Test 1 – PUT / GET trên cùng node

1. Chạy node 8000.
2. Chạy client:

   ```bash
   python client.py 8000
   ```
3. Nhập `PUT test 123`.
4. Sau đó nhập `GET test`.

Kết quả mong đợi: `123`.

### Test 2 – Replication giữa node

1. Chạy cluster 3 node.
2. Client kết nối node 8000, thực hiện `PUT test 123`.
3. Mở client khác kết nối 8001, thực hiện `GET test`.

Kết quả mong đợi: `123`.

Điều này chứng tỏ dữ liệu đã được sao chép giữa các node.

### Test 3 – Node chạy độc lập

Chạy:

```bash
python node.py 8000
python node.py 8001
```

Hai node không có neighbors.

1. `PUT test 123` vào node 8000.
2. `GET test` ở node 8001.

Kết quả: `Not Found`.

Điều này là đúng vì 2 node không kết nối với nhau.

### Test 4 – DELETE đồng bộ

1. `PUT test 123`.
2. `DELETE test`.
3. `GET test` ở node khác.

Kết quả: `Not Found`.

Dữ liệu đã bị xóa trên toàn hệ thống.

### Test 5 – Recovery khi node restart

1. Chạy cluster 3 node.
2. Tắt node 8002.
3. `PUT` dữ liệu mới ở 8000.
4. Khởi động lại node 8002:

   ```bash
   python node.py 8002 8000 8001
   ```

Node 8002 sẽ tự động đồng bộ dữ liệu từ node khác.

## 8. Log hệ thống

Trong terminal của node có thể thấy các log như:

**Khi PUT**

```text
[8000] PUT request: test = 123
-> Replicated to node 8001
-> Replicated to node 8002
```

**Khi GET**

```text
[8001] GET test -> 123
```

**Khi node lỗi**

```text
Node 8002 is down
```

## 9. Hạn chế của hệ thống

Do đây là một hệ thống mô phỏng đơn giản nên vẫn có một số hạn chế:

- Dữ liệu chỉ lưu trong RAM, nếu tắt tất cả node thì dữ liệu sẽ mất
- Chưa có cơ chế leader election
- Chưa có quorum để đảm bảo consistency
- Chỉ phù hợp để minh họa nguyên lý hệ thống phân tán

## 10. Kết luận

Dự án này giúp hiểu các khái niệm cơ bản của hệ thống phân tán như:

- Replication
- Node communication
- Fault detection
- Data recovery

Mặc dù hệ thống còn đơn giản, nhưng nó giúp hiểu được cách các hệ thống phân tán hoạt động ở mức cơ bản.


