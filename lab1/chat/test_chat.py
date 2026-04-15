import socket
import threading
import time
import sys

def test_tcp_client(nickname, messages, delay=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 12345))
        
        msg = sock.recv(1024).decode('utf-8')
        if msg == 'NICK':
            sock.send(nickname.encode('utf-8'))
            print(f"[{nickname}] Connected")
        
        def receive():
            while True:
                try:
                    msg = sock.recv(1024).decode('utf-8')
                    if msg:
                        print(f"[{nickname}] Received: {msg}")
                    else:
                        break
                except:
                    break
        
        recv_thread = threading.Thread(target=receive, daemon=True)
        recv_thread.start()
        
        time.sleep(delay)
        
        for msg in messages:
            print(f"[{nickname}] Sending: {msg}")
            sock.send(msg.encode('utf-8'))
            time.sleep(1)
        
        time.sleep(2)
        sock.close()
        print(f"[{nickname}] Disconnected")
        
    except Exception as e:
        print(f"[{nickname}] Error: {e}")

def test_udp_client(nickname, message, delay=2):
    try:
        time.sleep(delay)
        
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        recv_sock.bind(('', 12345))
        
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        def receive_udp():
            while True:
                try:
                    data, addr = recv_sock.recvfrom(4096)
                    msg = data.decode('utf-8')
                    if not msg.startswith(f"{nickname}:"):
                        print(f"[{nickname}] UDP Received: {msg}")
                except:
                    break
        
        recv_thread = threading.Thread(target=receive_udp, daemon=True)
        recv_thread.start()
        
        time.sleep(1)
        full_msg = f"{nickname}: {message}"
        print(f"[{nickname}] Sending UDP: {message}")

        send_sock.sendto(full_msg.encode('utf-8'), ('127.0.0.1', 12345))
        
        recv_sock.close()
        send_sock.close()
        
    except Exception as e:
        print(f"[{nickname}] UDP Error: {e}")

def test_multicast_client(nickname, message, delay=3):
    try:
        time.sleep(delay)
        
        import struct
        multicast_group = '224.0.0.1'
        
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        recv_sock.bind(('', 12345))
        mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        def receive_multicast():
            while True:
                try:
                    data, addr = recv_sock.recvfrom(4096)
                    msg = data.decode('utf-8')
                    if not msg.startswith(f"{nickname}:"):
                        print(f"[{nickname}] Multicast Received: {msg}")
                except:
                    break
        
        recv_thread = threading.Thread(target=receive_multicast, daemon=True)
        recv_thread.start()
        
        time.sleep(1)
        
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        full_msg = f"{nickname}: {message}"
        print(f"[{nickname}] Sending Multicast: {message}")
        send_sock.sendto(full_msg.encode('utf-8'), (multicast_group, 12345))
        send_sock.close()
        
        time.sleep(2)
        recv_sock.close()
        
    except Exception as e:
        print(f"[{nickname}] Multicast Error: {e}")

def run_tests():
    print("=== Starting Chat Application Tests ===\n")
    
    print("Test 1: TCP Communication (2 clients)")
    print("-" * 50)
    
    client1 = threading.Thread(target=test_tcp_client, args=("A1", ["Hello", "How are you?"], 1))
    client2 = threading.Thread(target=test_tcp_client, args=("B1", ["Hi!", "good!"], 2))
    
    client1.start()
    client2.start()
    
    client1.join()
    client2.join()
    
    time.sleep(2)
    print("\n" + "=" * 50)
    print("Test 2: UDP Communication")
    print("-" * 50)
    
    udp1 = threading.Thread(target=test_udp_client, args=("C1", "UDP ASCII Art: ¯\\_(ツ)_/¯", 1))
    udp2 = threading.Thread(target=test_udp_client, args=("D1", "UDP Message from Dave", 2))
    
    udp1.start()
    udp2.start()
    
    udp1.join()
    udp2.join()
    
    time.sleep(2)
    print("\n" + "=" * 50)
    print("Test 3: Multicast Communication")
    print("-" * 50)
    
    mc1 = threading.Thread(target=test_multicast_client, args=("Eve", "Multicast from Eve", 1))
    mc2 = threading.Thread(target=test_multicast_client, args=("Frank", "Multicast from Frank", 2))
    
    mc1.start()
    mc2.start()
    
    mc1.join()
    mc2.join()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    print("Starting server first...")
    print("Make sure server.py is running on port 12345\n")
    time.sleep(2)
    run_tests()