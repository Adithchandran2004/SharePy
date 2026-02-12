#--------------- Libraries ---------------#
import socket
import os
import json
import threading
from threading import Event, Thread
import struct
import time
from tqdm import tqdm
import subprocess
import sys
#---------global variables-----------------#
# Gradient colors from yellow to oranges
n1 = "\033[38;2;255;230;0m"  # #ffe600
n2 = "\033[38;2;255;208;0m"  # #ffd000
n3 = "\033[38;2;255;191;0m"  # #ffbf00
n4 = "\033[38;2;255;174;0m"  # #ffae00
n5 = "\033[38;2;255;162;0m"  # #ffa200
n6 = "\033[38;2;255;145;0m"  # #ff9100
reset = "\033[0m"

queue_path = os.path.join(os.path.dirname(__file__), "file_queue.json")
#-------------- Banners -------------------#
def showbanner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{n1}███████╗██╗  ██╗ █████╗ ██████╗ ███████╗██████╗ ██╗   ██╗{reset}
{n2}██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝{reset}
{n3}███████╗███████║███████║██████╔╝█████╗  ██████╔╝ ╚████╔╝ {reset}
{n4}╚════██║██╔══██║██╔══██║██╔══██╗██╔══╝  ██╔═══╝   ╚██╔╝  {reset}
{n5}███████║██║  ██║██║  ██║██║  ██║███████╗██║        ██║   {reset}
{n6}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   {reset}
             {n6}Fast | Secure | Python Powered |            {reset}
""")

def clear_and_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{n1}███████╗██╗  ██╗ █████╗ ██████╗ ███████╗██████╗ ██╗   ██╗{reset}
{n2}██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝{reset}
{n3}███████╗███████║███████║██████╔╝█████╗  ██████╔╝ ╚████╔╝ {reset}
{n4}╚════██║██╔══██║██╔══██║██╔══██╗██╔══╝  ██╔═══╝   ╚██╔╝  {reset}
{n5}███████║██║  ██║██║  ██║██║  ██║███████╗██║        ██║   {reset}
{n6}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   {reset}
           
            Press (S) to Send & (Q) to Quit
""")
#--------------ip_prefix_finder -------------------#
def get_network_prefix():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0] 
        s.close()
        return ".".join(local_ip.split(".")[:3]) + "."
    except Exception:
        return "192.168.1." 
#-------------- Login -------------------#
def login():
    showbanner()
    if os.path.exists("profile.json"):
        with open('profile.json', 'r') as f:
            profile = json.load(f)
        username = profile.get('username', 'User')
        ip_prefix = profile.get('ip_prefix', get_network_prefix())
        return username, ip_prefix
    else:
        print("[+] Creating New Account")
        username = input("Enter the username: ").strip()
        ip_prefix = get_network_prefix()
        profile = {"username": username, "ip_prefix": ip_prefix}
        with open("profile.json", "w") as f:
            json.dump(profile, f)
        print("[+] Account Created Successfully")
        return username, ip_prefix

#-------------- Server Function --------------#
def start_server(username, host='0.0.0.0', port=5001):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[+] {username} waiting for connection ....")
        
        conn, addr = server_socket.accept()
        conn.sendall(username.encode())
        time.sleep(0.2)
        conn.close()
        
        while True:
            try:
                conn, addr = server_socket.accept()
                conn.sendall(username.encode())
                time.sleep(0.2)
                peer_name = conn.recv(1024).decode()
                print(f"[+] Connected to {peer_name}")
                session_loop(conn)
                break
            except Exception as e:
                print(f"[!] Error: {e}")
                break
            finally:
                try: conn.close()
                except: pass
    except KeyboardInterrupt:
        os._exit(0)
#-------------- Client Function --------------#
def start_client(ip, username, port=5001):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        peer_name = client_socket.recv(1024).decode()
        client_socket.sendall(username.encode())
        print(f"[+] Connected to {peer_name} at {ip}")
        session_loop(client_socket)
    except Exception as e:
        print(f"[!] Error: {e}")
#-------------- Fast Scan -------------------#
def scan_ip(ip, port, timeout, servers):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        username = s.recv(1024).decode()
        servers.append((username, ip))
        s.close()
    except:
        pass

