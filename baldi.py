import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import math
import sys
import numpy as np
from PIL import Image  # Добавляем для загрузки текстуры

# Инициализация Pygame и OpenGL
pygame.init()
glutInit(sys.argv)  # Правильная инициализация GLUT с аргументами
display = (1024, 768)
pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
pygame.display.set_caption("Mathias POV!!!")

# Настройка OpenGL
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)  # Включаем освещение
glEnable(GL_LIGHT0)    # Включаем первый источник света
glEnable(GL_COLOR_MATERIAL)  # Включаем поддержку цветов материалов
glEnable(GL_CULL_FACE)  # Включаем отсечение невидимых граней
glCullFace(GL_BACK)     # Отсекаем задние грани

# Настраиваем свет
glLight(GL_LIGHT0, GL_POSITION, (0, 5, 0, 1))  # Положение света сверху
glLight(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1))  # Фоновое освещение
glLight(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))    # Рассеянное освещение

# Настройка камеры
gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)  # Увеличено до 1000.0
glTranslatef(0.0, -0.5, -5.0)  # Начальное положение камеры

glClearColor(0.5, 0.7, 1.0, 1)  # Светло-голубой фон

# Настраиваем буфер глубины для лучшей видимости
glClearDepth(1.0)
glDepthFunc(GL_LESS)

# Класс игрока
class Player:
    def __init__(self):
        self.pos = [0.0, 1.0, 0.0]
        self.rot = [0, 0]
        self.speed = 0.1
        self.mouse_sensitivity = 0.3
        self.jump_force = 0.15
        self.jump_speed = 0
        self.is_jumping = False
        self.gravity = 0.01
        self.collision_radius = 0.3  # Уменьшаем размер коллизии игрока
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[K_w]:
            self.pos[0] += math.sin(self.rot[1]) * self.speed
            self.pos[2] += math.cos(self.rot[1]) * self.speed
        if keys[K_s]:
            self.pos[0] -= math.sin(self.rot[1]) * self.speed
            self.pos[2] -= math.cos(self.rot[1]) * self.speed
        if keys[K_a]:
            self.rot[0] -= 0.03
        if keys[K_d]:
            self.rot[0] += 0.03
        
        # Ограничение движения в пределах школы
        self.pos[0] = max(-15, min(15, self.pos[0]))
        self.pos[2] = max(-15, min(15, self.pos[2]))

# Класс Балди
class Baldi:
    def __init__(self):
        self.pos = [0.0, 0.0, 0.0]
        self.rotation = 0
        self.speed = 0.03  # Уменьшена базовая скорость
        self.target = None
        self.state = 'idle'
        self.detection_range = 8.0  # Уменьшен радиус обнаружения
        self.anger = 0
        self.max_anger_speed = 0.02  # Ограничение дополнительной скорости от злости

class Door:
    def __init__(self, pos, rotation):
        self.pos = pos
        self.rotation = rotation
        self.angle = 0
        self.target_angle = 0
        self.opening_speed = 3.0
        self.color = (0.6, 0.3, 0.1)  # Коричневый цвет двери

