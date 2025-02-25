import pygame
import random
import cv2
import mediapipe as mp
import os

from pyrect import WIDTH, HEIGHT

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
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

