import pygame
import random
import cv2
import mediapipe as mp
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face-Controlled Dodge Game")

# Load assets
ASSET_PATH = r"C:\Users\Linuun\Downloads"

bg_image = pygame.image.load(os.path.join(ASSET_PATH, "background.jpg"))
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

player_img = pygame.image.load(os.path.join(ASSET_PATH, "player.jpg"))
player_img = pygame.transform.scale(player_img, (50, 50))

block_img = pygame.image.load(os.path.join(ASSET_PATH, "asteroid.png"))
block_img = pygame.transform.scale(block_img, (50, 50))

# Player settings
player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size - 20

# Block settings
block_size = 50
block_speed = 7

# Font
font = pygame.font.Font(None, 36)

# Face Detection (MediaPipe)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)

# Open Camera
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

        # Read camera frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            continue
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run face detection every 5 frames
        if frame_count % 5 == 0:
            results = face_detection.process(rgb_frame)

            if results.detections:  # ✅ Fixed
                for detection in results.detections:  # ✅ Fixed
                    bbox = detection.location_data.relative_bounding_box
                    face_x = int(bbox.xmin * frame.shape[1])
                    new_x = int((face_x / frame.shape[1]) * WIDTH)

                    # Smooth movement
                    player_x = int(0.5 * player_x + 0.5 * new_x)

        frame_count += 1

        # Spawn falling blocks
        if random.randint(1, 20) == 1:
            block_x = random.randint(0, WIDTH - block_size)
            block_list.append([block_x, 0])

        # Move blocks
        for block in block_list:
            block[1] += block_speed

        # Collision detection
        for block in block_list:
            if (player_x < block[0] < player_x + player_size or player_x < block[0] + block_size < player_x + player_size) and \
                    (player_y < block[1] + block_size < player_y + player_size):
                print("Collision detected! Game Over.")
                return show_game_over_screen(score)

        # Remove off-screen blocks
        block_list = [block for block in block_list if block[1] < HEIGHT]

        # Draw player
        screen.blit(player_img, (player_x, player_y))

        # Draw blocks
        for block in block_list:
            screen.blit(block_img, (block[0], block[1]))

        # Update score
        score += 1
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Show camera feed
        # Convert OpenCV image to Pygame surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        frame = cv2.transpose(frame)  # Rotate if needed
        frame_surface = pygame.surfarray.make_surface(frame)

        # Resize and display in Pygame
        frame_surface = pygame.transform.scale(frame_surface, (150, 150))  # Resize to fit
        screen.blit(frame_surface, (WIDTH - 160, 10))  # Display in the top-right corner

        # Refresh screen
        pygame.display.flip()
        clock.tick(60)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()

        # Quit if 'q' is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:  # If 'Q' is pressed, quit the game
            pygame.quit()
            cap.release()
            exit()

    print("Game loop ended. Restarting game...")
    return True  # Ensure game restarts


# Function to show game over screen
def show_game_over_screen(score):
    while True:
        screen.blit(bg_image, (0, 0))
        game_over_text = font.render("Game Over!", True, (200, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, (0, 0, 0))
        replay_text = font.render("Press SPACE to Play Again", True, (0, 0, 0))
        quit_text = font.render("Press Q to Quit", True, (0, 0, 0))

        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - 80, HEIGHT // 3 + 40))
        screen.blit(replay_text, (WIDTH // 2 - 140, HEIGHT // 3 + 80))
        screen.blit(quit_text, (WIDTH // 2 - 80, HEIGHT // 3 + 120))

        pygame.display.flip()

        # Wait for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Restarting game...")
                    return True  # Restart game
                elif event.key == pygame.K_q:
                    print("Quitting game...")
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()


# Main game loop
while True:
    if not run_game():  # Run the game and check if it should restart
        break  # Exit loop if run_game() does not return True
