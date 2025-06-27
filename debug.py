import json
import socket

# Test data untuk requst http pada localhost:8888
test_data = {
    "register": json.dumps({
        "username": "testuser2",
        "password": "testpass2",
        "nickname": "Test User 2"
    }),
    "login1": json.dumps({
        "username": "testuser",
        "password": "testpass"
    }),
    "login2": json.dumps({
        "username": "testuser2",
        "password": "testpass2"
    }),
    "logout": json.dumps({
        "token": "2-c8f06d1ee39d4a01bc90e65d5b8419c9"
    }),
    "search_battle1": json.dumps({
        "token": "1-d8af9f13128149af8061bb2a03e7f963",
        "player_id": 1,
    }),
    "search_battle2": json.dumps({
        "token": "2-c4ef6a8c4cb740efabac01f2b5285ca5",
        "player_id": 2,
    }),
    "battle": json.dumps({
        "room_id": "1175368f-fdb5-4d97-89f9-68aad1ad47a4",
        "token": "2-08efc1c2f17c44c2a3137ab3029af93b",
        "enemy_token": "1-b88c5f9b5ea44d3ba5cebdffc3c2bcc4",
        "action": 1,
        "attack_type": 2,
        "x": 650,
        "y": 280,
        "damage": 20
    }),
}

def send_request(endpoint, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8888))
        request = f"POST {endpoint} HTTP/1.1\r\n"
        request += "Host: localhost\r\n"
        request += "Content-Type: application/json\r\n"
        request += f"Content-Length: {len(data)}\r\n"
        request += "\r\n"
        request += data
        
        s.sendall(request.encode())
        
        response = b""
        while True:
            part = s.recv(4096)
            if not part:
                break
            response += part
            
    return response.decode()

def send_get_request(endpoint):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8888))
        request = f"GET {endpoint} HTTP/1.1\r\n"
        request += "Host: localhost\r\n"
        request += "\r\n"
        
        s.sendall(request.encode())
        
        response = b""
        while True:
            part = s.recv(4096)
            if not part:
                break
            response += part
            
    return response.decode()

if __name__ == "__main__":
    # Test register
    # response = send_request('/register', test_data['register'])
    # print("Register Response:")
    # print(response)

    # Test login
    # response = send_request('/login', test_data['login1'])
    # print("\nLogin Response:")
    # print(response)
    
    # response = send_request('/login', test_data['login2'])
    # print("\nLogin Response:")
    # print(response)

    # Test logout
    # response = send_request('/logout', test_data['logout'])
    # print("\nLogout Response:")
    # print(response)

    # Test battle
    # response = send_request('/battle', test_data['battle'])
    # print("\nBattle Response:")
    # print(response)
    
    # Test get player data
    # response = send_get_request('/user/2')
    # print("\nGet Player Data Response:")
    # print(response)
    
    # Test search battle
    response = send_request('/search_battle', test_data['search_battle1'])
    print("\n Search Battle Response:")
    print(response)