import pygame
import random
import asyncio

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()

# Player paddle
PADDLE_W, PADDLE_H = 12, 90
paddle_x = 40
paddle_y = SCREEN_HEIGHT // 2 - PADDLE_H // 2
paddle_speed = 5

# AI paddle
ai_paddle_x = SCREEN_WIDTH - PADDLE_W - 40
ai_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_H // 2
ai_paddle_speed = 3

# Ball
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_radius = 10
ball_dx = random.choice([-3, 3])
ball_dy = random.uniform(-2.5, 2.5)

# Score
score = 0
score_2 = 0

# Font
font = pygame.font.SysFont("Arial", 20)
red = (255, 0, 0)

# AI targeting
target_y = SCREEN_HEIGHT // 2
ai_next_retarget = 0

game_over = False
game_win = False
game_over_until = 0
game_win_until = 0


def resetBall(towards=1):
    global ball_dx, ball_dy
    bx = SCREEN_WIDTH // 2
    by = SCREEN_HEIGHT // 2
    ball_dx = 3 * towards
    ball_dy = random.uniform(-2.5, 2.5)
    return bx, by


def resetGame():
    global paddle_y, ai_paddle_y, score, score_2
    global ball_x, ball_y, game_over, game_win

    paddle_y = SCREEN_HEIGHT // 2 - PADDLE_H // 2
    ai_paddle_y = SCREEN_HEIGHT // 2 - PADDLE_H // 2

    score = 0
    score_2 = 0

    ball_x, ball_y = resetBall()

    game_over = False
    game_win = False


async def main():
    global paddle_y, ai_paddle_y, ball_x, ball_y
    global ball_dx, ball_dy, score, score_2
    global game_over, game_win, game_over_until, game_win_until
    global target_y, ai_next_retarget

    run = True

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        now = pygame.time.get_ticks()

        #Player controls
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            paddle_y -= paddle_speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            paddle_y += paddle_speed

        paddle_y = max(0, min(paddle_y, SCREEN_HEIGHT - PADDLE_H))

        #Ball 
        ball_x += ball_dx
        ball_y += ball_dy

        #Wall bounce
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= SCREEN_HEIGHT:
            ball_dy *= -1
            ball_y += ball_dy

        #Rectangles
        paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_W, PADDLE_H)
        ai_rect = pygame.Rect(ai_paddle_x, ai_paddle_y, PADDLE_W, PADDLE_H)

        ball_rect = pygame.Rect(
            ball_x - ball_radius,
            ball_y - ball_radius,
            ball_radius * 2,
            ball_radius * 2
        )

        #AI 
        if ball_dx > 0 and ball_x > SCREEN_WIDTH * 0.55 and now >= ai_next_retarget:
            offset = random.randint(-80, 80)
            target_y = ball_y + offset
            ai_next_retarget = now + random.randint(120, 300)

        ai_center = ai_paddle_y + PADDLE_H / 2
        diff = target_y - ai_center

        if abs(diff) > 6:
            if diff > 0:
                ai_paddle_y += ai_paddle_speed
            else:
                ai_paddle_y -= ai_paddle_speed

        ai_paddle_y = max(0, min(ai_paddle_y, SCREEN_HEIGHT - PADDLE_H))

        
        if ball_rect.colliderect(paddle_rect) and ball_dx < 0:
            ball_x = paddle_rect.right + ball_radius
            ball_dx *= -1

        # AI  collision
        if ball_rect.colliderect(ai_rect) and ball_dx > 0:
            ball_x = ai_rect.left - ball_radius
            ball_dx *= -1

        # Score 
        if ball_x - ball_radius < 0:
            score_2 += 1
            ball_x, ball_y = resetBall(1)

        if ball_x + ball_radius > SCREEN_WIDTH:
            score += 1
            ball_x, ball_y = resetBall(-1)

        # W/ L
        if score >= 10 and not game_win:
            game_win = True
            game_win_until = now + 1000

        if score_2 >= 10 and not game_over:
            game_over = True
            game_over_until = now + 1000

    
        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (255, 255, 255), paddle_rect)
        pygame.draw.rect(screen, (255, 255, 255), ai_rect)

        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (int(ball_x), int(ball_y)),
            ball_radius
        )

        text = font.render(f"Player 1: {score}", True, red)
        text2 = font.render(f"Player 2 Ai: {score_2}", True, red)

        screen.blit(text, (20, 20))
        screen.blit(text2, (SCREEN_WIDTH - 120, 20))

        if game_win:
            win = font.render("YOU WIN!", True, red)
            screen.blit(win, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))

            if now >= game_win_until:
                resetGame()

        if game_over:
            lost = font.render("YOU LOST!", True, red)
            screen.blit(lost, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))

            if now >= game_over_until:
                resetGame()

        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
pygame.quit()