import socket
import threading
import struct
import sys

class ChatClient:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.nickname = None
        self.tcp_socket = None
        self.udp_socket = None
        self.multicast_group = '224.0.0.1'
        self.running = False
        
    def start(self):
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.host, self.port))
            
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('', self.port))
            
            multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            multicast_socket.bind(('', self.port))
            mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            self.multicast_socket = multicast_socket
            
            message = self.tcp_socket.recv(1024).decode('utf-8')
            if message == 'NICK':
                self.nickname = input("Enter your nickname: ")
                self.tcp_socket.send(self.nickname.encode('utf-8'))
            
            self.running = True
            
            threading.Thread(target=self.receive_tcp, daemon=True).start()
            threading.Thread(target=self.receive_udp, daemon=True).start()
            threading.Thread(target=self.receive_multicast, daemon=True).start()
            
            print(f"\nConnected as {self.nickname}")
            print("Commands:")
            print("  - Type message and press Enter for TCP")
            print("  - Type 'U' + message for UDP")
            print("  - Type 'M' + message for Multicast")
            print("  - Type 'quit' to exit\n")
            
            self.send_messages()
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop()
    
    def receive_tcp(self):
        while self.running:
            try:
                if self.tcp_socket is None:
                    break
                message = self.tcp_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"\r{message}\n> ", end='', flush=True)
                else:
                    break
            except Exception as e:
                if self.running:
                    print(f"\nConnection error: {e}")
                break
    
    def receive_udp(self):
        while self.running:
            try:
                if self.udp_socket is None:
                    break
                data, address = self.udp_socket.recvfrom(4096)
                message = data.decode('utf-8')
                print(f"\r[UDP] {message}\n> ", end='', flush=True)
            except Exception as e:
                if self.running:
                    print(f"\nUDP error: {e}")
                break
    
    def receive_multicast(self):
        while self.running:
            try:
                if not hasattr(self, 'multicast_socket') or self.multicast_socket is None:
                    break
                data, address = self.multicast_socket.recvfrom(4096)
                message = data.decode('utf-8')
                if not message.startswith(f"{self.nickname}:"):
                    print(f"\r[MULTICAST] {message}\n> ", end='', flush=True)
            except Exception as e:
                if self.running:
                    print(f"\nMulticast error: {e}")
                break
    
    def send_messages(self):
        while self.running:
            try:
                message = input("> ")
                
                if message.lower() == 'quit':
                    break
                
                if message.startswith('U'):
                    content = message[1:].strip()
                    if content and self.udp_socket is not None:
                        full_message = f"{self.nickname}: {content}"
                        self.udp_socket.sendto(full_message.encode('utf-8'), (self.host, self.port))
                        print(f"[UDP sent] {content}")
                
                elif message.startswith('M'):
                    content = message[1:].strip()
                    if content:
                        full_message = f"{self.nickname}: {content}"
                        multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                        multicast_sock.sendto(full_message.encode('utf-8'), (self.multicast_group, self.port))
                        multicast_sock.close()
                        print(f"[MULTICAST sent] {content}")
                
                else:
                    if message and self.tcp_socket is not None:
                        self.tcp_socket.send(message.encode('utf-8'))
                        
            except Exception as e:
                print(f"Error sending message: {e}")
                break
    
    def stop(self):
        print("\nDisconnecting...")
        self.running = False
        
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
        
        if hasattr(self, 'multicast_socket') and self.multicast_socket:
            try:
                self.multicast_socket.close()
            except:
                pass
        
        print("Disconnected")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
    
    client = ChatClient(host, port)
    client.start()