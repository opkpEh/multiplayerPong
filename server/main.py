import pygame
from random import randint
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

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Multiplayer pong")
clock = pygame.time.Clock()
running = True

player1 = Player(pygame.Vector2(50, 50), pygame.Rect(50, 50, 10, 100), pygame.Color('blue'))
player2 = Player(pygame.Vector2(1230, 600), pygame.Rect(1230, 600, 10, 100), pygame.Color('red'))

ball = Ball(
    pos=pygame.Vector2(640, 360),
    rect=pygame.Rect(640, 360, 15, 15),
    color=pygame.Color('white'),
    velocity=pygame.Vector2(randint(-4, 4), randint(-4, 4))
)

ball.velocity.x = 12
ball.velocity.y = 12

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player1.pos.y > 0:
        player1.pos.y -= 25
    if keys[pygame.K_DOWN] and player1.pos.y < screen.get_height() - player1.rect.height:
        player1.pos.y += 25
    if keys[pygame.K_w] and player2.pos.y > 0:
        player2.pos.y -= 25
    if keys[pygame.K_s] and player2.pos.y < screen.get_height() - player2.rect.height:
        player2.pos.y += 25

    # Update player rects based on positions
    player1.rect.topleft = player1.pos
    player2.rect.topleft = player2.pos

    ball.pos += ball.velocity
    ball.rect.topleft = ball.pos

    if ball.rect.top <= 0 or ball.rect.bottom >= screen.get_height():
        ball.velocity.y = -ball.velocity.y

    if ball.rect.colliderect(player1.rect) or ball.rect.colliderect(player2.rect):
        ball.velocity.x = -ball.velocity.x

    if ball.rect.left <= 0 or ball.rect.right >= screen.get_width():
        ball.pos = pygame.Vector2(640, 360)
        ball.velocity = pygame.Vector2(randint(-4, 4), randint(-4, 4))
        if ball.velocity.x == 0:
            ball.velocity.x = 4
        if ball.velocity.y == 0:
            ball.velocity.y = 4

    screen.fill("pink")
    pygame.draw.rect(screen, player1.color, player1.rect)
    pygame.draw.rect(screen, player2.color, player2.rect)
    pygame.draw.rect(screen, ball.color, ball.rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
