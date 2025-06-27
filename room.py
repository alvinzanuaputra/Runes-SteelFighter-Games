import time

class Room:
    def __init__(self, room_id, player1_id, player1_token):
        self.room_id = room_id
        self.player1_id = player1_id
        self.player1_token = player1_token
        self.player2_id = None
        self.player2_token = None
        self.status = "waiting"
        self.created_at = time.time()

    def is_waiting(self):
        return self.status == "waiting"

    def join(self, player2_id, player2_token):
        self.player2_id = player2_id
        self.player2_token = player2_token
        self.status = "in_progress"

    def is_expired(self, timeout=300):  # 5 menit
        return (time.time() - self.created_at) > timeout

    def is_ready(self):
        return self.player1_token is not None and self.player2_token is not None
