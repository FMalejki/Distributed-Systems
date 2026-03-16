import socket
import threading
import struct
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Tuple

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345, max_workers=10):
        self.host = host
        self.port = port
        self.clients: Dict[str, Tuple[socket.socket, Tuple[str, int]]] = {}
        self.clients_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tcp_socket: Optional[socket.socket] = None
        self.udp_socket: Optional[socket.socket] = None
        self.multicast_group = '224.0.0.1'
        self.running = False
        
    def start(self):
        self.running = True
        
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((self.host, self.port))
        self.tcp_socket.listen(5)
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind((self.host, self.port))
        
        print(f"Server started on {self.host}:{self.port}")
        print(f"Multicast group: {self.multicast_group}")
        
        threading.Thread(target=self.accept_tcp_connections, daemon=True).start()
        threading.Thread(target=self.handle_udp, daemon=True).start()
        
        try:
            while self.running:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            self.stop()
    
    def accept_tcp_connections(self):
        while self.running:
            try:
                assert self.tcp_socket is not None, "TCP socket not initialized"
                client_socket, address = self.tcp_socket.accept()
                self.executor.submit(self.handle_tcp_client, client_socket, address)
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_tcp_client(self, client_socket, address):
        nickname = None
        try:
            client_socket.send("NICK".encode('utf-8'))
            nickname = client_socket.recv(1024).decode('utf-8').strip()
            
            with self.clients_lock:
                self.clients[nickname] = (client_socket, address)
            
            print(f"{nickname} connected from {address}")
            self.broadcast_tcp(f"{nickname} joined the chat", exclude=nickname)
            
            while self.running:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                print(f"[TCP] {nickname}: {message}")
                self.broadcast_tcp(f"{nickname}: {message}", exclude=nickname)
                
        except Exception as e:
            print(f"Error handling client {nickname}: {e}")
        finally:
            if nickname:
                with self.clients_lock:
                    if nickname in self.clients:
                        del self.clients[nickname]
                print(f"{nickname} disconnected")
                self.broadcast_tcp(f"{nickname} left the chat", exclude=nickname)
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast_tcp(self, message, exclude=None):
        with self.clients_lock:
            for nick, (sock, addr) in list(self.clients.items()):
                if nick != exclude:
                    try:
                        sock.send(message.encode('utf-8'))
                    except Exception as e:
                        print(f"Error sending to {nick}: {e}")
    
    def handle_udp(self):
        while self.running:
            try:
                assert self.udp_socket is not None, "UDP socket not initialized"
                data, address = self.udp_socket.recvfrom(4096)
                message = data.decode('utf-8')
                print(f"[UDP] Received from {address}: {message}")
                
                with self.clients_lock:
                    for nick, (sock, addr) in self.clients.items():
                        try:
                            self.udp_socket.sendto(data, addr)
                        except Exception as e:
                            print(f"Error sending UDP to {nick}: {e}")
            except Exception as e:
                if self.running:
                    print(f"UDP error: {e}")
    
    def stop(self):
        print("\nShutting down server...")
        self.running = False
        
        with self.clients_lock:
            for nick, (sock, addr) in list(self.clients.items()):
                try:
                    sock.close()
                except:
                    pass
            self.clients.clear()
        
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass
        
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except:
                pass
        
        self.executor.shutdown(wait=False)
        print("Server stopped")

if __name__ == "__main__":
    server = ChatServer()
    server.start()