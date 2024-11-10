import socket
import threading
import json
import pygame
from dataclasses import dataclass, asdict
from random import randint
import time

@dataclass
class Player:
    pos: dict
    rect: dict
    color: str

@dataclass
class Ball:
    pos: dict
    rect: dict
    color: str
    velocity: dict

class PongServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2) 
        
        self.screen_width = 1280
        self.screen_height = 720
        self.players = {}
        self.ball = Ball(
            pos={'x': 640, 'y': 360},
            rect={'x': 640, 'y': 360, 'width': 15, 'height': 15},
            color='white',
            velocity={'x': 24, 'y': 24}
        )
        self.running = True
        self.game_started = False
        print(f"Server started on {host}:{port}")

    def init_player(self, player_num):
        if player_num == 1:
            return Player(
                pos={'x': 50, 'y': 50},
                rect={'x': 50, 'y': 50, 'width': 10, 'height': 100},
                color='blue'
            )
        else:
            return Player(
                pos={'x': 1230, 'y': 600},
                rect={'x': 1230, 'y': 600, 'width': 10, 'height': 100},
                color='red'
            )

    def handle_client(self, client_socket, player_num):
        player = self.init_player(player_num)
        self.players[player_num] = player

        while self.running:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                command = json.loads(data)
                if 'move' in command:
                    self.move_player(player_num, command['move'])
                
                game_state = self.get_game_state()
                client_socket.send(json.dumps(game_state).encode('utf-8'))
                
            except Exception as e:
                print(f"Error handling client {player_num}: {e}")
                break

        del self.players[player_num]
        client_socket.close()

    def move_player(self, player_num, direction):
        player = self.players[player_num]
        if direction == 'UP' and player.pos['y'] > 0:
            player.pos['y'] -= 25
            player.rect['y'] = player.pos['y']
        elif direction == 'DOWN' and player.pos['y'] < self.screen_height - player.rect['height']:
            player.pos['y'] += 25
            player.rect['y'] = player.pos['y']

    def update_ball(self):
        self.ball.pos['x'] += self.ball.velocity['x']
        self.ball.pos['y'] += self.ball.velocity['y']
        self.ball.rect['x'] = self.ball.pos['x']
        self.ball.rect['y'] = self.ball.pos['y']

        if self.ball.rect['y'] <= 0 or self.ball.rect['y'] + self.ball.rect['height'] >= self.screen_height:
            self.ball.velocity['y'] = -self.ball.velocity['y']

        for player in self.players.values():
            if (self.ball.rect['x'] < player.rect['x'] + player.rect['width'] and
                self.ball.rect['x'] + self.ball.rect['width'] > player.rect['x'] and
                self.ball.rect['y'] < player.rect['y'] + player.rect['height'] and
                self.ball.rect['y'] + self.ball.rect['height'] > player.rect['y']):
                self.ball.velocity['x'] = -self.ball.velocity['x']

        if self.ball.rect['x'] <= 0 or self.ball.rect['x'] + self.ball.rect['width'] >= self.screen_width:
            self.ball.pos = {'x': 640, 'y': 360}
            self.ball.rect['x'] = self.ball.pos['x']
            self.ball.rect['y'] = self.ball.pos['y']
            self.ball.velocity = {
                'x': randint(-4, 4) or 4,
                'y': randint(-4, 4) or 4
            }

    def get_game_state(self):
        return {
            'players': {str(k): asdict(v) for k, v in self.players.items()},
            'ball': asdict(self.ball)
        }

    def game_loop(self):
        while self.running:
            if len(self.players) == 2:
                self.update_ball()
            time.sleep(1/60)  

    def start(self):
        game_thread = threading.Thread(target=self.game_loop)
        game_thread.start()

        player_num = 1
        while self.running:
            try:
                client_socket, addr = self.server.accept()
                if player_num <= 2:
                    print(f"Player {player_num} connected from {addr}")
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, player_num)
                    )
                    client_thread.start()
                    player_num += 1
                else:
                    client_socket.close()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break

    def stop(self):
        self.running = False
        self.server.close()

if __name__ == "__main__":
    server = PongServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped")
