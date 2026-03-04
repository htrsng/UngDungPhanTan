import sys
import threading
import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn

class QuietXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    def log_message(self, format, *args):
        pass


class KeyValueNode:
    def __init__(self, port, neighbors):
        self.port = port
        self.neighbors = neighbors
        self.data_store = {}

        print(f"--- Node {port} ĐANG KHỞI ĐỘNG ---")

    # Khởi tạo cấu trúc heartbeat
        self.last_heartbeat = {}
        self.node_status = {}
        self.lock = threading.Lock()

        for n in self.neighbors:
            self.last_heartbeat[n] = None
            self.node_status[n] = "UNKNOWN"

    # Đồng bộ dữ liệu sau khi đã có biến
        self.sync_data_from_neighbors()
        print(f"Node {port} đã sẵn sàng phục vụ! Dữ liệu hiện tại: {self.data_store}")

    # Khởi động heartbeat theo thread
        threading.Thread(target=self.send_heartbeat, daemon=True).start()
        threading.Thread(target=self.detect_failed_nodes, daemon=True).start()


    def sync_data_from_neighbors(self):
        """Hỏi các hàng xóm để xin lại dữ liệu"""
        if not self.neighbors:
            return

        print("Đang đồng bộ dữ liệu từ hàng xóm...")
        for p in self.neighbors:
            self.node_status[p] = False

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
    def heartbeat(self, from_port):
        with self.lock:
            self.last_heartbeat[from_port] = time.time()

            if self.node_status.get(from_port) != "ALIVE":
                self.node_status[from_port] = "ALIVE"
                print(f"✅ [{self.port}] Node {from_port} ĐÃ HOẠT ĐỘNG")
        return True
    
    def send_heartbeat(self):
        while True:
            for neighbor_port in self.neighbors:
                try:
                    neighbor = xmlrpc.client.ServerProxy(f'http://localhost:{neighbor_port}')
                    neighbor.heartbeat(self.port)
                except:
                    pass
            time.sleep(3)
    def detect_failed_nodes(self):
        TIMEOUT = 10

        while True:
            now = time.time()
            with self.lock:
                for n_port in self.neighbors:
                    last = self.last_heartbeat.get(n_port)

                    # Chưa từng nhận heartbeat → bỏ qua
                    if last is None:
                        continue

                    # timeout → DEAD
                    if now - last > TIMEOUT:
                        if self.node_status.get(n_port) == "ALIVE":
                            self.node_status[n_port] = "DEAD"
                            print(f"⚠️ [{self.port}] PHÁT HIỆN Node {n_port} BỊ HỎNG!")
            time.sleep(2)

if __name__ == "__main__":
    # Cách chạy: python node.py 8000 8001 8002
    if len(sys.argv) < 2:
        print("Lỗi. Chạy lệnh: python node.py [Port] [Neighbor1] [Neighbor2]...")
        sys.exit(1)

    my_port = int(sys.argv[1])
    neighbor_ports = [int(p) for p in sys.argv[2:]]
    
    class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
        pass

    server = ThreadedXMLRPCServer(("localhost", my_port),requestHandler=QuietXMLRPCRequestHandler,allow_none=True)
    server.register_instance(KeyValueNode(my_port, neighbor_ports))
    
    print(f"Listening on port {my_port}...")
    server.serve_forever()