# Hệ Thống Lưu Trữ Phân Tán Key–Value 

## 1. Giới thiệu

Đây là đồ án xây dựng **hệ thống lưu trữ dữ liệu dạng Key–Value hoạt động trên môi trường phân tán** gồm nhiều node. Hệ thống cho phép các node phối hợp lưu trữ và sao lưu dữ liệu nhằm đảm bảo:

* **Consistency (Tính nhất quán)**: Dữ liệu được đồng bộ giữa các node.
* **Availability (Khả năng sẵn sàng)**: Client có thể truy cập dữ liệu từ bất kỳ node nào còn hoạt động.
* **Fault Tolerance (Khả năng chịu lỗi)**: Hệ thống vẫn hoạt động khi một hoặc nhiều node bị tắt.

Hệ thống sử dụng **XML-RPC qua HTTP** để giao tiếp giữa các node với nhau và giữa client với node.

---

## 2. Tính năng chính

* **Thao tác dữ liệu cơ bản**

  * `PUT`: Lưu hoặc cập nhật dữ liệu theo cặp key–value
  * `GET`: Lấy dữ liệu theo key
  * `DELETE`: Xóa dữ liệu theo key

* **Phân tán & Sao lưu (Replication)**
  Khi một node nhận dữ liệu mới, nó sẽ tự động **đồng bộ (replicate)** dữ liệu sang các node hàng xóm trong cụm.

* **Chịu lỗi (Fault Tolerance)**
  Hệ thống vẫn phục vụ client nếu một hoặc nhiều node bị tắt, miễn là còn ít nhất một node đang hoạt động.

* **Tự động khôi phục (Auto Recovery)**
  Khi một node bị hỏng khởi động lại, node đó sẽ tự động **kéo (pull)** dữ liệu còn thiếu từ các node khác để đồng bộ trạng thái.

---

## 3. Yêu cầu hệ thống

* **Ngôn ngữ**: Python 3.x
* **Thư viện**: Chỉ sử dụng thư viện chuẩn của Python (không cần cài thêm bằng `pip`)

  * `xmlrpc.server`
  * `xmlrpc.client`
  * `sys`, `threading` (nếu có)

---

## 4. Cấu trúc thư mục

```text
/DoAnGK
├── node.py       # Mã nguồn Node (Server)
├── client.py     # Mã nguồn Client (Người dùng)
└── README.md     # Tài liệu hướng dẫn (file này)
```

---

## 5. Hướng dẫn cài đặt và chạy

### Bước 1: Khởi động các Node trong Cluster

Mỗi node sẽ chạy trên một cổng (port) khác nhau và **biết địa chỉ của các node còn lại**.

Mở **3 cửa sổ Terminal/CMD**:

**Terminal 1 – Node A (Port 8000)**

```bash
python node.py 8000 8001 8002
```

**Terminal 2 – Node B (Port 8001)**

```bash
python node.py 8001 8000 8002
```

**Terminal 3 – Node C (Port 8002)**

```bash
python node.py 8002 8000 8001
```

Sau khi chạy, mỗi node sẽ hiển thị log cho biết node đang lắng nghe và kết nối thành công tới các node khác.

---

### Bước 2: Chạy Client

Mở **Terminal thứ 4** và kết nối Client tới **bất kỳ node nào** trong cluster (ví dụ Node 8000):

```bash
python client.py 8000
```

Client có thể gửi các lệnh `PUT`, `GET`, `DELETE` tới node đã kết nối.

---

## 6. Kịch bản kiểm thử (Demo Scenario)

### Kịch bản 1: Sao lưu dữ liệu (Replication)

1. Client kết nối tới Node 8000.
2. Thực hiện:

   ```
   PUT sinhvien Nguyen Van A
   ```
3. Quan sát Terminal của Node 8001 và Node 8002.

**Kết quả mong đợi**:
Cả Node 8001 và Node 8002 đều hiển thị log cho biết đã nhận được dữ liệu `sinhvien` từ Node 8000.

---

### Kịch bản 2: Kiểm tra tính nhất quán (Consistency)

1. Tắt Client hiện tại.
2. Chạy lại Client và kết nối tới Node 8001:

   ```bash
   python client.py 8001
   ```
3. Thực hiện:

   ```
   GET sinhvien
   ```

**Kết quả mong đợi**:
Client nhận được giá trị `Nguyen Van A` dù dữ liệu ban đầu được ghi vào Node 8000.

---

### Kịch bản 3: Chịu lỗi và khôi phục (Fault Tolerance & Recovery)

1. Tắt Node 8002 (Ctrl + C tại Terminal của Node 8002).
2. Client đang kết nối tới Node 8000 hoặc 8001 thực hiện:

   ```
   PUT exam Passed
   ```
3. Bật lại Node 8002:

   ```bash
   python node.py 8002 8000 8001
   ```
4. Quan sát Terminal của Node 8002.

**Kết quả mong đợi**:

* Node 8002 hiển thị thông báo đang đồng bộ dữ liệu.
* Node 8002 tự động tải lại cả `sinhvien` và `exam`.
* Client kết nối tới Node 8002 và thực hiện `GET exam` sẽ nhận được kết quả `Passed`.

---

## 7. Kiến trúc hệ thống

### 7.1 Mô hình mạng

* **Full Mesh (Lưới đầy đủ)**:
  Mỗi node đều biết địa chỉ (port) của tất cả các node còn lại trong cluster.

### 7.2 Cơ chế đồng bộ dữ liệu

* **Push (Khi ghi dữ liệu)**
  Khi node nhận lệnh `PUT` hoặc `DELETE`, node đó sẽ chủ động **đẩy dữ liệu cập nhật** sang các node hàng xóm đang hoạt động.

* **Pull (Khi khởi động lại)**
  Khi một node khởi động, nó sẽ **kéo toàn bộ dữ liệu** từ node hàng xóm đầu tiên khả dụng để đồng bộ trạng thái hiện tại.

---

## 8. Kết luận

Đồ án mô phỏng một **Distributed Key–Value Store đơn giản**, giúp minh họa các khái niệm quan trọng trong hệ phân tán như:

* Replication
* Consistency
* Fault Tolerance
* Recovery

Hệ thống tuy đơn giản nhưng đủ để phục vụ mục đích học tập và mở rộng nghiên cứu các kỹ thuật phân tán nâng cao hơn (quorum, leader election, vector clock, …).

---


