# Hệ thống lưu trữ Key–Value phân tán

## 1) Tổng quan

Hệ thống gồm nhiều node lưu dữ liệu dạng `key -> value`, giao tiếp qua **XML-RPC**.

- `PUT`: lưu/cập nhật dữ liệu
- `GET`: đọc dữ liệu
- `DELETE`: xóa dữ liệu
- Replication: node nhận lệnh từ client sẽ đẩy dữ liệu sang các node hàng xóm
- Recovery: node vừa khởi động sẽ thử kéo dữ liệu từ hàng xóm đầu tiên đang online
- Heartbeat: các node gửi tín hiệu sống định kỳ để phát hiện node hỏng

## 2) Cấu trúc mã nguồn

```text
UngDungPhanTan/
├── node.py      # Node server XML-RPC
├── client.py    # Client CLI
└── README.md
```

## 3) Yêu cầu hệ thống

- Python 3.x
- Chỉ dùng thư viện chuẩn Python (không cần `pip install`)

## 4) Xây dựng (setup)

Không có bước build riêng.

Chỉ cần mở terminal trong thư mục dự án và chạy trực tiếp bằng Python.

## 5) Chạy hệ thống

## 5.1 Chạy cluster 3 node (khuyến nghị)

Mở 3 terminal khác nhau:

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

> Lưu ý quan trọng: Nếu chạy `python node.py 8000` (không truyền hàng xóm), node đó sẽ chạy **độc lập**, dữ liệu không tự đồng bộ sang node khác.

## 5.2 Chạy client

Mở terminal mới:

```bash
python client.py 8000
```

Hoặc kết nối sang node khác:

```bash
python client.py 8001
python client.py 8002
```

## 6) Kiểm thử hệ thống

## Kịch bản A — PUT/GET trên cùng một node

1. Chạy node 8000 (có hoặc không có hàng xóm đều được).
2. Chạy client vào 8000:

   ```bash
   python client.py 8000
   ```
3. Trong menu client:
   - `1` -> Key: `test`, Value: `123`
   - `2` -> Key: `test`

Kết quả mong đợi: trả về `123`.

## Kịch bản B — Replication giữa node

1. Chạy **đúng cluster có neighbors** như mục 5.1.
2. Dùng client kết nối node 8000, thực hiện `PUT test 123`.
3. Dùng client khác kết nối node 8001, thực hiện `GET test`.

Kết quả mong đợi: node 8001 trả về `123`.

## Kịch bản C — Trường hợp dễ nhầm: chạy node độc lập

1. Chạy:

   ```bash
   python node.py 8000
   python node.py 8001
   ```
2. `PUT test 123` vào node 8000.
3. `GET test` ở node 8001.

Kết quả mong đợi: `Not Found` (đúng theo code hiện tại vì 2 node không phải hàng xóm của nhau).

## Kịch bản D — DELETE đồng bộ

1. Cluster chạy như mục 5.1.
2. `PUT test 123` vào node 8000.
3. `DELETE test` ở node 8000.
4. `GET test` ở node 8001/8002.

Kết quả mong đợi: `Not Found` trên các node còn lại.

## Kịch bản E — Recovery khi node khởi động lại

1. Cluster chạy đủ 3 node.
2. Tắt node 8002.
3. Ghi dữ liệu mới ở 8000 hoặc 8001.
4. Bật lại node 8002 bằng lệnh có neighbors:

   ```bash
   python node.py 8002 8000 8001
   ```

Kết quả mong đợi: lúc khởi động, node 8002 tự đồng bộ dữ liệu từ hàng xóm online.

## 7) Nhật ký (log) cần quan sát

- Khi ghi dữ liệu:
  - `[port] PUT request từ 'client': key = value`
  - `-> Đã sao lưu sang Node ...`
- Khi đọc:
  - `[port] GET: key -> ...`
- Khi phát hiện lỗi node:
  - `PHÁT HIỆN Node ... BỊ HỎNG!`

## 8) Lỗi thường gặp và cách xử lý

## `GET` ở node khác trả `Not Found`

Nguyên nhân phổ biến nhất: bạn khởi động node **không truyền neighbors**.

✅ Cách đúng (ví dụ 2 node):

```bash
python node.py 8000 8001
python node.py 8001 8000
```

## `Address already in use`

Cổng đang bị chiếm. Đổi cổng khác hoặc tắt process cũ.

## Client báo lỗi kết nối

Đảm bảo node đích đã chạy trước, đúng cổng, và không bị firewall chặn localhost.

## 9) Giới hạn hiện tại của code

- Dữ liệu lưu trong RAM, tắt toàn bộ node sẽ mất dữ liệu.
- `GET` đang dùng kiểm tra truthy/falsy (`return val if val else "Not Found"`), nên giá trị rỗng (`""`) hoặc `0` có thể bị trả về `Not Found`.
- Chưa có cơ chế quorum/leader election.

---


