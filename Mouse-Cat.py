import pygame
import random
import math
import os
import json

pygame.init()
pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def res(path):
    return os.path.join(BASE_DIR, path)

pygame.mixer.music.load(res("bgm.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# ─── 窗口 ────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouse VS Cat")

# ─── 加载图片 ─────────────────────────────────────────────
def load_img(path):
    return pygame.image.load(res(path)).convert_alpha()

mouse_imgs = {
    "grey": [
        load_img("pictures/grey-mouse1.jpg"),
        load_img("pictures/grey-mouse2.jpg"),
        load_img("pictures/grey-mouse3.jpg"),
    ],
    "brown": [
        load_img("pictures/brown-mouse1.jpg"),
        load_img("pictures/brown-mouse2.jpg"),
        load_img("pictures/brown-mouse3.jpg"),
    ],
}

enemy_imgs_orig = {
    "cat":       load_img("pictures/cat.gif"),
    "dog":       load_img("pictures/dog.gif"),
    "cockatiel": load_img("pictures/cockatiel.gif"),
}
ENEMY_TYPES = ["cat", "dog", "cockatiel"]

# ─── 排行榜读写 ───────────────────────────────────────────
SCORES_FILE = res("scores.json")

def load_scores():
    """从 scores.json 读取，返回 dict {name: best_time}"""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_scores(scores: dict):
    """把 scores dict 写入 scores.json"""
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

def update_player_score(name: str, time_val: float):
    """若本次成绩比历史最佳更好则更新并保存"""
    scores = load_scores()
    if name not in scores or time_val > scores[name]:
        scores[name] = round(time_val, 1)
        save_scores(scores)

def get_sorted_leaderboard():
    """返回按成绩从高到低排序的 [(name, time), ...]"""
    scores = load_scores()
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# ─── 全局状态 ───
game_state   = "name_input"   # 新增：先输入名字
player_name  = ""             # 当前玩家名字
best_time    = 0              # 当前玩家本场 session 最佳
game_mode    = "easy"
mouse_color  = "grey"
player_dir   = 0

invincible_time = 0
pause_start     = 0
paused_duration = 0

# 玩家
player_size  = 30
player_x     = WIDTH // 2
player_y     = HEIGHT - 100
player_speed = 7

# 敌人
initial_enemy_size = 50
min_enemy_size     = 20
enemy_size         = initial_enemy_size
enemies            = []
bullets            = []
seconds            = 0
final_time         = 0

# ─── 辅助函数 ─────────────────────────────────────────────
def create_enemy(size):
    x     = random.randint(0, WIDTH - size)
    etype = random.choice(ENEMY_TYPES)
    return [x, 0, etype]

def reset_game():
    global player_x, player_dir, enemy_size
    global enemies, bullets, start_time, final_time
    global invincible_time, game_state, paused_duration

    player_x        = WIDTH // 2
    player_dir      = 0
    enemy_size      = initial_enemy_size

    enemies.clear()
    bullets.clear()
    enemies.append(create_enemy(initial_enemy_size))

    start_time      = pygame.time.get_ticks()
    invincible_time = pygame.time.get_ticks()
    paused_duration = 0
    final_time      = 0
    game_state      = "start"

    pygame.mixer.music.stop()
    pygame.mixer.music.play(-1)

def draw_pvz_text(surface, text, cx, cy, font_size=68):
    fnt = pygame.font.Font(None, font_size)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        dx, dy = int(math.cos(rad) * 4), int(math.sin(rad) * 4)
        s = fnt.render(text, True, (0, 70, 0))
        surface.blit(s, s.get_rect(center=(cx + dx, cy + dy)))
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        dx, dy = int(math.cos(rad) * 2), int(math.sin(rad) * 2)
        s = fnt.render(text, True, (60, 200, 60))
        surface.blit(s, s.get_rect(center=(cx + dx, cy + dy)))
    s = fnt.render(text, True, (255, 235, 0))
    surface.blit(s, s.get_rect(center=(cx, cy)))

def draw_leaderboard(surface, font, cx, top_y):
    """在指定位置绘制排行榜，最多显示8名"""
    board = get_sorted_leaderboard()

    title_font = pygame.font.Font(None, 32)
    title_surf = title_font.render("🏆 Leaderboard", True, (255, 215, 0))
    surface.blit(title_surf, title_surf.get_rect(center=(cx, top_y)))

    if not board:
        no_data = font.render("No records yet", True, (150, 150, 150))
        surface.blit(no_data, no_data.get_rect(center=(cx, top_y + 30)))
        return

    for i, (name, t) in enumerate(board[:8]):
        # 名次颜色：金银铜 + 普通
        if i == 0:
            color = (255, 215, 0)
        elif i == 1:
            color = (192, 192, 192)
        elif i == 2:
            color = (205, 127, 50)
        else:
            color = (200, 200, 200)

        # 高亮当前玩家
        if name == player_name:
            color = (100, 255, 150)

        line = f"{i+1}. {name}  {int(t)}s"
        line_surf = font.render(line, True, color)
        surface.blit(line_surf, line_surf.get_rect(center=(cx, top_y + 30 + i * 28)))

# ─── 初始敌人 ─────────────────────────────────────────────
enemies.append(create_enemy(initial_enemy_size))

clock      = pygame.time.Clock()
running    = True
start_time = pygame.time.get_ticks()

# ═══════════════════════════════════════════════════════════
#  主循环
# ═══════════════════════════════════════════════════════════
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # ── 名字输入界面 ──
            if game_state == "name_input":
                if event.key == pygame.K_RETURN and player_name.strip():
                    # 读取该玩家历史最佳
                    scores = load_scores()
                    best_time = scores.get(player_name.strip(), 0)
                    player_name = player_name.strip()
                    game_state = "start"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    # 限制名字长度 12 个字符
                    if len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode

            # ── 开始界面 ──
            elif game_state == "start":
                if event.key == pygame.K_1:
                    game_mode = "easy"
                elif event.key == pygame.K_2:
                    game_mode = "hard"
                elif event.key == pygame.K_g:
                    mouse_color = "grey"
                elif event.key == pygame.K_b:
                    mouse_color = "brown"
                elif event.key == pygame.K_SPACE:
                    game_state      = "playing"
                    start_time      = pygame.time.get_ticks()
                    invincible_time = pygame.time.get_ticks()
                    paused_duration = 0

            # 任意状态：R 重开
            if game_state not in ("name_input",):
                if event.key == pygame.K_r:
                    reset_game()
                elif game_mode == "hard" and event.key == pygame.K_z:
                    bullets.append([player_x + player_size // 2, player_y])

                if event.key == pygame.K_p:
                    if game_state == "playing":
                        game_state  = "paused"
                        pause_start = pygame.time.get_ticks()
                        pygame.mixer.music.pause()
                    elif game_state == "paused":
                        game_state       = "playing"
                        paused_duration += pygame.time.get_ticks() - pause_start
                        pygame.mixer.music.unpause()

    # ── 游戏逻辑 ──
    if game_state == "playing":

        seconds    = (pygame.time.get_ticks() - start_time - paused_duration) / 1000
        enemy_size = int(max(min_enemy_size, initial_enemy_size - seconds * 1.5))

        if game_mode == "easy":
            enemy_speed = min(5 + seconds * 0.2, 12)
            spawn_rate  = 0.02
        else:
            enemy_speed = min(7 + seconds * 0.3, 18)
            spawn_rate  = 0.05

        if random.random() < spawn_rate:
            enemies.append(create_enemy(enemy_size))

        keys       = pygame.key.get_pressed()
        player_dir = 0
        if keys[pygame.K_LEFT]:
            player_x  -= player_speed
            player_dir = -1
        if keys[pygame.K_RIGHT]:
            player_x  += player_speed
            player_dir = 1
        player_x = max(0, min(WIDTH - player_size, player_x))

        for enemy in enemies:
            enemy[1] += enemy_speed
            if enemy[1] > HEIGHT:
                enemy[1] = 0
                enemy[0] = random.randint(0, WIDTH - enemy_size)

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        if pygame.time.get_ticks() - invincible_time > 1000:
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
                if player_rect.colliderect(enemy_rect) and enemy[2] == "cat":
                    game_state = "game_over"
                    final_time = seconds
                    if seconds > best_time:
                        best_time = seconds
                    # ── 保存成绩到本地文件 ──
                    update_player_score(player_name, seconds)
                    pygame.mixer.music.stop()
                    break

        for bullet in bullets:
            bullet[1] -= 10
        bullets = [b for b in bullets if b[1] > 0]

        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
                if bullet_rect.colliderect(enemy_rect):
                    enemy[1] -= 20

    # ── 渲染 ─────────────────────────────────────────────
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)

    dir_idx    = 1 if player_dir == -1 else (2 if player_dir == 1 else 0)
    player_img = pygame.transform.scale(
        mouse_imgs[mouse_color][dir_idx], (player_size, player_size)
    )

    # ── 名字输入界面 ──
    if game_state == "name_input":
        big_font = pygame.font.Font(None, 56)

        title = big_font.render("Mouse VS Cat", True, (255, 235, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

        prompt = font.render("Enter your name and press ENTER:", True, (200, 200, 200))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

        # 输入框背景
        input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 15, 300, 44)
        pygame.draw.rect(screen, (40, 40, 40), input_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 235, 0), input_rect, 2, border_radius=6)

        # 打字内容 + 光标闪烁
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        input_surf = font.render(player_name + cursor, True, (255, 255, 255))
        screen.blit(input_surf, input_surf.get_rect(center=input_rect.center))

        tip = font.render("Name up to 12 characters", True, (100, 100, 100))
        screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        # 旁边显示排行榜预览
        draw_leaderboard(screen, pygame.font.Font(None, 28), WIDTH // 2, HEIGHT // 2 + 100)

    # ── 开始界面 ──
    elif game_state == "start":
        big_font = pygame.font.Font(None, 60)
        title = big_font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        name_surf = font.render(f"Player: {player_name}", True, (100, 255, 150))
        screen.blit(name_surf, (10, 10))

        mode_surf = font.render(
            f"Mode: {game_mode.upper()}   (1 = Easy  |  2 = Hard)", True, (200, 200, 200)
        )
        screen.blit(mode_surf, (10, 50))

        color_surf = font.render(
            f"Mouse: {mouse_color.upper()}   (G = Grey  |  B = Brown)", True, (200, 200, 200)
        )
        screen.blit(color_surf, (10, 90))

        tip = font.render("Don't be afraid of dogs and cockatiels!", True, (100, 100, 100))
        screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        preview = pygame.transform.scale(mouse_imgs[mouse_color][0], (64, 64))
        screen.blit(preview, preview.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 95)))

        # 个人最佳
        pb_surf = font.render(f"Your Best: {int(best_time)} s", True, (255, 215, 0))
        screen.blit(pb_surf, pb_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 160)))

    # ── 游戏进行中 ──
    elif game_state == "playing":
        time_surf = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_surf, (10, 10))

        name_surf = font.render(player_name, True, (100, 255, 150))
        screen.blit(name_surf, (10, 40))

        if game_mode == "hard":
            hint = font.render("Press Z to pull a piece of rat droppings", True, (200, 200, 200))
            screen.blit(hint, (10, 70))

        screen.blit(player_img, (player_x, player_y))

        for enemy in enemies:
            eimg = pygame.transform.scale(
                enemy_imgs_orig[enemy[2]], (enemy_size, enemy_size)
            )
            screen.blit(eimg, (enemy[0], enemy[1]))

        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 0), (bullet[0], bullet[1], 5, 10))

    # ── 暂停界面 ──
    elif game_state == "paused":
        time_surf = font.render(f"Time: {int(seconds)} s", True, (255, 255, 255))
        screen.blit(time_surf, (10, 10))
        screen.blit(player_img, (player_x, player_y))

        for enemy in enemies:
            eimg = pygame.transform.scale(
                enemy_imgs_orig[enemy[2]], (enemy_size, enemy_size)
            )
            screen.blit(eimg, (enemy[0], enemy[1]))

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        big_font   = pygame.font.Font(None, 74)
        pause_text = big_font.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        tip = font.render("Press P to Resume", True, (200, 200, 200))
        screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    # ── Game Over 界面 ──
    else:
        t    = pygame.time.get_ticks() / 1000
        wave = int(math.sin(t * 3) * 6)

        # PvZ 艺术字（左半区）
        draw_pvz_text(screen, "You're eaten",  220, HEIGHT // 2 - 75 + wave, font_size=62)
        draw_pvz_text(screen, "by the cat!",   220, HEIGHT // 2 - 10 - wave, font_size=62)

        small_font = pygame.font.Font(None, 32)
        for txt, color, y_off in [
            (f"{player_name}'s time: {int(final_time)} s", (255, 255, 255), 55),
            (f"Personal Best: {int(best_time)} s",          (255, 215, 0),   85),
            ("Press R to Restart",                           (200, 200, 200), 125),
        ]:
            s = small_font.render(txt, True, color)
            screen.blit(s, s.get_rect(center=(220, HEIGHT // 2 + y_off)))

        # 分割线
        pygame.draw.line(screen, (80, 80, 80), (430, 20), (430, HEIGHT - 20), 1)

        # 右半区：排行榜
        draw_leaderboard(screen, pygame.font.Font(None, 28), 615, 40)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


