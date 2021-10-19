# Universidad del Valle de Guatemala
# Graficas por computadora - CC3044
# Julio Herrera - 19402
# Raycaster

import pygame
import math

from pygame import color
from pygame import draw

wallColors = {
  '1': pygame.Color('red'),
  '2': pygame.Color('green'),
  '3': pygame.Color('blue'),
  '4': pygame.Color('yellow'),
  '5': pygame.Color('purple'),
}

wallTextures = {
  '1': pygame.image.load('textures/BIGDOOR2.png'),
  '2': pygame.image.load('textures/BIGDOOR3.png'),
  '3': pygame.image.load('textures/BIGDOOR4.png'),
  '4': pygame.image.load('textures/BIGDOOR6.png'),
  '5': pygame.image.load('textures/BIGDOOR7.png'),
  '6': pygame.image.load('textures/wall6.gif'),
}

class Raycaster(object):
  def __init__(self, screen):
    self.screen = screen
    _, _, self.width, self.height = screen.get_rect()
    self.map = []
    self.blockSize = 50
    self.wallHeight = 50
    self.stepSize = 10
    self.turnSize = 5
    self.maxDistance = 200
    self.mapBuffer = []
    self.scaledTextures = {}
    self.player = {
      'x': self.width / 4 + self.blockSize / 2,
      'y': self.height / 2 + self.blockSize / 2,
      'fov': 60,
      'angle': 0
    }

  def load_map(self, filename):
    with open(filename, 'r') as f:
      for line in f.readlines():
        self.map.append(list(line.rstrip()))

  def drawBlock(self, x, y, id):
    texture = wallTextures[id]
    texture = pygame.transform.scale(texture, (self.blockSize, self.blockSize))
    rect = texture.get_rect()
    rect = rect.move(x, y)
    self.mapBuffer.append((texture, rect))

  def drawPlayer(self, color):
    if self.player['x'] < self.width / 2:
      rect = (self.player['x'] - 2, self.player['y'] - 2, 4, 4)
      self.screen.fill(color, rect)

  def castRay(self, angle):
    d = 0
    rads = angle * math.pi / 180
    stepSize = 1
    stepX = stepSize * math.cos(rads)
    stepY = stepSize * math.sin(rads)
    playerPos = (self.player['x'], self.player['y'])
    x = playerPos[0]
    y = playerPos[1]
    while True:
      d += stepSize
      x += stepX
      y += stepY
      i = int(x / self.blockSize)
      j = int(y / self.blockSize)

      if j < len(self.map):
        if i < len(self.map[j]):
          if self.map[j][i] != ' ':
            hitX = x - (i * self.blockSize)
            hitY = y - (j * self.blockSize)
            hit = 0
            if 1 < hitX < self.blockSize - 1:
              if hitY < 1:
                hit = self.blockSize - hitX
              elif hitY >= self.blockSize - 1:
                hit = hitX
            elif 1 < hitY < self.blockSize - 1:
              if hitX < 1:
                hit = hitY
              elif hitX >= self.blockSize -1:
                hit = self.blockSize - hitY
            hit /= self.blockSize
            pygame.draw.line(self.screen, pygame.Color('white'), playerPos, (x, y))
            return d, self.map[j][i], hit

  def render(self):
    halfWidth = int(self.width / 2)
    halfHeight = int(self.height / 2)
    if len(self.mapBuffer) == 0:
      for x in range(0, halfWidth, self.blockSize):
        for y in range(0, self.height, self.blockSize):
          i = int(x / self.blockSize)
          j = int(y / self.blockSize)

          if j < len(self.map):
            if i < len(self.map[j]):
              if self.map[j][i] != ' ':
                self.drawBlock(x, y, self.map[j][i])
    else:
      for block in self.mapBuffer:
        self.screen.blit(block[0], block[1])
        
    RAY_AMOUNT = 100
    self.drawPlayer(pygame.Color('black'))
    for column in range(RAY_AMOUNT):
      angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
      d, id, tx = self.castRay(angle)

      rayWidth = int((1 / RAY_AMOUNT) * halfWidth)
      x = halfWidth + int((column / RAY_AMOUNT) * halfWidth)
      # perceived height
      h = self.height / (d * math.cos((angle - self.player["angle"]) * math.pi / 180)) * self.wallHeight
      y = int(halfHeight - h / 2)

      color_k = (1 - min(1, d / self.maxDistance)) * 255
      texture = wallTextures[id]
      idTb = hash(id * int(h))
      if idTb not in self.scaledTextures:
        self.scaledTextures[idTb] = pygame.transform.scale(texture, (texture.get_width() * rayWidth, int(h)))
      texture = self.scaledTextures[idTb]
      #texture.fill((color_k, color_k, color_k), special_flags=pygame.BLEND_MULT) # too slow
      tx = int(tx * texture.get_width())

      self.screen.blit(texture, (x, y), (tx, 0, rayWidth, texture.get_height()))
      s = pygame.Surface((rayWidth, h))
      s.set_alpha(d / 2)
      s.fill((color_k, color_k, color_k))
      self.screen.blit(s, (x, y))

    # Column
    self.screen.fill(pygame.Color('black'), (halfWidth - 2, 0, 4, self.height))

