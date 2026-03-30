import pygame
import random

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("Avoid-blocks_plus/bgm.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


# 窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("升级版：躲避方块")

game_state = "start"
best_time = 0
invincible_time = 0


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

    #重置函数
def reset_game():
    global player_x, enemies, start_time, final_time, invincible_time, game_state
    
    player_x = WIDTH // 2
    enemies.clear()
    # 重新加入初始敌人
    enemies.append(create_enemy(initial_enemy_size))
    
    start_time = pygame.time.get_ticks()
    invincible_time = pygame.time.get_ticks() # 重启后给1秒无敌，防止出生点杀
    final_time = 0
    game_state = "start"
    pygame.mixer.music.stop()
    pygame.mixer.music.play(-1)


# 初始一个敌人
enemies.append(create_enemy(initial_enemy_size))

clock = pygame.time.Clock()

running = True
game_over = False

# 时间控制
start_time = pygame.time.get_ticks()

final_time = 0 

while running:
    #监听输入事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # 初始界面按空格开始
            if game_state == "start" and event.key == pygame.K_SPACE:
                game_state = "playing"
                start_time = pygame.time.get_ticks()
                invincible_time = pygame.time.get_ticks() 
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                reset_game()




    if game_state == "playing":
        #计算游戏时间
        seconds = (pygame.time.get_ticks() - start_time) / 1000
        enemy_size = initial_enemy_size - seconds * 1.5
        enemy_size = max(min_enemy_size, enemy_size)
        enemy_size = int(enemy_size)


        #敌人速度随时间增加
        enemy_speed = 5 + seconds * 0.2
        enemy_speed = min(enemy_speed, 15)  # 限制最大速度

        #敌人数量逐渐增加
        if random.random() < 0.02:
            enemies.append(create_enemy(enemy_size))

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
            if pygame.time.get_ticks() - invincible_time > 1000:  # 1秒无敌
                if player_rect.colliderect(enemy_rect):
                    game_state = "game_over"
                    final_time = seconds
                    if seconds > best_time:
                        best_time = seconds

                    pygame.mixer.music.stop()

    screen.fill((0, 0, 0))
    #计时器
    font = pygame.font.Font(None, 36)

    if game_state == "start":
        font = pygame.font.Font(None, 74)
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)


    elif game_state == "playing":

        time_text = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_text, (10, 10))

        pygame.draw.rect(screen, (255, 0, 0), (player_x, player_y, player_size, player_size))

        for enemy in enemies:
            pygame.draw.rect(screen, (0, 255, 0), (enemy[0], enemy[1], enemy_size, enemy_size))

    else:
        big_font = pygame.font.Font(None, 74)
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        best_text = font.render(f"Best: {int(best_time)} s", True, (255, 255, 0))
        best_rect = best_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(best_text, best_rect)

        # 获取文字矩形，并设置居中
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        restart_text = font.render("Press LSHIFT to Restart", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
        screen.blit(restart_text, restart_rect)


        score_text = font.render(f"Survival Time: {int(final_time)} s", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(score_text, score_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
