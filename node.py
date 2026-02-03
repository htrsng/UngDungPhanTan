
# test 1
# import sys
# from xmlrpc.server import SimpleXMLRPCServer

# class KeyValueNode:
#     def __init__(self, port):
#         self.port = port
#         # Đây là nơi lưu dữ liệu chính (RAM)
#         self.data_store = {} 
#         print(f"Node đang chạy tại cổng {port}...")

#     # --- Các hàm chức năng chính ---
    
#     def put(self, key, value):
#         """Lưu khóa và giá trị"""
#         self.data_store[key] = value
#         print(f"[{self.port}] PUT: {key} = {value}")
#         return True # Trả về True báo thành công

#     def get(self, key):
#         """Lấy giá trị từ khóa"""
#         val = self.data_store.get(key)
#         print(f"[{self.port}] GET: {key} -> {val}")
#         # Nếu không tìm thấy, trả về chuỗi rỗng hoặc thông báo
#         return val if val else "Not Found"

#     def delete(self, key):
#         """Xóa khóa"""
#         if key in self.data_store:
#             del self.data_store[key]
#             print(f"[{self.port}] DELETE: {key}")
#             return True
#         return False

# if __name__ == "__main__":
#     # Cách chạy: python node.py 8000
#     if len(sys.argv) < 2:
#         print("Lỗi: Vui lòng nhập cổng. Ví dụ: python node.py 8000")
#         sys.exit(1)

#     port = int(sys.argv[1])
    
#     # Khởi tạo Server lắng nghe tại localhost
#     server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    
#     # Đăng ký class KeyValueNode để Client có thể gọi hàm của nó
#     server.register_instance(KeyValueNode(port))
    
#     print(f"Server đã sẵn sàng. Nhấn Ctrl+C để tắt.")
#     server.serve_forever()

# # test 2
# import sys
# import xmlrpc.client
# from xmlrpc.server import SimpleXMLRPCServer

# class KeyValueNode:
#     def __init__(self, port, neighbors):
#         self.port = port
#         self.neighbors = neighbors # Danh sách các cổng của node hàng xóm
#         self.data_store = {}
#         print(f"Node {port} khởi động. Hàng xóm: {neighbors}")

#     def put(self, key, value, source="client"):
#         """
#         Lưu dữ liệu.
#         Tham số 'source' dùng để biết ai gọi hàm này:
#         - "client": Người dùng gọi -> Cần lưu và sao lưu sang hàng xóm.
#         - "replica": Hàng xóm gọi -> Chỉ cần lưu thôi, đừng gửi lại kẻo lặp vô tận.
#         """
#         print(f"[{self.port}] PUT request từ '{source}': {key} = {value}")
#         self.data_store[key] = value

#         # Nếu lệnh đến từ Client, ta phải sao lưu sang các hàng xóm
#         if source == "client":
#             self.replicate_to_neighbors(key, value)
        
#         return True

#     def replicate_to_neighbors(self, key, value):
#         """Gửi dữ liệu sang các node khác"""
#         for neighbor_port in self.neighbors:
#             try:
#                 # Tạo kết nối tới hàng xóm
#                 neighbor = xmlrpc.client.ServerProxy(f'http://localhost:{neighbor_port}')
#                 # Gọi hàm put của hàng xóm với cờ "replica"
#                 neighbor.put(key, value, "replica")
#                 print(f"  -> Đã sao lưu sang Node {neighbor_port}")
#             except Exception as e:
#                 print(f"  -> Lỗi kết nối tới Node {neighbor_port} (Node này có thể đang tắt)")

#     def get(self, key):
#         val = self.data_store.get(key)
#         print(f"[{self.port}] GET: {key} -> {val}")
#         return val if val else "Not Found"

#     def delete(self, key, source="client"):
#         # Tương tự PUT, DELETE cũng cần sao lưu (bạn tự bổ sung logic sao lưu cho delete nhé)
#         if key in self.data_store:
#             del self.data_store[key]
#             print(f"[{self.port}] DELETE: {key}")
            
#             # Bài tập nhỏ: Bạn hãy thử copy logic sao lưu của hàm PUT xuống đây
#             # để khi xóa ở 1 node, nó xóa luôn ở node kia.
            
#             return True
#         return False

