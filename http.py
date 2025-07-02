from glob import glob
from datetime import datetime
from controller import login, logout, register, get_player_data, handle_battle, update_match, get_session, delete_session
from controller import search_available_room, create_room, create_session
import json
from redis_client import get_battle_state, save_battle_state, delete_battle_state

TIMEOUT = 5 * 60 	
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

class HttpServer:
	def parse_headers(self, header_list):
		headers = {}
		for line in header_list:
			if ": " in line:
				key, value = line.split(": ", 1)
				headers[key.strip()] = value.strip()
		return headers

	def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")

		response_headers=''
		for i in resp:
			response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
		if (type(messagebody) is not bytes):
			messagebody = messagebody.encode('utf-8')

		response = response_headers.encode('utf-8') + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		requests = data.split("\r\n")
		# print(requests)
		baris = requests[0]
		#print(baris)
		all_headers = [n for n in requests[1:] if n!='']

		j = baris.split(" ")
		try:
			method=j[0].upper().strip()
			object_address = j[1].strip()
			if (method == 'GET'):
				parsed_headers = self.parse_headers(all_headers)
				return self.http_get(object_address, parsed_headers)
			if (method=='POST'):
				body = data.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in data else ""
				parsed_headers = self.parse_headers(all_headers)
				return self.http_post(object_address, parsed_headers, body)
			if (method=='PUT'):
				body = data.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in data else ""
				parsed_headers = self.parse_headers(all_headers)
				return self.http_put(object_address, parsed_headers, body)
			else:
				return self.response(400,'Bad Request','',{})
		except IndexError:
			return self.response(400,'Bad Request','',{})

	def http_get(self,object_address,headers):
		if object_address.startswith('/user/'):
			try:
				user_id = object_address.split('/user/')[1]
				data = get_player_data(user_id)
				headers = {'Content-type': 'application/json'}
				if json.loads(data).get('status') == 'fail':
					return self.response(404, 'Not Found', data, headers)
				return self.response(200, 'OK', data, headers)
			except Exception as e:
				return self.response(500, 'Internal Server Error', str(e), {})

		return self.response(404, 'Not Found', json.dumps({
			"status": "fail",
			"message": "Endpoint tidak ditemukan"
		}), {'content-type': 'application/json'})

	def http_post(self,object_address,headers, body):  
		if (object_address == '/register'):
			output = register(body)
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(400, 'Bad Request', output, headers)

			return self.response(200, 'OK', output, headers)
		elif (object_address == '/login'):
			output = login(body)
			if json.loads(output).get('status') == 'ok':
				token = json.loads(output).get('token')
				user_id = json.loads(output).get('user_id')
				create_session(token, user_id)
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(401, 'Unauthorized', output, headers)

			return self.response(200, 'OK', output, headers)
		elif (object_address == '/logout'):
			token = json.loads(body).get('token')

			is_login = get_session(token)
			if not is_login:
				return self.response(401, 'Unauthorized', json.dumps({
					"status": "fail",
					"message": "Token tidak valid"
				}), {'Content-type': 'application/json'})
    
			delete_session(token)
			output = logout(token)
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(401, 'Unauthorized', output, headers)

			return self.response(200, 'OK', output, headers)
		elif object_address == '/search_battle':
			body_json = json.loads(body)
			token = body_json.get("token")
			player_id = body_json.get("player_id")

			if not token or not player_id:
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Token dan player_id wajib ada"
				}), {'Content-type': 'application/json'})

			# Cek valid session dari database
			current_session = get_session(token)
			if not current_session:
				return self.response(401, 'Unauthorized', json.dumps({
					"status": "fail",
					"message": "Token tidak valid"
				}), {'Content-type': 'application/json'})
			# Coba cari room yang available
			joined_room = search_available_room(player_id, token)
			# Jika tidak ada room, buat room baru dan tunggu lawan
			if joined_room is None:
				joined_room = create_room(player_id, token)
				if joined_room is None:
					return self.response(408, 'Request Timeout', json.dumps({
						"status": "fail",
						"message": "Tidak ada lawan ditemukan dalam 5 menit"
					}), {'Content-type': 'application/json'})

			# Tentukan token musuh
			enemy_token = (
				joined_room.player1_token if joined_room.player2_token == token
				else joined_room.player2_token
			)
			enemy_session = get_session(enemy_token)
			if enemy_session is None:
				return self.response(500, 'Server Error', json.dumps({
					"status": "fail",
					"message": "Lawan tidak ditemukan"
				}), {'Content-type': 'application/json'})

			# Atur posisi awal
			initial_state_p1 = {
				"token": joined_room.player1_token,
				"x": 0.2 * SCREEN_WIDTH,
				"y": 0.8 * SCREEN_HEIGHT,
				"action": 0,
				"attack_type": None,
				"health": 100,
				"armor": 1
			}

			initial_state_p2 = {
				"token": joined_room.player2_token,
				"x": 0.8 * SCREEN_WIDTH,
				"y": 0.8 * SCREEN_HEIGHT,
				"action": 0,
				"attack_type": None,
				"health": 100,
				"armor": 1
			}
   
			# Tentukan posisi berdasarkan urutan player
			save_battle_state(joined_room.id, {
				"state_p1": initial_state_p1,
				"state_p2": initial_state_p2,
				"p1_token": joined_room.player1_token, 
				"p2_token": joined_room.player2_token 
			})
			
			return self.response(200, 'OK', json.dumps({
				"status": "ok",
				"message": "Berhasil menemukan lawan",
				"room_id": joined_room.id, 
				"self_state": token == joined_room.player1_token and initial_state_p1 or initial_state_p2,
				"enemy_state": token == joined_room.player1_token and initial_state_p2 or initial_state_p1,
				"enemy_token": enemy_token,
				"p1": (token == joined_room.player1_token)
			}), {'Content-type': 'application/json'})
		elif object_address == '/battle':
			body_json = json.loads(body)
			token = body_json.get("token")
			enemy_token = body_json.get("enemy_token")
			room_id = body_json.get("room_id")

			if not token or not enemy_token or not room_id:
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Token, enemy_token, dan room_id wajib ada"
				}), {'Content-type': 'application/json'})

			# Ambil state pertarungan dari Redis
			battle_state = get_battle_state(room_id)
			if not battle_state:
				return self.response(404, 'Not Found', json.dumps({
					"status": "fail",
					"message": "Pertarungan tidak ditemukan"
				}), {'Content-type': 'application/json'})

			# Tentukan siapa pemain dan musuh berdasarkan token
			if token == battle_state["state_p1"]["token"]:
				player_state = battle_state["state_p1"]
				enemy_state = battle_state["state_p2"]
			elif token == battle_state["state_p2"]["token"]:
				player_state = battle_state["state_p2"]
				enemy_state = battle_state["state_p1"]
			else:
				return self.response(403, 'Forbidden', json.dumps({
					"status": "fail",
					"message": "Token tidak valid untuk room ini"
				}), {'Content-type': 'application/json'})

			output_json, updated_player_state, updated_enemy_state = handle_battle(
				body_json, player_state, enemy_state
			)

			# Update state di Redis
			if token == battle_state["p1_token"]:
				battle_state["state_p1"] = updated_player_state
				battle_state["state_p2"] = updated_enemy_state
			else:
				battle_state["state_p2"] = updated_player_state
				battle_state["state_p1"] = updated_enemy_state

			save_battle_state(room_id, battle_state)

			status = json.loads(output_json).get("status")
			response_code = 200 if status != "fail" else 400

			return self.response(response_code, 'OK', json.dumps({
				"status": "ok" if status != "fail" else "fail",
				"message": "Battle updated",
				"self": updated_player_state,
				"enemy": updated_enemy_state
			}), {'Content-type': 'application/json'})

		return self.response(404, 'Not Found', json.dumps({
			"status": "fail",
			"message": "Endpoint tidak ditemukan",
		}), {'Content-type': 'application/json'})
		
	def http_put(self, object_address, headers, body):
		if object_address == '/update_match':
			try:
				body_json = json.loads(body)
				token = body_json.get("token")
				player_id = int(body_json.get("player_id"))
				room_id = body_json.get("room_id")
				is_win = body_json.get("is_win", False)
			except (ValueError, TypeError, json.JSONDecodeError):
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Input tidak valid"
				}), {'content-type': 'application/json'})

			if not token or not player_id or not room_id:
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Token, player_id, dan room_id wajib ada"
				}), {'content-type': 'application/json'})
    
			player_session = get_session(token)
			if not player_session:
				return self.response(403, 'Forbidden', json.dumps({
					"status": "fail",
					"message": "Token tidak valid"
				}), {'content-type': 'application/json'})

			output = update_match(player_id, is_win)
			delete_battle_state(room_id)
			return self.response(200, 'OK', output, {'content-type': 'application/json'})

		return self.response(404, 'Not Found', json.dumps({
			"status": "fail",
			"message": "Endpoint tidak ditemukan"
		}), {'content-type': 'application/json'})
		
if __name__=="__main__":
	httpserver = HttpServer()
	# d = httpserver.proses('GET /user/1 HTTP/1.0')
	# print(d)
	# d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	# print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
	# d = httpserver.http_get('testing.txt')
	# print(d)

	# data_register = {
	# 	"username": "user2",
	# 	"password": "pass2",
	# 	"nickname": "User2"
	# }
 
	# body_raw = json.dumps(data_register)
	# d = httpserver.http_post('/register', {}, body_raw)
	# print(d)
 
	# data_login = {
	# 	"username": "testuser",
	# 	"password": "testpass"
  	# }
 
	# body_raw = json.dumps(data_login)
	# d = httpserver.http_post('/login', {}, body_raw)
	# print(d)
 
	# data_logout = {
	# 	"token": "1-c1431ca564bb40b5809e7ea453aaa219"
	# }
 
	# body_raw = json.dumps(data_logout)
	# d = httpserver.http_post('/logout', {}, body_raw)
	# print(d)