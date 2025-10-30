import socket
import ssl

host = "www.google.com"
port = 443

context = ssl.create_default_context()
client = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)
client.connect((host, port))

request = (
    f"GET / HTTP/1.1\r\n"
    f"Host: {host}\r\n"
    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
    f"Connection: close\r\n\r\n"
)

client.send(request.encode())

response = b""
while True:
    data = client.recv(4096)
    if not data:
        break
    response += data

print(response.decode(errors="ignore"))
client.close()