def load_texture(path):
    image = Image.open(path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.convert("RGBA").tobytes()
    width = image.width
    height = image.height
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Улучшенные параметры текстуры для прозрачности
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    return texture_id

def draw_school():
    glBegin(GL_QUADS)
    # Пол
    glColor3f(0.8, 0.8, 0.8)
    glVertex3f(-15, -1, -15)
    glVertex3f(-15, -1, 15)
    glVertex3f(15, -1, 15)
    glVertex3f(15, -1, -15)
    
    # Стены
    glColor3f(0.7, 0.7, 1.0)
    # Передняя стена
    glVertex3f(-15, -1, -15)
    glVertex3f(-15, 5, -15)
    glVertex3f(15, 5, -15)
    glVertex3f(15, -1, -15)
    # Задняя стена
    glVertex3f(-15, -1, 15)
    glVertex3f(-15, 5, 15)
    glVertex3f(15, 5, 15)
    glVertex3f(15, -1, 15)
    # Левая стена
    glVertex3f(-15, -1, -15)
    glVertex3f(-15, 5, -15)
    glVertex3f(-15, 5, 15)
    glVertex3f(-15, -1, 15)
    # Правая стена
    glVertex3f(15, -1, -15)
    glVertex3f(15, 5, -15)
    glVertex3f(15, 5, 15)
    glVertex3f(15, -1, 15)
    glEnd()

def draw_baldi(baldi):
    glPushMatrix()
    glTranslatef(baldi.pos[0], baldi.pos[1], baldi.pos[2])
    glRotatef(baldi.rotation, 0, 1, 0)
    
    # Голова (овал)
    glColor3f(1.0, 0.8, 0.6)  # Телесный цвет
    glBegin(GL_POLYGON)
    for i in range(32):
        angle = 2 * math.pi * i / 32
        glVertex3f(0.3 * math.cos(angle), 1.7 + 0.4 * math.sin(angle), 0)
    glEnd()
    
    # Тело (прямоугольник)
    glColor3f(0.0, 0.7, 0.0)  # Зеленый свитер
    glBegin(GL_QUADS)
    glVertex3f(-0.25, 1.0, 0)
    glVertex3f(0.25, 1.0, 0)
    glVertex3f(0.25, 1.6, 0)
    glVertex3f(-0.25, 1.6, 0)
    glEnd()
    
    # Брюки
    glColor3f(0.0, 0.0, 0.4)  # Синие брюки
    glBegin(GL_QUADS)
    glVertex3f(-0.25, 0.0, 0)
    glVertex3f(0.25, 0.0, 0)
    glVertex3f(0.25, 1.0, 0)
    glVertex3f(-0.25, 1.0, 0)
    glEnd()
    
    # Глаза
    glColor3f(0.0, 0.0, 0.0)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex3f(-0.1, 1.8, 0.1)
    glVertex3f(0.1, 1.8, 0.1)
    glEnd()
    
    # Улыбка
    glBegin(GL_LINE_STRIP)
    for i in range(32):
        angle = math.pi * i / 32
        glVertex3f(0.15 * math.cos(angle) - 0.0, 1.65 + 0.05 * math.sin(angle), 0.1)
    glEnd()
    
    # Линейка в руке
    glColor3f(0.8, 0.6, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(0.25, 1.3, 0)
    glVertex3f(0.8, 1.3, 0)
    glVertex3f(0.8, 1.4, 0)
    glVertex3f(0.25, 1.4, 0)
    glEnd()
    
    glPopMatrix()

def draw_room():
    # Пол (белый)
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-6, 0, -6)
    glVertex3f(6, 0, -6)
    glVertex3f(6, 0, 6)
    glVertex3f(-6, 0, 6)
    glEnd()

    # Стены с дверным проемом
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    
    # Передняя стена с дверным проемом
    # Левая часть от двери
    glVertex3f(-6, 0, -6)
    glVertex3f(-0.5, 0, -6)  # Сужен проем до размера двери
    glVertex3f(-0.5, 3, -6)
    glVertex3f(-6, 3, -6)
    
    # Правая часть от двери
    glVertex3f(0.5, 0, -6)   # Сужен проем до размера двери
    glVertex3f(6, 0, -6)
    glVertex3f(6, 3, -6)
    glVertex3f(0.5, 3, -6)
    
    # Верхняя часть над дверью
    glVertex3f(-0.5, 2.2, -6)  # Высота двери
    glVertex3f(0.5, 2.2, -6)
    glVertex3f(0.5, 3, -6)
    glVertex3f(-0.5, 3, -6)
    
    # Задняя стена
    glVertex3f(-6, 0, 6)
    glVertex3f(6, 0, 6)
    glVertex3f(6, 3, 6)
    glVertex3f(-6, 3, 6)
    
    # Левая стена
    glVertex3f(-6, 0, -6)
    glVertex3f(-6, 0, 6)
    glVertex3f(-6, 3, 6)
    glVertex3f(-6, 3, -6)
    
    # Правая стена
    glVertex3f(6, 0, -6)
    glVertex3f(6, 0, 6)
    glVertex3f(6, 3, 6)
    glVertex3f(6, 3, -6)
    glEnd()

    # Потолок (зеленый)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.8, 0.0)
    glVertex3f(-6, 3, -6)
    glVertex3f(6, 3, -6)
    glVertex3f(6, 3, 6)
    glVertex3f(-6, 3, 6)
    glEnd()

    # Сетка на полу
    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.0)  # Черные линии сетки
    # Вертикальные линии
    for x in range(-6, 7):
        glVertex3f(x, 0, -6)
        glVertex3f(x, 0, 6)
    # Горизонтальные линии
    for z in range(-6, 7):
        glVertex3f(-6, 0, z)
        glVertex3f(6, 0, z)
    glEnd()

    # Сетка на стенах
    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.0)  # Черные линии сетки
    
    # Сетка на передней стене
    for x in range(-6, 7):
        glVertex3f(x, 0, -6)
        glVertex3f(x, 3, -6)
    for y in range(0, 4):
        glVertex3f(-6, y, -6)
        glVertex3f(6, y, -6)

    # Сетка на задней стене
    for x in range(-6, 7):
        glVertex3f(x, 0, 6)
        glVertex3f(x, 3, 6)
    for y in range(0, 4):
        glVertex3f(-6, y, 6)
        glVertex3f(6, y, 6)

    # Сетка на левой стене
    for z in range(-6, 7):
        glVertex3f(-6, 0, z)
        glVertex3f(-6, 3, z)
    for y in range(0, 4):
        glVertex3f(-6, y, -6)
        glVertex3f(-6, y, 6)

    # Сетка на правой стене
    for z in range(-6, 7):
        glVertex3f(6, 0, z)
        glVertex3f(6, 3, z)
    for y in range(0, 4):
        glVertex3f(6, y, -6)
        glVertex3f(6, y, 6)
    glEnd()

    # Сетка на потолке
    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.0)  # Черные линии сетки
    # Вертикальные линии
    for x in range(-6, 7):
        glVertex3f(x, 3, -6)
        glVertex3f(x, 3, 6)
    # Горизонтальные линии
    for z in range(-6, 7):
        glVertex3f(-6, 3, z)
        glVertex3f(6, 3, z)
    glEnd()

