# Face-Controlled Dodge Game
import pygame
import random
import cv2
import mediapipe as mp
import os

pygame.init()

WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face-Controlled Dodge Game")

ASSET_PATH = r"C:\Users\Linuun\Downloads"

bg_image = pygame.image.load(os.path.join(ASSET_PATH, "background.jpg"))
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

player_img = pygame.image.load(os.path.join(ASSET_PATH, "player.jpg"))
player_img = pygame.transform.scale(player_img, (50, 50))

block_img = pygame.image.load(os.path.join(ASSET_PATH, "asteroid.png"))
block_img = pygame.transform.scale(block_img, (50, 50))

player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size - 20

block_size = 50
block_speed = 7

font = pygame.font.Font(None, 36)

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=1)

cap = cv2.VideoCapture(0)

def run_game():
    global player_x
    block_list = []
    score = 0
    clock = pygame.time.Clock()
    frame_count = 0

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        ret,frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if frame_count % 5 == 0:
            results = face_detection.process(rgb_frame)

            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    face_x = int(bbox.xmin * frame.shape[1])
                    new_x = int((face_x / frame.shape[1]) * WIDTH)

                    player_x = int(0.5 * player_x + 0.5 * new_x)

        frame_count += 1

        if random.randint(1, 20) == 1:
            block_x = random.randint(0, WIDTH - block_size)
            block_list.append([block_x, 0])

        for block in block_list:
            block[1] += block_speed

        for block in block_list:
            if (player_x < block[0] < player_x + player_size or player_x < block[0] + block_size < player_x + player_size) and \
                (player_y < block[1] + block_size < player_y + player_size):
                    print("Collision detected! Game Over.")
                    return show_game_over_screen(score)

        block_list = [block for block in block_list if block[1] < HEIGHT]

        screen.blit(player_img, (player_x, player_y))

        for block in block_list:
            screen.blit(block_img, (block[0], block[1]))

        score += 1
        score_text = font.render(f"Score: {score}", True, (255, 0, 0))
        screen.blit(score_text, (10, 10))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        frame_surface = pygame.surfarray.make_surface(frame)

        frame_surface = pygame.transform.scale(frame_surface, (150, 150))
        screen.blit(frame_surface, (WIDTH - 160, 10))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            pygame.quit()
            cap.release()
            exit()

    print("Game loop ended. Restarting game...")
    return True

def show_game_over_screen(score):
    while True:
        screen.blit(bg_image, (0,0))
        game_over_text = font.render("Game Over!", True, (200, 0 , 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        replay_text = font.render("Press SPACE to Play Again", True, (255, 255, 255))
        quit_text = font.render("Press Q to Quit", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - 80, HEIGHT // 3 + 40))
        screen.blit(replay_text, (WIDTH // 2 - 140, HEIGHT // 3 + 80))
        screen.blit(quit_text, (WIDTH // 2 - 80, HEIGHT // 3 + 120))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Restarting game...")
                    return True
                elif event.key == pygame.K_q:
                    print("Quitting game...")
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

while True:
    if not run_game():
        break