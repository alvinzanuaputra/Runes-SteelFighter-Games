from glob import glob
from datetime import datetime
from controller import login, logout, register, get_player_data, handle_battle, update_match
import json
import time
import uuid
from room import Room

TIMEOUT = 5 * 60 	
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.matching = {}
		self.rooms = {}
  
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
			messagebody = messagebody.encode()

		response = response_headers.encode() + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		requests = data.split("\r\n")
		#print(requests)
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

	def http_post(self,object_address,headers, body):  
		if (object_address == '/register'):
			output = register(body)
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(400, 'Bad Request', output, headers)
		elif (object_address == '/login'):
			output, session_player = login(body)
			token = json.loads(output).get('token')
			if token:
				self.sessions[token] = session_player
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(401, 'Unauthorized', output, headers)
		elif (object_address == '/logout'):
			output, token = logout(body)
			if token in self.sessions:
				del self.sessions[token]
			headers['Content-type']='application/json'
			if json.loads(output).get('status') == 'fail':
				return self.response(401, 'Unauthorized', output, headers)
		elif (object_address == '/search_battle'):
			body_json = json.loads(body)
			token = body_json.get("token")
			player_id = body_json.get("player_id")

			if not token or not player_id:
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Token dan player_id wajib ada"
				}), {'Content-type': 'application/json'})

			# Cek valid session
			player = self.sessions.get(token)
			if not player:
				return self.response(401, 'Unauthorized', json.dumps({
					"status": "fail",
					"message": "Token tidak valid"
				}), {'Content-type': 'application/json'})

			# Cari room yang sedang menunggu
			joined_room = None
			for room_id, room in self.rooms.items():
				if room.is_waiting() and not room.is_expired() and room.player1_id != player_id:
					room.join(player_id, token)
					joined_room = room
					break

			# Jika belum ada room, buat room baru
			if not joined_room:
				room_id = str(uuid.uuid4())
				new_room = Room(room_id, player_id, token)
				self.rooms[room_id] = new_room
				joined_room = new_room

				# Tunggu maksimal 5 menit
				start_time = time.time()
				while not joined_room.is_ready():
					if joined_room.is_expired():
						del self.rooms[room_id]
						return self.response(408, 'Request Timeout', json.dumps({
							"status": "fail",
							"message": "Tidak ada lawan ditemukan dalam 5 menit"
						}), {'Content-type': 'application/json'})
					time.sleep(0.1)
     
			# Ambil token musuh
			enemy_token = (
				joined_room.player1_token if joined_room.player2_token == token
				else joined_room.player2_token
			)
			enemy = self.sessions.get(enemy_token)

			if not enemy:
				return self.response(500, 'Server Error', json.dumps({
					"status": "fail",
					"message": "Lawan tidak ditemukan"
				}), {'Content-type': 'application/json'})

			# Tentukan posisi awal
			initial_state_p1 = {
				"x": 0.2 * SCREEN_WIDTH,
				"y": 0.8 * SCREEN_HEIGHT,
				"action": 0,
				"attack_type": None,
				"health": 100,
				"armor": 1
			}
   
			initial_state_p2 = {
				"x": 0.8 * SCREEN_WIDTH,
				"y": 0.8 * SCREEN_HEIGHT,
				"action": 0,
				"attack_type": None,
				"health": 100,
				"armor": 1
			}

			# Atur session untuk kedua player
			if token == joined_room.player1_token:
				p1_token = token
				p2_token = enemy_token
			else:
				p1_token = enemy_token
				p2_token = token

			# Atur state sesuai posisi
			self.sessions[p1_token]["state"] = initial_state_p1
			self.sessions[p2_token]["state"] = initial_state_p2


			return self.response(200, 'OK', json.dumps({
				"status": "ok",
				"message": "Berhasil menemukan lawan",
				"room_id": joined_room.room_id,
				"self_state": self.sessions[token]["state"],
				"enemy_state": self.sessions[enemy_token]["state"],
				"enemy_token": enemy_token,
    			"p1": token == joined_room.player1_token
			}), {'Content-type': 'application/json'})
		elif object_address == '/battle':
			body_json = json.loads(body)
			token = body_json.get("token")
			player = self.sessions.get(token)
			enemy_token = body_json.get("enemy_token")
			enemy = self.sessions.get(enemy_token)

			if not token or not player or not enemy_token or not enemy:
				return self.response(400, 'Bad Request', json.dumps({
					"status": "fail",
					"message": "Token dan enemy_token wajib ada"
			}))
    
			# Jalankan logika pertarungan
			output, player_state, enemy_state = handle_battle(body_json, player, enemy)
			self.sessions[token]["state"] = player_state
			self.sessions[enemy_token]["state"] = enemy_state

			headers['Content-type'] = 'application/json'
			status_code = 200 if json.loads(output).get("status") != 'fail' else 400
			return self.response(200, 'OK', json.dumps({
				"status": "ok",
				"message": "Battle updated",
				"self": self.sessions[token]["state"],
				"enemy": self.sessions[enemy_token]["state"]
			}), headers)


		return self.response(200, 'OK', output, headers)
		
	def http_put(self, object_address, headers, body):
		if object_address == '/update_match':
			try:
				body_json = json.loads(body)
				token = body_json.get("token")
				player_id = int(body_json.get("player_id"))
				room_id = body_json.get("room_id")
				is_win = body_json.get("is_win", False)
				enemy_token = body_json.get("enemy_token")
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

			room = self.rooms.get(room_id)
			if room:
				del self.rooms[room_id]

			output = update_match(player_id, is_win)
			return self.response(200, 'OK', output, {'content-type': 'application/json'})
		
		return self.response(501, 'Not Implemented', 'PUT method is not implemented', headers)


if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET /user/1 HTTP/1.0')
	print(d)
	# d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	# print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
	# d = httpserver.http_get('testing.txt')
	# print(d)

	# data_register = {
	# 	"username": "testuser",
	# 	"password": "testpass",
	# 	"nickname": "Test User"
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