# if __name__ == "__main__":
#     # Cách chạy mới: python node.py [Cổng_của_mình] [Cổng_hàng_xóm_1] [Cổng_hàng_xóm_2]...
#     if len(sys.argv) < 2:
#         print("Lỗi. Chạy lệnh: python node.py 8000 8001 8002")
#         sys.exit(1)

#     my_port = int(sys.argv[1])
    
#     # Tất cả các tham số phía sau là cổng hàng xóm
#     neighbor_ports = [int(p) for p in sys.argv[2:]]
    
#     server = SimpleXMLRPCServer(("localhost", my_port), allow_none=True)
#     server.register_instance(KeyValueNode(my_port, neighbor_ports))
    
#     print(f"Server {my_port} đang chạy...")
#     server.serve_forever()

# test 3 
import sys
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

class KeyValueNode:
    def __init__(self, port, neighbors):
        self.port = port
        self.neighbors = neighbors
        self.data_store = {}
        
        print(f"--- Node {port} ĐANG KHỞI ĐỘNG ---")
        
        # Bước quan trọng: Đồng bộ dữ liệu từ hàng xóm ngay khi bật lên
        self.sync_data_from_neighbors()
        
        print(f"Node {port} đã sẵn sàng phục vụ! Dữ liệu hiện tại: {self.data_store}")

    def sync_data_from_neighbors(self):
        """Hỏi các hàng xóm để xin lại dữ liệu"""
        if not self.neighbors:
            return

        print("Đang đồng bộ dữ liệu từ hàng xóm...")
        for n_port in self.neighbors:
            try:
                # Kết nối tới hàng xóm
                neighbor = xmlrpc.client.ServerProxy(f'http://localhost:{n_port}')
                # Xin toàn bộ dữ liệu
                data = neighbor.get_all_data()
                # Cập nhật vào kho của mình
                self.data_store.update(data)
                print(f" -> Đã đồng bộ thành công từ Node {n_port}. Lấy được {len(data)} mục.")
                # Chỉ cần đồng bộ từ 1 người sống là đủ, không cần hỏi hết
                return 
            except Exception as e:
                print(f" -> Không thể kết nối Node {n_port} để đồng bộ.")
        
        print(" -> Không tìm thấy hàng xóm nào online. Khởi tạo với dữ liệu trống.")

    def get_all_data(self):
        """Cho phép node khác lấy toàn bộ dữ liệu (để backup)"""
        return self.data_store

    def put(self, key, value, source="client"):
        print(f"[{self.port}] PUT request từ '{source}': {key} = {value}")
        self.data_store[key] = value

        if source == "client":
            self.replicate_to_neighbors(key, value)
        return True

    def replicate_to_neighbors(self, key, value):
        for neighbor_port in self.neighbors:
            try:
                neighbor = xmlrpc.client.ServerProxy(f'http://localhost:{neighbor_port}')
                neighbor.put(key, value, "replica")
                print(f"  -> Đã sao lưu sang Node {neighbor_port}")
            except Exception:
                print(f"  -> Node {neighbor_port} đang tắt. Bỏ qua.")

    def get(self, key):
        val = self.data_store.get(key)
        print(f"[{self.port}] GET: {key} -> {val}")
        return val if val else "Not Found"
        
    def delete(self, key, source="client"):
        if key in self.data_store:
            del self.data_store[key]
            print(f"[{self.port}] DELETE: {key} (nguồn: {source})")
            
            # Logic sao lưu cho lệnh Xóa
            if source == "client":
                 for neighbor_port in self.neighbors:
                    try:
                        neighbor = xmlrpc.client.ServerProxy(f'http://localhost:{neighbor_port}')
                        neighbor.delete(key, "replica")
                    except:
                        pass
            return True
        return False

if __name__ == "__main__":
    # Cách chạy: python node.py 8000 8001 8002
    if len(sys.argv) < 2:
        print("Lỗi. Chạy lệnh: python node.py [Port] [Neighbor1] [Neighbor2]...")
        sys.exit(1)

    my_port = int(sys.argv[1])
    neighbor_ports = [int(p) for p in sys.argv[2:]]
    
    server = SimpleXMLRPCServer(("localhost", my_port), allow_none=True)
    server.register_instance(KeyValueNode(my_port, neighbor_ports))
    
    print(f"Listening on port {my_port}...")
    server.serve_forever()