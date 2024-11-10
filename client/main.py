import pygame
import socket
import json
import threading
from dataclasses import dataclass

@dataclass
class Player:
    pos: pygame.Vector2
    rect: pygame.Rect
    color: pygame.Color

@dataclass
class Ball:
    pos: pygame.Vector2
    rect: pygame.Rect
    color: pygame.Color
    velocity: pygame.Vector2

class PongClient:
    def __init__(self, host='localhost', port=5555):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Multiplayer Pong")
        self.clock = pygame.time.Clock()
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
        self.running = False
        self.game_state = None

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def dict_to_player(self, data):
        return Player(
            pos=pygame.Vector2(data['pos']['x'], data['pos']['y']),
            rect=pygame.Rect(
                data['rect']['x'],
                data['rect']['y'],
                data['rect']['width'],
                data['rect']['height']
            ),
            color=pygame.Color(data['color'])
        )

    def dict_to_ball(self, data):
        return Ball(
            pos=pygame.Vector2(data['pos']['x'], data['pos']['y']),
            rect=pygame.Rect(
                data['rect']['x'],
                data['rect']['y'],
                data['rect']['width'],
                data['rect']['height']
            ),
            color=pygame.Color(data['color']),
            velocity=pygame.Vector2(data['velocity']['x'], data['velocity']['y'])
        )

    def receive_game_state(self):
        while self.running:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if data:
                    game_state = json.loads(data)
                    self.game_state = {
                        'players': {
                            k: self.dict_to_player(v)
                            for k, v in game_state['players'].items()
                        },
                        'ball': self.dict_to_ball(game_state['ball'])
                    }
            except Exception as e:
                print(f"Error receiving game state: {e}")
                self.running = False
                break

    def send_command(self, command):
        try:
            self.client.send(json.dumps(command).encode('utf-8'))
        except Exception as e:
            print(f"Error sending command: {e}")
            self.running = False

    def run(self):
        self.running = True
        
        receive_thread = threading.Thread(target=self.receive_game_state)
        receive_thread.start()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.send_command({'move': 'UP'})
            if keys[pygame.K_DOWN]:
                self.send_command({'move': 'DOWN'})

            if self.game_state:
                self.screen.fill("pink")
                
                for player in self.game_state['players'].values():
                    pygame.draw.rect(self.screen, player.color, player.rect)
                
                ball = self.game_state['ball']
                pygame.draw.rect(self.screen, ball.color, ball.rect)
                
                pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()
        self.client.close()

if __name__ == "__main__":
    client = PongClient()
    if client.connect():
        client.run()
