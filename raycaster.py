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
  'f': pygame.image.load('textures/wall4.png'),
}

enemies = [
  {
    'id': 0,
    'x': 100,
    'y': 200,
    'size': 50,
    'sprite': pygame.image.load('textures/sprite1.png'),
  },
  {
    'id': 1,
    'x': 100,
    'y': 400,
    'size': 50,
    'sprite': pygame.image.load('textures/sprite2.png'),
  },
  {
    'id': 2,
    'x': 400,
    'y': 100,
    'size': 50,
    'sprite': pygame.image.load('textures/sprite3.png'),
  },
  {
    'id': 3,
    'x': 400,
    'y': 425,
    'size': 50,
    'sprite': pygame.image.load('textures/sprite4.png'),
  },
]

maps = {
  'Mapa 1': {
    'file': 'maps/map.txt',
    'next': 'Mapa 2',
  },
  'Mapa 2': {
    'file': 'maps/map2.txt',
    'next': 'Mapa 3',
  },
  'Mapa 3': {
    'file': 'maps/map3.txt',
    'next': 'Mapa 1',
  },
}

class Raycaster(object):
  def __init__(self, screen):
    self.screen = screen
    _, _, self.width, self.height = screen.get_rect()
    self.map = []
    self.actualMap = ''
    self.blockSize = 50
    self.wallHeight = self.height / 10
    self.stepSize = 10
    self.turnSize = 5
    self.maxDistance = 200
    self.mapBuffer = []
    self.zBuffer = [float('inf') for z in range(int(self.width / 2))]
    self.scaledTextures = {}
    self.player = {
      'x': self.width / 4 + self.blockSize / 2,
      'y': self.height / 2 + self.blockSize / 2,
      'fov': 60,
      'angle': 0,
      'speed': 0.4,
    }

  def load_map(self, mapName):
    columns = 0
    rows = 0
    self.actualMap = mapName
    filename = maps[mapName]['file']
    with open(filename, 'r') as f:
      for line in f.readlines():
        self.map.append(list(line.rstrip()))
      columns = len(self.map[0])
      rows = len(self.map)
    self.blockSize = int((self.width / 2) / columns) if columns > rows else int((self.width / 2) / rows)

  def drawBlock(self, x, y, id):
    texture = wallTextures[id]
    texture = pygame.transform.scale(texture, (self.blockSize, self.blockSize))
    rect = texture.get_rect()
    rect = rect.move(x, y)
    self.mapBuffer.append((texture, rect))

  def drawPlayer(self, color):
    if self.player['x'] < self.width / 2:
      rect = (self.player['x'] - 3, self.player['y'] - 3, 6, 6)
      self.screen.fill(color, rect)

  def drawIcon(self):
    for enemy in enemies:
      rect = (enemy['x'] - 3, enemy['y'] - 3, 6, 6)
      self.screen.fill(pygame.Color('red'), rect)

  def drawSprite(self, x, y, sprite, size):
    spriteDist = math.sqrt((x - self.player['x']) ** 2 + (y - self.player['y']) ** 2)
    spriteAngle = math.atan2(y - self.player['y'], x - self.player['x'])
    aspectRatio = sprite.get_width() / sprite.get_height()
    spriteHeight = self.height / spriteDist * size
    spriteWidth = spriteHeight * aspectRatio
    angleRads = self.player['angle'] * math.pi / 180
    fovRads = self.player['fov'] * math.pi / 180
    # punto inicial para dibujar
    startX = ((self.width * 3/4) + (spriteAngle - angleRads) * self.width / 2 / fovRads) - spriteWidth / 2
    startY = self.height / 2 - spriteHeight / 2

    #texture = pygame.transform.scale(sprite, (int(spriteWidth), int(spriteHeight)))
    #self.screen.blit(texture, (int(startX), int(startY)))

    for x in range(int(startX), int(startX + spriteWidth)):
      for y in range(int(startY), int(startY + spriteHeight)):
        if (self.width / 2 < x < self.width):
          if self.zBuffer[x - int(self.width / 2)] >= spriteDist:
            tx = (x - int(startX)) * sprite.get_width() / spriteWidth
            ty = (y - int(startY)) * sprite.get_height() / spriteHeight
            pixel = sprite.get_at((int(tx), int(ty)))
            if pixel != (152,0,136,255):
              self.screen.set_at((x, y), pixel)
              self.zBuffer[x - int(self.width / 2)] = spriteDist

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
    # map name
    self.screen.fill(pygame.Color('black'), (width / 4 - 55, height - 25, 65, 25))
    font = pygame.font.SysFont('Arial', 20)
    text = font.render(self.actualMap, True, pygame.Color('white'))
    self.screen.blit(text, (width / 4 - 50, height - 25))
        
    RAY_AMOUNT = int((self.width / 2) / 5)
    self.drawPlayer(pygame.Color('black'))
    self.drawIcon()
    for column in range(RAY_AMOUNT):
      angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
      d, id, tx = self.castRay(angle)

      rayWidth = int((1 / RAY_AMOUNT) * halfWidth)
      for i in range(rayWidth):
        self.zBuffer[column * rayWidth + i] = d
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

    # enemies
    for enemy in enemies:
      self.drawSprite(enemy['x'], enemy['y'], enemy['sprite'], enemy['size'])

    # Column
    self.screen.fill(pygame.Color('black'), (halfWidth - 2, 0, 4, self.height))