def draw_grid_texture(size=1.0, width=20):
    glLineWidth(1.0)
    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.0)  # Черные линии сетки
    
    # Вертикальные линии
    for i in range(-width, width + 1):
        glVertex3f(i * size, 0, 0)
        glVertex3f(i * size, 3, 0)
    
    # Горизонтальные линии
    for i in range(4):  # 3 метра высоты
        glVertex3f(-width, i * size, 0)
        glVertex3f(width, i * size, 0)
    glEnd()

def draw_connecting_corridor():
    # Коридор
    glBegin(GL_QUADS)
    # Пол коридора (белый)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-2.5, 0, -6)
    glVertex3f(-2.5, 0, -14)
    glVertex3f(2.5, 0, -14)
    glVertex3f(2.5, 0, -6)
    glEnd()
    
    # Сетка на полу коридора
    glPushMatrix()
    glTranslatef(0, 0, -10)
    glRotatef(90, 1, 0, 0)
    draw_grid_texture(1.0, 3)
    glPopMatrix()
    
    # Потолок коридора (зеленый)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.8, 0.0)
    glVertex3f(-2.5, 3, -6)
    glVertex3f(-2.5, 3, -14)
    glVertex3f(2.5, 3, -14)
    glVertex3f(2.5, 3, -6)
    glEnd()
    
    # Сетка на потолке коридора
    glPushMatrix()
    glTranslatef(0, 3, -10)
    glRotatef(90, 1, 0, 0)
    draw_grid_texture(1.0, 3)
    glPopMatrix()
    
    # Стены коридора
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 0.0)
    
    # Левая стена
    glVertex3f(-2.5, 0, -6)
    glVertex3f(-2.5, 0, -14)
    glVertex3f(-2.5, 3, -14)
    glVertex3f(-2.5, 3, -6)
    
    # Правая стена
    glVertex3f(2.5, 0, -6)
    glVertex3f(2.5, 0, -14)
    glVertex3f(2.5, 3, -14)
    glVertex3f(2.5, 3, -6)
    
    # Стена с дверным проемом
    glVertex3f(-2.5, 0, -14)
    glVertex3f(-0.5, 0, -14)
    glVertex3f(-0.5, 3, -14)
    glVertex3f(-2.5, 3, -14)
    
    glVertex3f(0.5, 0, -14)
    glVertex3f(2.5, 0, -14)
    glVertex3f(2.5, 3, -14)
    glVertex3f(0.5, 3, -14)
    
    glVertex3f(-0.5, 2.2, -14)
    glVertex3f(0.5, 2.2, -14)
    glVertex3f(0.5, 3, -14)
    glVertex3f(-0.5, 3, -14)
    glEnd()
    
    # Сетка на стенах коридора
    glPushMatrix()
    glTranslatef(-2.5, 0, -10)
    glRotatef(90, 0, 1, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(2.5, 0, -10)
    glRotatef(-90, 0, 1, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, -14)
    draw_grid_texture(1.0, 3)
    glPopMatrix()

def draw_end_room():
    # Комната 8x8
    glBegin(GL_QUADS)
    # Пол (белый)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-4, 0, -14)
    glVertex3f(4, 0, -14)
    glVertex3f(4, 0, -22)
    glVertex3f(-4, 0, -22)
    glEnd()
    
    # Сетка на полу
    glPushMatrix()
    glTranslatef(0, 0, -18)
    glRotatef(90, 1, 0, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    # Потолок (зеленый)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.8, 0.0)
    glVertex3f(-4, 3, -14)
    glVertex3f(4, 3, -14)
    glVertex3f(4, 3, -22)
    glVertex3f(-4, 3, -22)
    glEnd()
    
    # Сетка на потолке
    glPushMatrix()
    glTranslatef(0, 3, -18)
    glRotatef(90, 1, 0, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    # Стены (желтые)
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 0.0)
    # Задняя стена
    glVertex3f(-4, 0, -22)
    glVertex3f(4, 0, -22)
    glVertex3f(4, 3, -22)
    glVertex3f(-4, 3, -22)
    
    # Левая стена
    glVertex3f(-4, 0, -14)
    glVertex3f(-4, 0, -22)
    glVertex3f(-4, 3, -22)
    glVertex3f(-4, 3, -14)
    
    # Правая стена
    glVertex3f(4, 0, -14)
    glVertex3f(4, 0, -22)
    glVertex3f(4, 3, -22)
    glVertex3f(4, 3, -14)
    glEnd()
    
    # Сетка на стенах
    glPushMatrix()
    glTranslatef(0, 0, -22)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-4, 0, -18)
    glRotatef(90, 0, 1, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(4, 0, -18)
    glRotatef(-90, 0, 1, 0)
    draw_grid_texture(1.0, 4)
    glPopMatrix()

def draw_door(door):
    glPushMatrix()
    glTranslatef(door.pos[0], door.pos[1], door.pos[2])
    glRotatef(door.rotation, 0, 1, 0)
    
    # Рисуем дверь с точкой вращения у правого края
    glPushMatrix()
    glTranslatef(0, 0, 0)  # Точка вращения у правого края
    glRotatef(door.angle, 0, 1, 0)
    glTranslatef(-1.0, 0, 0)  # Сдвигаем дверь влево, чтобы правый край был в точке вращения
    
    # Основная часть двери
    glColor3f(*door.color)
    glBegin(GL_QUADS)
    # Дверное полотно
    glVertex3f(0, 0, 0)
    glVertex3f(1.0, 0, 0)
    glVertex3f(1.0, 2.2, 0)
    glVertex3f(0, 2.2, 0)
    
    # Рамка двери (более темный оттенок)
    dark_color = tuple(c * 0.7 for c in door.color)
    glColor3f(*dark_color)
    # Верхняя рамка
    glVertex3f(0, 2.0, 0.02)
    glVertex3f(1.0, 2.0, 0.02)
    glVertex3f(1.0, 2.2, 0.02)
    glVertex3f(0, 2.2, 0.02)
    # Нижняя рамка
    glVertex3f(0, 0, 0.02)
    glVertex3f(1.0, 0, 0.02)
    glVertex3f(1.0, 0.2, 0.02)
    glVertex3f(0, 0.2, 0.02)
    # Левая рамка
    glVertex3f(0, 0, 0.02)
    glVertex3f(0.2, 0, 0.02)
    glVertex3f(0.2, 2.2, 0.02)
    glVertex3f(0, 2.2, 0.02)
    # Правая рамка
    glVertex3f(0.8, 0, 0.02)
    glVertex3f(1.0, 0, 0.02)
    glVertex3f(1.0, 2.2, 0.02)
    glVertex3f(0.8, 2.2, 0.02)
    glEnd()
    
    # Дверная ручка
    glColor3f(0.7, 0.7, 0.7)  # Металлический цвет
    glPushMatrix()
    glTranslatef(0.8, 1.1, 0.05)
    # Основание ручки
    glBegin(GL_QUADS)
    glVertex3f(-0.1, -0.02, 0)
    glVertex3f(0.1, -0.02, 0)
    glVertex3f(0.1, 0.02, 0)
    glVertex3f(-0.1, 0.02, 0)
    glEnd()
    # Ручка (цилиндр)
    glColor3f(0.8, 0.8, 0.8)
    glTranslatef(0.1, 0, 0)
    glBegin(GL_LINES)
    for i in range(8):
        angle = i * math.pi / 4
        glVertex3f(0, 0, 0)
        glVertex3f(0.1 * math.cos(angle), 0.1 * math.sin(angle), 0)
    glEnd()
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_crosshair():
    # Сохраняем текущую матрицу
    glPushMatrix()
    
    # Сбрасываем все трансформации
    glLoadIdentity()
    
    # Переключаемся в режим ортографической проекции для рисования 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Рисуем маленькую черную точку в центре экрана
    glPointSize(4.0)  # Размер точки
    glColor3f(0.0, 0.0, 0.0)  # Черный цвет
    glBegin(GL_POINTS)
    glVertex2f(0.0, 0.0)  # Центр экрана
    glEnd()
    
    # Восстанавливаем проекцию
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Восстанавливаем предыдущую матрицу
    glPopMatrix()

def update_doors(doors, player_pos):
    for door in doors:
        # Проверяем расстояние до двери
        dx = player_pos[0] - door.pos[0]
        dz = player_pos[2] - door.pos[2]
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Если игрок рядом - открываем дверь
        if distance < 2.5:
            door.target_angle = -90  # Изменено направление открытия на противоположное
        else:
            door.target_angle = 0
        
        # Плавная анимация
        if door.angle > door.target_angle:
            door.angle = max(door.angle - door.opening_speed, door.target_angle)
        elif door.angle < door.target_angle:
            door.angle = min(door.angle + door.opening_speed, door.target_angle)

def update_baldi(baldi, player):
    dx = player.pos[0] - baldi.pos[0]
    dz = player.pos[2] - baldi.pos[2]
    distance = math.sqrt(dx*dx + dz*dz)
    
    if distance < baldi.detection_range:
        baldi.state = 'chase'
        baldi.anger = min(baldi.anger + 0.0005, 0.05)  # Медленнее накапливается злость
    else:
        baldi.state = 'idle'
        baldi.anger = max(baldi.anger - 0.001, 0)
    
    if baldi.state == 'chase':
        angle = math.atan2(dx, dz)
        baldi.rotation = math.degrees(angle)
        
        # Ограничиваем максимальную скорость
        speed = min(baldi.speed + baldi.anger, baldi.speed + baldi.max_anger_speed)
        baldi.pos[0] += speed * math.sin(angle)
        baldi.pos[2] += speed * math.cos(angle)
    
    # Проверка коллизий со стенами для Балди
    if abs(baldi.pos[0]) > 5.7:
        baldi.pos[0] = 5.7 if baldi.pos[0] > 0 else -5.7
    if baldi.pos[2] > 5.7:
        baldi.pos[2] = 5.7
    if baldi.pos[2] < -21.7:
        baldi.pos[2] = -21.7

def main():
    pygame.init()
    display = (1024, 768)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    # Настройки для прозрачности
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Загружаем текстуру для Балди
    baldi = Baldi()
    baldi.texture_id = load_texture("./adrian.png")
    
    # Максимальные настройки видимости
    glEnable(GL_DEPTH_TEST)
    glClearDepth(1.0)
    glDepthFunc(GL_LEQUAL)  # Изменено для лучшей видимости дальних объектов
    
    # Настройка перспективы для максимальной видимости
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(100.0, (display[0]/display[1]), 0.01, 5000.0)  # Сильно увеличены параметры
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, -0.5, -5.0)
    
    # Отключаем все, что может мешать видимости
    glDisable(GL_FOG)
    glDisable(GL_CULL_FACE)
    
    # Настройка освещения для лучшей видимости
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    player = Player()
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    clock = pygame.time.Clock()
    
    # Создаем двери
    doors = [
        Door([0.5, 0, -6], 0),      # Первая дверь
        Door([0.5, 0, -14], 0),     # Вторая дверь
    ]
    
    # Создаем Балди
    baldi.pos = [-3.0, 0.0, -18.0]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Выход по Esc
                    pygame.quit()
                    return
                elif event.key == pygame.K_SPACE and not player.is_jumping:
                    player.is_jumping = True
                    player.jump_speed = player.jump_force
            elif event.type == pygame.MOUSEMOTION:
                player.rot[0] += event.rel[1] * player.mouse_sensitivity
                player.rot[1] += event.rel[0] * player.mouse_sensitivity
                player.rot[0] = max(min(player.rot[0], 89), -89)

        # Обработка прыжка и гравитации
        if player.is_jumping:
            player.pos[1] += player.jump_speed
            player.jump_speed -= player.gravity
            
            # Проверка приземления
            if player.pos[1] <= 1.0:
                player.pos[1] = 1.0
                player.is_jumping = False
                player.jump_speed = 0

        # Движение игрока с проверкой коллизий
        keys = pygame.key.get_pressed()
        x_move = z_move = 0
        
        if keys[pygame.K_w]:
            x_move += math.sin(math.radians(player.rot[1])) * player.speed
            z_move -= math.cos(math.radians(player.rot[1])) * player.speed
        if keys[pygame.K_s]:
            x_move -= math.sin(math.radians(player.rot[1])) * player.speed
            z_move += math.cos(math.radians(player.rot[1])) * player.speed
        if keys[pygame.K_a]:
            x_move -= math.cos(math.radians(player.rot[1])) * player.speed
            z_move -= math.sin(math.radians(player.rot[1])) * player.speed
        if keys[pygame.K_d]:
            x_move += math.cos(math.radians(player.rot[1])) * player.speed
            z_move += math.sin(math.radians(player.rot[1])) * player.speed

        # Обновленная система коллизий
        new_x = player.pos[0] + x_move
        new_z = player.pos[2] + z_move
        
        can_move_x = True
        can_move_z = True
        
        # Проверка стен с дверными проемами
        if abs(new_z + 6) < 0.2:  # Первая дверь
            if not (-0.5 < new_x < 0.5):  # Вне дверного проема
                can_move_z = False
        
        if abs(new_z + 14) < 0.2:  # Вторая дверь
            if not (-0.5 < new_x < 0.5):  # Вне дверного проема
                can_move_z = False
        
        # Проверка остальных стен
        if abs(new_x) > 5.7:  # Боковые стены первой комнаты
            can_move_x = False
        
        if new_z > 5.7:  # Задняя стена первой комнаты
            can_move_z = False
        
        # Проверка коридора
        if -14 < new_z < -6:
            if abs(new_x) > 2.0:
                can_move_x = False
        
        # Проверка конечной комнаты
        if new_z < -14:
            if abs(new_x) > 3.5:
                can_move_x = False
            if new_z < -22:
                can_move_z = False
        
        # Применяем движение
        if can_move_x:
            player.pos[0] = new_x
        if can_move_z:
            player.pos[2] = new_z
        
        # Обновляем Балди
        update_baldi(baldi, player)

        # Обновление состояния дверей
        update_doors(doors, player.pos)
        
        # Проверяем столкновение с Балди
        dx = player.pos[0] - baldi.pos[0]
        dz = player.pos[2] - baldi.pos[2]
        if math.sqrt(dx*dx + dz*dz) < 0.5:  # Если игрок слишком близко
            print("Game Over!")
            running = False
            break
        
        # Очистка с максимальной глубиной
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Обновление вида
        glLoadIdentity()
        glRotatef(player.rot[0], 1, 0, 0)
        glRotatef(player.rot[1], 0, 1, 0)
        glTranslatef(-player.pos[0], -player.pos[1], -player.pos[2])
        
        # Отрисовка
        draw_room()  # Основная комната
        draw_connecting_corridor()  # Соединительный коридор
        draw_end_room()  # Конечная комната
        
        # Отрисовка дверей
        for door in doors:
            draw_door(door)
        
        draw_crosshair()
        
        # Отрисовываем Балди
        draw_baldi(baldi)
        
        pygame.display.flip()
        clock.tick(60)

main()
