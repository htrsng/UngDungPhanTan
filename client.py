import sys
import xmlrpc.client

def run_client(port):
    # Kết nối tới Server (Node)
    try:
        node = xmlrpc.client.ServerProxy(f'http://localhost:{port}')
        print(f"Đã kết nối tới Node tại cổng {port}")
    except Exception as e:
        print("Không kết nối được server:", e)
        return

    while True:
        print("\n--- MENU ---")
        print("1. PUT (Lưu)")
        print("2. GET (Xem)")
        print("3. DELETE (Xóa)")
        print("4. Thoát")
        choice = input("Chọn lệnh (1-4): ")

        try:
            if choice == '1':
                k = input("Nhập Key: ")
                v = input("Nhập Value: ")
                # Gọi hàm put bên node.py
                node.put(k, v) 
                print("-> Đã lưu thành công!")

            elif choice == '2':
                k = input("Nhập Key cần xem: ")
                # Gọi hàm get bên node.py
                val = node.get(k)
                print(f"-> Kết quả: {val}")

            elif choice == '3':
                k = input("Nhập Key cần xóa: ")
                node.delete(k)
                print("-> Đã xóa!")

            elif choice == '4':
                break
        except Exception as e:
            print(f"Lỗi khi gọi Server: {e}")

if __name__ == "__main__":
    # Cách chạy: python client.py 8000
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_client(port)