width = 1000
height = 500

pygame.init()

screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWACCEL)
screen.set_alpha(None)

raycaster = Raycaster(screen)
raycaster.load_map('Mapa 1')

clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 16)
def updateFPS():
  fps = str(int(clock.get_fps()))
  fps = font.render(fps, 1, pygame.Color('white'))
  return fps

offsetX = 0
offsetY = height * 0.1
focused = 0
buttonsOrder = ['start', 'quit']
buttons = {
  'start': {
    'x': width / 2 - (width * 0.1) + offsetX,
    'y': height / 2 - (height * 0.05) + offsetY,
    'w': width * 0.2,
    'h': height * 0.1,
    'text': 'Start',
    'textPos': {
      'x': width / 2 + offsetX,
      'y': height / 2 - (height * 0) + offsetY
    },
    'color': pygame.Color('grey'),
    'focusColor': pygame.Color('#3258e3'),
  },
  'quit': {
    'x': width / 2 - (width * 0.1) + offsetX,
    'y': height / 2 + (height * 0.15) + offsetY,
    'w': width * 0.2,
    'h': height * 0.1,
    'text': 'Quit',
    'textPos': {
      'x': width / 2 + offsetX,
      'y': height / 2 + (height * 0.2) + offsetY
    },
    'color': pygame.Color('grey'),
    'focusColor': pygame.Color('#3258e3'),
  }
}

drawMap = True
pause = False
menuOpen = True
mousePos = (0, 0)
buttonSelected = 0
isRunning = True

def menu():
  global isRunning, menuOpen, focused
  menuOpen = True
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      isRunning = False
      menuOpen = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        menuOpen = False
      if event.key == pygame.K_DOWN:
        focused = (focused + 1) % len(buttonsOrder)
      if event.key == pygame.K_UP:
        focused = (focused - 1) % len(buttonsOrder)
    if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER)):
      mouse_pos = pygame.mouse.get_pos()
      if (event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER)):
        mouse_pos = (buttons[buttonsOrder[focused]]['x'] + 1, buttons[buttonsOrder[focused]]['y'] + 1)
      for button in buttons:
        if buttons[button]['x'] < mouse_pos[0] < buttons[button]['x'] + buttons[button]['w'] and buttons[button]['y'] < mouse_pos[1] < buttons[button]['y'] + buttons[button]['h']:
          focused = buttonsOrder.index(button)
          if button == 'start':
            menuOpen = False
          if button == 'quit':
            isRunning = False
            menuOpen = False

    # charge images
    bg = pygame.image.load('images/bg2.jpg')
    bg = pygame.transform.scale(bg, (width, height))
    screen.blit(bg, (0, 0))
    title = pygame.image.load('images/at2.png')
    title = pygame.transform.scale(title, (int((title.get_width() / title.get_height()) * (height * 0.3)), int(height * 0.3)))
    title2 = pygame.image.load('images/zoom2.png')
    title2 = pygame.transform.scale(title2, (int((title2.get_width() / title2.get_height()) * (height * 0.3)), int(height * 0.3)))
    screen.blit(title, ((width * 0.46) - title.get_width() + offsetX, height * 0.05 + offsetY))
    screen.blit(title2, (width * 0.46 + offsetX, height * 0.05 + offsetY))
    # draw buttons
    for button in buttons:
      if focused == buttonsOrder.index(button):
        screen.fill(buttons[button]['focusColor'], (buttons[button]['x'], buttons[button]['y'], buttons[button]['w'], buttons[button]['h']))
      else:
        screen.fill(buttons[button]['color'], (buttons[button]['x'], buttons[button]['y'], buttons[button]['w'], buttons[button]['h']))
      textImage = pygame.image.load(f'images/{button}.png')
      textImage = pygame.transform.scale(textImage, (int(textImage.get_width() / textImage.get_height()) * int(buttons[button]['h']), int(buttons[button]['h'])))
      screen.blit(textImage, (buttons[button]['textPos']['x'] - int(textImage.get_width() / 2), buttons[button]['textPos']['y'] - int(textImage.get_height() / 2)))

    clock.tick(60)
    pygame.display.update()