def scan_server(ip_base, port=5001, timeout=0.5):
    print("[+] Scanning started")
    servers = []
    threads = []
    for i in range(1, 255):
        ip = f"{ip_base}{i}"
        t = threading.Thread(target=scan_ip, args=(ip, port, timeout, servers))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return servers
#-------------- File Sending --------------#
def send_files(conn):
    if not os.path.exists(queue_path):
        return
    try:
        with open(queue_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return 

        file_paths = [entry["path"] for entry in data if entry["status"] == "pending"]
        if not file_paths:
            return

        conn.send(struct.pack('!I', len(file_paths)))

        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue

            filename = os.path.basename(file_path)
            filesize = os.path.getsize(file_path)

            conn.send(struct.pack('!I', len(filename)))
            conn.send(filename.encode())
            conn.send(struct.pack('!Q', filesize))

            print(f"Sending: {filename}")
            with open(file_path, 'rb') as f:
                bytes_sent = 0
                with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Sending:", colour="#a9f52f") as pbar:
                    while bytes_sent < filesize:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        conn.sendall(chunk)
                        bytes_sent += len(chunk)
                        pbar.update(len(chunk))

            time.sleep(1)
            for entry in data:
                if entry["path"] == file_path:
                    entry["status"] = "done"
                    break
            
            with open(queue_path, "w") as f:
                json.dump(data, f, indent=4)
    except Exception:
        pass
#-------------- File Receiving --------------#
def continuous_receive(conn, save_folder='received_files'):
    while True:
        try:
            receive_files(conn, save_folder)
        except Exception as e:
            error_msg = str(e)
            if any(x in error_msg for x in ["Connection closed", "Connection reset", "NoneType"]):
                print("\n[!] Peer has disconnected.")
                os._exit(0)
            time.sleep(1)

def receive_files(conn, save_folder='received_files'):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    try:
        peek = conn.recv(4, socket.MSG_PEEK)
        if not peek:
             raise ConnectionResetError("Connection closed")
    except BlockingIOError:
        return

    num_file_data = conn.recv(4)
    if not num_file_data:
        return
    
    num_files = struct.unpack('!I', num_file_data)[0]
    if num_files == 0:
        return

    print(f"[+] Receiving {num_files} file(s)...")
    for _ in range(num_files):
        len_data = conn.recv(4)
        if not len_data: break
        name_len = struct.unpack('!I', len_data)[0]
        filename = conn.recv(name_len).decode()
        filesize = struct.unpack('!Q', conn.recv(8))[0]
        
        received = 0
        save_path = os.path.join(save_folder, filename)
        
        with open(save_path, 'wb') as f:
            with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Received:",colour="#a9f52f") as pbar:
                while received < filesize:
                    chunk_size = min(4096, filesize - received)
                    chunk = conn.recv(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    pbar.update(len(chunk))
        time.sleep(1)
    clear_and_banner()
#-------------- Session Loop --------------#
def session_loop(conn):
    try:
        if os.path.exists("path_handler.py"):
            subprocess.Popen([sys.executable, "path_handler.py"])

        threading.Thread(target=continuous_receive, args=(conn,), daemon=True).start()

        def continuous_send_loop():
            while True:
                send_files(conn)
                time.sleep(3)

        threading.Thread(target=continuous_send_loop, daemon=True).start()

        while True:
            print("[i] File Sharing Running...")
            print("[i] Press 'q' to quit.")
            choice = input(">>> ").strip().lower()
            if choice == "q":
                conn.close()
                os._exit(0)
    except Exception:
        os._exit(0)
#-------------- Main -------------------#
def main():
    username, ip = login()
    while True:
        showbanner()
        print(f"\n[+] Act as (S)erver or (C)lient or (Q)uit")
        choice = input(">>> ").strip().lower()
        if choice == 's':
            start_server(username)
            break
        elif choice == 'c':
            found_servers = scan_server(ip_base=ip)
            if not found_servers:
                print("[-] No servers found.")
                input("Press Enter to retry...")
            else:
                print("\nAvailable Servers:")
                for i, (name, srv_ip) in enumerate(found_servers, 1):
                    print(f"{i}. {name} ({srv_ip})")
                sel = input("\nSelect server number: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(found_servers):
                    start_client(found_servers[int(sel) - 1][1], username)
                    break
        elif choice =='q':
            return

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 21b86ba0e9cfece94fcee3296ee07e47448ed313