width = 1000
height = 500

pygame.init()

screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWACCEL)
screen.set_alpha(None)

raycaster = Raycaster(screen)
raycaster.load_map('maps/map2.txt')

clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 16)
def updateFPS():
  fps = str(int(clock.get_fps()))
  fps = font.render(fps, 1, pygame.Color('white'))
  return fps


drawMap = True
pause = False
menuOpen = True
buttonSelected = 0
isRunning = True

def menu():
  global isRunning, menuOpen
  menuOpen = True
  while menuOpen:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        isRunning = False
        menuOpen = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          menuOpen = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        # Start
        if width / 2 - 100 < mouse_pos[0] < (width / 2 - 100) + 200 and height / 2 - 50 < mouse_pos[1] < (height / 2 - 50) + 50:
          menuOpen = False
        # Quit
        if width / 2 - 100 < mouse_pos[0] < (width / 2 - 100) + 200 and height / 2 + 50 < mouse_pos[1] < (height / 2 + 50) + 50:
          isRunning = False
          menuOpen = False
    screen.fill(pygame.Color('blue'))
    pygame.draw.rect(screen, pygame.Color('white'), (width / 2 - 100, height / 2 - 50, 200, 50))
    pygame.draw.rect(screen, pygame.Color('white'), (width / 2 - 100, height / 2 + 50, 200, 50))
    screen.blit(font.render('Start', 1, pygame.Color('black')), (width / 2 - 50, height / 2 - 25))
    screen.blit(font.render('Quit', 1, pygame.Color('black')), (width / 2 - 50, height / 2 + 75))
    screen.blit(font.render('Raycaster', 1, pygame.Color('white')), (width / 2 - 50, height / 2 - 100))
    clock.tick(60)
    pygame.display.flip()

def game():
  global isRunning, menuOpen
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      isRunning = False
    elif event.type == pygame.KEYDOWN:
      newX = raycaster.player['x']
      newY = raycaster.player['y']
      rads = raycaster.player['angle'] * (math.pi / 180)
      if event.key == pygame.K_ESCAPE:
        menuOpen = True
      elif event.key == pygame.K_UP or event.key == pygame.K_w:
        newX += math.cos(rads) * raycaster.stepSize
        newY += math.sin(rads) * raycaster.stepSize
      elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        newX -= math.cos(rads) * raycaster.stepSize
        newY -= math.sin(rads) * raycaster.stepSize
      elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        newX += math.sin(rads) * raycaster.stepSize
        newY -= math.cos(rads) * raycaster.stepSize
      elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        newX -= math.sin(rads) * raycaster.stepSize
        newY += math.cos(rads) * raycaster.stepSize

      i = int(newX / raycaster.blockSize)
      j = int(newY / raycaster.blockSize)

      if raycaster.map[j][i] == ' ':
        raycaster.player['x'] = newX
        raycaster.player['y'] = newY
    
    # get mouse movement
    elif event.type == pygame.MOUSEMOTION:
      x, y = event.pos
      # player see to current mouse position
      raycaster.player['angle'] = math.atan2(y - raycaster.player['y'], x - raycaster.player['x']) * 180 / math.pi

  screen.fill((120,120,120))
  screen.fill((0,0,0), (0,0,15,15))
  screen.fill(pygame.Color("brown"), (int(width / 2), 0, int(width / 2), int(height / 2)))
  screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2), int(width / 2), int(height / 2)))

  raycaster.render()

  screen.fill(pygame.Color("black"), (0, 0, 30, 20))
  screen.blit(updateFPS(), (0,0))
  clock.tick(240)

while isRunning:
  if menuOpen:
    menu()
  else:
    game()

  pygame.display.update()

pygame.quit()