actualMovements = []
def movement():
  global actualMovements
  newX = raycaster.player['x']
  newY = raycaster.player['y']
  rads = raycaster.player['angle'] * (math.pi / 180)
  i = 0
  j = 0
  if 'up' in actualMovements:
    newX += math.cos(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    newY += math.sin(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    i = int((newX + math.cos(rads) * 10) / raycaster.blockSize)
    j = int((newY + math.sin(rads) * 10) / raycaster.blockSize)
  if 'down' in actualMovements:
    newX -= math.cos(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    newY -= math.sin(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    i = int((newX - math.cos(rads) * 10) / raycaster.blockSize)
    j = int((newY - math.sin(rads) * 10) / raycaster.blockSize)
  if 'left' in actualMovements:
    newX += math.sin(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    newY -= math.cos(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    i = int((newX + math.cos(rads) * 10) / raycaster.blockSize)
    j = int((newY - math.sin(rads) * 10) / raycaster.blockSize)
  if 'right' in actualMovements:
    newX -= math.sin(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    newY += math.cos(rads) * ((265 / clock.get_fps()) * raycaster.player['speed'])
    i = int((newX - math.cos(rads) * 10) / raycaster.blockSize)
    j = int((newY + math.sin(rads) * 10) / raycaster.blockSize)
  if raycaster.map[j][i] == ' ':
    raycaster.player['x'] = newX
    raycaster.player['y'] = newY
  if raycaster.map[j][i] == 'f':
    raycaster.map = []
    raycaster.mapBuffer = []
    raycaster.load_map(maps[raycaster.actualMap]['next'])
    raycaster.player['x'] = width / 4 + raycaster.blockSize / 2
    raycaster.player['y'] = height / 2 + raycaster.blockSize / 2

def game():
  global isRunning, menuOpen, actualMovements, mousePos
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      isRunning = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        menuOpen = True
      elif event.key == pygame.K_UP or event.key == pygame.K_w:
        actualMovements.append('up')
      elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        actualMovements.append('down')
      elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        actualMovements.append('left')
      elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        actualMovements.append('right')

    elif event.type == pygame.KEYUP:
      if event.key == pygame.K_UP or event.key == pygame.K_w:
        actualMovements.remove('up')
      elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        actualMovements.remove('down')
      elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        actualMovements.remove('left')
      elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        actualMovements.remove('right')
    
    # get mouse movement
    elif event.type == pygame.MOUSEMOTION:
      mousePos = event.pos
      # player see to current mouse position
  movement()
  raycaster.player['angle'] = math.atan2(mousePos[1] - raycaster.player['y'], mousePos[0] - raycaster.player['x']) * 180 / math.pi

  screen.fill((120,120,120))
  screen.fill((0,0,0), (0,0,15,15))
  screen.fill(pygame.Color("brown"), (int(width / 2), 0, int(width / 2), int(height / 2)))
  screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2), int(width / 2), int(height / 2)))

  raycaster.render()

  screen.fill(pygame.Color("black"), (0, 0, 30, 20))
  screen.blit(updateFPS(), (0,0))
  clock.tick(265)

while isRunning:
  if menuOpen:
    menu()
  else:
    game()

  pygame.display.update()

pygame.quit()