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
        "username": "user1",
        "password": "pass1"
    }),
    "login2": json.dumps({
        "username": "user2",
        "password": "pass2"
    }),
    "logout": json.dumps({
        "token": "2-c8f06d1ee39d4a01bc90e65d5b8419c9"
    }),
    "search_battle1": json.dumps({
        "token": "1-4d99af9a56e3497cb8f0fd7b20dd69bf",
        "player_id": 1,
    }),
    "search_battle2": json.dumps({
        "token": "2-46c8f73a7f7d4408aa26a3fb8a111d0c",
        "player_id": 2,
    }),
    "battle": json.dumps({
        "room_id": "249a2990-090d-476e-ad8d-61cd8029ada2",
        "token": "2-46c8f73a7f7d4408aa26a3fb8a111d0c",
        "enemy_token": "1-4d99af9a56e3497cb8f0fd7b20dd69bf",
        "action": 1,
        "attack_type": 2,
        "flip": False,
        "health": 100,
        "armor": 1,
        "x": 650,
        "y": 380,
        "damage": 20
    }),
}

def send_request(endpoint, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 8891))
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
    response = send_request('/login', test_data['login1'])
    print("\nLogin Response:")
    print(response)
    
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
    # response = send_request('/search_battle', test_data['search_battle1'])
    # print("\n Search Battle Response:")
    # print(response)