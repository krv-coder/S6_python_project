import pygame
import random
import sys
import math
import os
import cv2

# --- Initialization ---
pygame.init()
pygame.mixer.init()

# Attempt Fullscreen with fallback
try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except:
    screen = pygame.display.set_mode((1280, 720))

WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Ultimate RPS - Cinema Edition")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD  = (255, 215, 0)
GRAY  = (50, 50, 50)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)

# --- Fonts ---
font_main = pygame.font.SysFont("Verdana", 80, bold=True)
font_sub = pygame.font.SysFont("Verdana", 35)
font_msg = pygame.font.SysFont("Verdana", 45, italic=True)

class Game:
    def __init__(self):
        self.user_score = 0
        self.comp_score = 0
        self.win_limit = 3 
        self.state = "MENU"
        self.choices = ["Rock", "Paper", "Scissors"]
        self.frame = 0 
        self.message = "Choose your weapon!"
        
        # UI Rects
        self.start_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 60)
        self.limit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
        self.how_rect   = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60)
        self.exit_rect  = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 60)
        self.back_rect  = pygame.Rect(WIDTH//2 - 150, HEIGHT - 100, 300, 60)

        self.images = {}
        self.sounds = {}
        self.bg = None
        self.load_assets()
        
        if os.path.exists("bk.mp3"):
            pygame.mixer.music.load("bk.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    def load_assets(self):
        """Loads high-quality assets with fallbacks."""
        try:
            if os.path.exists("bck.jpg"):
                img = pygame.image.load("bck.jpg").convert()
                self.bg = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

            for choice in self.choices:
                # Check for standard names or 'scissor.png'
                name = f"{choice.lower()}.png"
                if choice == "Scissors" and not os.path.exists(name): 
                    name = "scissor.png"
                
                if os.path.exists(name):
                    img = pygame.image.load(name).convert_alpha()
                    self.images[choice] = pygame.transform.smoothscale(img, (180, 180))

            sfx = ["stone_hit", "paper_cut", "paper_fold", "lose", "win"]
            for s in sfx:
                if os.path.exists(f"{s}.mp3"):
                    self.sounds[s] = pygame.mixer.Sound(f"{s}.mp3")
        except Exception as e:
            print(f"Asset Error: {e}")

    def play_video_intro(self):
        """Optimized High-Resolution Video Player."""
        video_path = "intro_video.mp4"
        audio_path = "intro_sound.mp3"

        if not os.path.exists(video_path): return

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        target_size = (WIDTH, HEIGHT)
        
        pygame.mixer.music.pause()
        if os.path.exists(audio_path):
            pygame.mixer.Sound(audio_path).play()

        clock = pygame.time.Clock()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            for event in pygame.event.get():
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    cap.release()
                    pygame.mixer.stop()
                    pygame.mixer.music.unpause()
                    return

            # Fast Processing for High Resolution
            frame = cv2.resize(frame, target_size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.swapaxes(0, 1)
            frame_surface = pygame.surfarray.make_surface(frame)
            
            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()
            clock.tick(fps)

        cap.release()
        pygame.mixer.music.unpause()

    def draw_screen_base(self):
        if self.bg: screen.blit(self.bg, (0, 0))
        else: screen.fill(BLACK)

    def draw_button(self, rect, text):
        m_pos = pygame.mouse.get_pos()
        active = rect.collidepoint(m_pos)
        clr = GOLD if active else WHITE
        pygame.draw.rect(screen, GRAY, rect, border_radius=10)
        pygame.draw.rect(screen, clr, rect, 3, border_radius=10)
        txt = font_sub.render(text, True, clr)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def play_round(self, user_choice):
        comp_choice = random.choice(self.choices)
        if user_choice == comp_choice:
            self.message = f"Tie! Both chose {user_choice}"
        elif (user_choice == "Rock" and comp_choice == "Scissors"):
            self.message = "Your Stone smashed the Scissor!"
            if "stone_hit" in self.sounds: self.sounds["stone_hit"].play()
            self.user_score += 1
        elif (user_choice == "Scissors" and comp_choice == "Paper"):
            self.message = "Your Scissor cut the Paper!"
            if "paper_cut" in self.sounds: self.sounds["paper_cut"].play()
            self.user_score += 1
        elif (user_choice == "Paper" and comp_choice == "Rock"):
            self.message = "Your Paper wrapped the Stone!"
            if "paper_fold" in self.sounds: self.sounds["paper_fold"].play()
            self.user_score += 1
        else:
            self.comp_score += 1
            if comp_choice == "Rock":
                self.message = "Enemy's Stone smashed you!"
                if "stone_hit" in self.sounds: self.sounds["stone_hit"].play()
            elif comp_choice == "Scissors":
                self.message = "Enemy's Scissor cut you!"
                if "paper_cut" in self.sounds: self.sounds["paper_cut"].play()
            else:
                self.message = "Enemy's Paper wrapped you!"
                if "paper_fold" in self.sounds: self.sounds["paper_fold"].play()

        if self.user_score >= self.win_limit:
            if "win" in self.sounds: self.sounds["win"].play()
            self.state = "GAMEOVER"
        elif self.comp_score >= self.win_limit:
            if "lose" in self.sounds: self.sounds["lose"].play()
            self.state = "GAMEOVER"

    def menu(self):
        self.draw_screen_base()
        title = font_main.render("ULTIMATE RPS", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))
        
        self.draw_button(self.start_rect, "START GAME")
        self.draw_button(self.limit_rect, f"GOAL: {self.win_limit} PTS")
        self.draw_button(self.how_rect, "HOW TO PLAY")
        self.draw_button(self.exit_rect, "EXIT")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_rect.collidepoint(event.pos):
                    self.play_video_intro()
                    pygame.mixer.music.set_volume(0.2)
                    self.state = "PLAYING"
                if self.limit_rect.collidepoint(event.pos):
                    self.win_limit = 5 if self.win_limit == 3 else 10 if self.win_limit == 5 else 3
                if self.how_rect.collidepoint(event.pos): self.state = "HOW"
                if self.exit_rect.collidepoint(event.pos): pygame.quit(); sys.exit()

    def game_loop(self):
        self.draw_screen_base()
        self.frame += 1
        
        score_txt = font_sub.render(f"PLAYER: {self.user_score} | CPU: {self.comp_score}", True, GOLD)
        screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 30))
        
        msg_img = font_msg.render(self.message, True, BLACK)
        screen.blit(msg_img, (WIDTH//2 - msg_img.get_width()//2, 120))

        choices_rects = []
        for i, choice in enumerate(self.choices):
            x_pos = (WIDTH // 4) * (i + 1)
            y_pos = HEIGHT // 2 + (math.sin(self.frame * 0.05 + i) * 15)
            rect = pygame.Rect(x_pos - 90, y_pos - 90, 180, 180)
            choices_rects.append((rect, choice))
            
            if self.images.get(choice): 
                screen.blit(self.images[choice], rect.topleft)
            
            lbl = font_sub.render(choice, True, BLACK)
            screen.blit(lbl, (x_pos - lbl.get_width()//2, y_pos + 100))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r, c in choices_rects:
                    if r.collidepoint(event.pos): self.play_round(c)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.set_volume(0.5); self.state = "MENU"

    def how_to_play(self):
        self.draw_screen_base()
        instr = ["HOW TO PLAY", "- Use MOUSE to click icons", "- Rock will smash the scissor", 
                 "- Scissor can cut the paper", "- Paper will wrap the rock", "Click BACK to Menu"]
        for i, line in enumerate(instr):
            txt = font_sub.render(line, True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200 + i*50))
        
        self.draw_button(self.back_rect, "BACK")
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.back_rect.collidepoint(event.pos):
                self.state = "MENU"

    def game_over(self):
        self.draw_screen_base()
        msg = "VICTORY!" if self.user_score > self.comp_score else "DEFEAT!"
        txt = font_main.render(msg, True, BLACK if "VIC" in msg else BLACK)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//3))
        
        btn = pygame.Rect(WIDTH//2-150, HEIGHT//2 + 50, 300, 60)
        self.draw_button(btn, "MAIN MENU")
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(event.pos):
                pygame.mixer.music.set_volume(0.5)
                self.__init__()

# --- Main Logic ---
game = Game()
clock = pygame.time.Clock()
while True:
    if game.state == "MENU": game.menu()
    elif game.state == "HOW": game.how_to_play()
    elif game.state == "PLAYING": game.game_loop()
    elif game.state == "GAMEOVER": game.game_over()
    pygame.display.flip()
    clock.tick(60)
