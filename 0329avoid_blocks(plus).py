import pygame
import random

pygame.init()

# 窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("升级版：躲避方块")

# 玩家
player_size = 20
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 7

# 敌人
enemy_size = 50
enemies = []

def create_enemy():
    x = random.randint(0, WIDTH - enemy_size)
    y = 0
    return [x, y]

# 初始一个敌人
enemies.append(create_enemy())

clock = pygame.time.Clock()

running = True
game_over = False

# 时间控制
start_time = pygame.time.get_ticks()

final_time = 0

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        #计算游戏时间
        seconds = (pygame.time.get_ticks() - start_time) / 1000

        #敌人速度随时间增加
        enemy_speed = 5 + seconds * 0.2
        enemy_speed = min(enemy_speed, 15)  # 限制最大速度

        #敌人数量逐渐增加
        if random.random() < 0.02:
            enemies.append(create_enemy())

        #玩家控制
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        #限制边界
        player_x = max(0, min(WIDTH - player_size, player_x))

        #移动敌人
        for enemy in enemies:
            enemy[1] += enemy_speed

            if enemy[1] > HEIGHT:
                enemy[1] = 0
                enemy[0] = random.randint(0, WIDTH - enemy_size)

        #碰撞检测
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_over = True
                final_time = seconds

    #画面
    screen.fill((0, 0, 0))
    #计时器
    font = pygame.font.Font(None, 36)

    if not game_over:
        time_text = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))

        pygame.draw.rect(screen, (255, 0, 0), (player_x, player_y, player_size, player_size))

        for enemy in enemies:
            pygame.draw.rect(screen, (0, 255, 0), (enemy[0], enemy[1], enemy_size, enemy_size))
    else:
        font = pygame.font.Font(None, 74)
        big_font = pygame.font.Font(None, 74)
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        # 获取文字矩形，并设置居中
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)


        score_text = font.render(f"Survival Time: {int(final_time)} s", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(score_text, score_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
