import os
import socket
import threading

""" IP of Server """
IP = socket.gethostbyname(socket.gethostname())   
PORT = 1200
ADDRESS = (IP, PORT)
SIZE = 2028
FORMAT = "utf-8"
CLIENT_DATA_ROOT = "client_server"  

clients = {}  

def list_files(client_id, client_socket):
    client_folders = [f for f in os.listdir(CLIENT_DATA_ROOT) if os.path.isdir(os.path.join(CLIENT_DATA_ROOT, f))]
    all_files = []
    try:
        for folder in client_folders:
            client_files = os.listdir(os.path.join(CLIENT_DATA_ROOT, folder))
            client_info = f"{folder}: " + ", ".join(client_files)
            all_files.append(client_info)
        
        send_data = " "
        if len(all_files) == 0:
            send_data += "No files found."
        else:
            send_data += "\n".join(all_files)
        client_socket.send(send_data.encode(FORMAT))
    except FileNotFoundError:
        client_socket.send("ERROR@Directory not found.".encode(FORMAT))

def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] Connection from {address} is established.")
    client_socket.send("Welcome to the File Server.".encode(FORMAT))

    """ Receive client ID"""
    client_id = client_socket.recv(SIZE).decode(FORMAT)
    print(f"Client ID {client_id} connected.")

    while True:
        data = client_socket.recv(SIZE).decode(FORMAT)
        if not data:
            break
        cmd, *args = data.split("@")
        
        if cmd == "LIST":
            list_files(client_id, client_socket)
            
        elif cmd == "UPLOAD":
    
            try:
                target_client_id, filename = args

                """ Send confirmation to client to proceed with upload"""
                client_socket.send("READY_FOR_UPLOAD".encode(FORMAT))

                """ Receive sender client ID from the client"""
                sender_client_id = client_socket.recv(SIZE).decode(FORMAT)

                """Check if the sender_client_id matches the expected one"""
                expected_sender_client_id = sender_client_id

                if client_id == expected_sender_client_id:
                    """Construct filepath of the file in the target client's directory"""
                    target_folder = os.path.join(CLIENT_DATA_ROOT, f"client{target_client_id}_server")
                    filepath = os.path.join(target_folder, filename)
                    
                    """Read the file content"""
                    with open(filepath, "rb") as file:
                        file_content = file.read()

                    """Save the file in the client's own directory"""
                    client_folder = os.path.join(CLIENT_DATA_ROOT, f"client{client_id}_server")
                    os.makedirs(client_folder, exist_ok=True)
                    filepath = os.path.join(client_folder, filename)
                    with open(filepath, "wb") as file:
                        file.write(file_content)
                    
                    send_data = "File uploaded successfully"
                else:
                    send_data = "ERROR@Invalid sender client ID for upload"
            except (IndexError, PermissionError, FileNotFoundError) as e:
                send_data = f"ERROR@Failed to upload file: {e}"
            client_socket.send(send_data.encode(FORMAT))

        elif cmd == "QUIT":
            print(f"Client {client_id} requested to quit.")
            client_socket.send("QUIT".encode(FORMAT))
            break

    print(f"[DISCONNECTED] {address} is disconnected.")
    client_socket.close()


def main():
    if not os.path.exists(CLIENT_DATA_ROOT):
        os.makedirs(CLIENT_DATA_ROOT)
    print("[STARTING] Server is starting.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDRESS)
    server_socket.listen()
    print("[LISTENING] Server is listening for connections...")

    while True:
        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

if __name__ == "__main__":
    main()

