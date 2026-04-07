import pygame
import random

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("bgm.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# 窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("升级版：躲避方块")

game_state = "start"
best_time = 0

invincible_time = 0

#暂停相关
pause_start = 0
paused_duration = 0

# 玩家
player_size = 20
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 7

# 敌人
initial_enemy_size = 50
min_enemy_size = 20
enemies = []

def create_enemy(size):
    x = random.randint(0, WIDTH - size)
    y = 0
    return [x, y]

def reset_game():
    global player_x, enemies, start_time, final_time
    global invincible_time, game_state, paused_duration

    player_x = WIDTH // 2
    enemies.clear()
    enemies.append(create_enemy(initial_enemy_size))

    start_time = pygame.time.get_ticks()
    invincible_time = pygame.time.get_ticks()
    paused_duration = 0

    final_time = 0
    game_state = "start"

    pygame.mixer.music.stop()
    pygame.mixer.music.play(-1)

# 初始敌人
enemies.append(create_enemy(initial_enemy_size))

clock = pygame.time.Clock()
running = True

start_time = pygame.time.get_ticks()
final_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # 开始游戏
            if game_state == "start" and event.key == pygame.K_SPACE:
                game_state = "playing"
                start_time = pygame.time.get_ticks()
                invincible_time = pygame.time.get_ticks()
                paused_duration = 0

            #重开
            if event.key == pygame.K_LSHIFT:
                reset_game()

            #暂停功能
            if event.key == pygame.K_p:

                if game_state == "playing":
                    game_state = "paused"
                    pause_start = pygame.time.get_ticks()
                    pygame.mixer.music.pause()

                elif game_state == "paused":
                    game_state = "playing"
                    paused_duration += pygame.time.get_ticks() - pause_start
                    pygame.mixer.music.unpause()

    # 游戏逻辑
    if game_state == "playing":

        seconds = (pygame.time.get_ticks() - start_time - paused_duration) / 1000

        enemy_size = initial_enemy_size - seconds * 1.5
        enemy_size = max(min_enemy_size, enemy_size)
        enemy_size = int(enemy_size)

        enemy_speed = 5 + seconds * 0.2
        enemy_speed = min(enemy_speed, 15)

        if random.random() < 0.02:
            enemies.append(create_enemy(enemy_size))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - player_size, player_x))

        for enemy in enemies:
            enemy[1] += enemy_speed

            if enemy[1] > HEIGHT:
                enemy[1] = 0
                enemy[0] = random.randint(0, WIDTH - enemy_size)

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)

            if pygame.time.get_ticks() - invincible_time > 1000:
                if player_rect.colliderect(enemy_rect):
                    game_state = "game_over"
                    final_time = seconds

                    if seconds > best_time:
                        best_time = seconds

                    pygame.mixer.music.stop()

    # ====== 画面 ======
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)

    if game_state == "start":
        font = pygame.font.Font(None, 74)
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    elif game_state == "playing":
        time_text = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))

        pygame.draw.rect(screen, (255, 0, 0),
                         (player_x, player_y, player_size, player_size))

        for enemy in enemies:
            pygame.draw.rect(screen, (0, 255, 0),
                             (enemy[0], enemy[1], enemy_size, enemy_size))

    elif game_state == "paused":
        #先画游戏画面
        time_text = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))

        pygame.draw.rect(screen, (255, 0, 0),
                         (player_x, player_y, player_size, player_size))

        for enemy in enemies:
            pygame.draw.rect(screen, (0, 255, 0),
                             (enemy[0], enemy[1], enemy_size, enemy_size))

        #半透明黑色遮罩（变暗）
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        #暂停文字
        big_font = pygame.font.Font(None, 74)
        pause_text = big_font.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        tip = font.render("Press p to Resume", True, (200, 200, 200))
        screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    else:
        big_font = pygame.font.Font(None, 74)
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

        best_text = font.render(f"Best: {int(best_time)} s", True, (255, 255, 0))
        screen.blit(best_text, best_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))

        score_text = font.render(f"Survival Time: {int(final_time)} s", True, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        restart_text = font.render("Press LSHIFT to Restart", True, (200, 200, 200))
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
