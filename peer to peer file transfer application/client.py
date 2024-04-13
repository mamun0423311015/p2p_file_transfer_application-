import os
import socket

"""  IP of Server """
IP = socket.gethostbyname(socket.gethostname())   
PORT = 1200
ADDRESS = (IP, PORT)
SIZE = 2048
FORMAT = "utf-8"

def list_files(client_socket):
    try:
        client_socket.send("LIST".encode(FORMAT))
        response = client_socket.recv(SIZE).decode(FORMAT)
        print(response)
    except ConnectionError as e:
        print(f"Connection error: {e}")

def upload_file(client_id, client_socket):
    try:
        """ Prompt user for target client ID and filename to download """
        target_client_id = input("Enter target client ID: ")
        filename = input("Enter filename to download: ")
        filepath = os.path.join("client_server", f"client{target_client_id}_server", filename)
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                file_content = file.read()
            """Send the target client ID and filename to the server"""
            upload_cmd = f"UPLOAD@{target_client_id}@{filename}"
            client_socket.send(upload_cmd.encode(FORMAT))
            """Confirm readiness for upload"""
            response = client_socket.recv(SIZE).decode(FORMAT)
            if response == "READY_FOR_UPLOAD":
                """ Send the client ID"""
                client_socket.send(client_id.encode(FORMAT))
                """Send the file content"""
                client_socket.send(file_content)
                upload_response = client_socket.recv(SIZE).decode(FORMAT)
                print(upload_response)
            else:
                print("Server is not ready for upload.")
        else:
            print("File not found.")
    except ConnectionError as e:
        print(f"Connection error: {e}")

def main():
    client_id = input("Enter your client ID: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect(ADDRESS)
            client_socket.send(client_id.encode(FORMAT))
            welcome_msg = client_socket.recv(SIZE).decode(FORMAT)
            print(welcome_msg)
            
            while True:
                command = input("Enter command (LIST/UPLOAD/QUIT): ").strip().upper()
                
                if command == "LIST":
                    list_files(client_socket)
                elif command == "UPLOAD":
                    upload_file(client_id, client_socket)
                elif command == "QUIT":
                    client_socket.send("QUIT".encode(FORMAT))
                    print("Disconnecting from the server...")
                    break 
                else:
                    print("Invalid command. Please enter LIST, UPLOAD, or QUIT.")
                    
        except ConnectionError as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    main()



