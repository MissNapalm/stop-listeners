import psutil

def list_listening_tcp_connections():
    listening_connections = {}
    for conn in psutil.net_connections(kind='tcp'):
        if conn.status == psutil.CONN_LISTEN:
            process_name = "Unknown"
            try:
                process = psutil.Process(conn.pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

            connection_info = {
                'laddr': f"{conn.laddr.ip}:{conn.laddr.port}",
                'process_name': process_name,
                'essential': False
            }
            listening_connections[conn.pid] = connection_info
    
    return listening_connections

def close_tcp_connection(pid):
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        print(f"Terminating process {process_name} (PID: {pid})")
        process.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        print("Process not found or unable to terminate.")

def main():
    listening_connections = list_listening_tcp_connections()
    
    if not listening_connections:
        print("No listening TCP connections found.")
        return

    print("Listening TCP connections:")
    for index, (pid, connection_info) in enumerate(listening_connections.items()):
        process_name = connection_info['process_name']
        connection_status = "essential" if connection_info['essential'] else "optional"
        print(f"{index + 1}. {connection_status} - PID: {pid}, Local Address: {connection_info['laddr']}, Process: {process_name}")
    
    choice = input("Enter the index of the connection or process to close (or 'all' to close all, or 'q' to quit): ")

    if choice == 'q':
        return
    elif choice == 'all':
        for pid in listening_connections.keys():
            close_tcp_connection(pid)
        print("All listening connections have been closed.")
    else:
        try:
            choice = int(choice)
            if 1 <= choice <= len(listening_connections):
                pid = list(listening_connections.keys())[choice - 1]
                if listening_connections[pid]['essential']:
                    confirmation = input("This is an essential connection. Are you sure you want to close it? (y/n): ").strip().lower()
                    if confirmation == 'y':
                        close_tcp_connection(pid)
                    else:
                        print("Connection not closed.")
                else:
                    close_tcp_connection(pid)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a valid index, 'all', or 'q' to quit.")

if __name__ == "__main__":
    main()