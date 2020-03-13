import pygame, sys, math

pygame.init()

FPS = 60  # frames per second setting
fpsClock = pygame.time.Clock()

# set up the window
WIDTH = 900
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Verlet Simple Cloth System')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 50)
BLUE = (50, 50, 255)
GREY = (200, 200, 200)
ORANGE = (200, 100, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
TRANS = (1, 1, 1)


class Particle:
    def __init__(self, x, y, ax, m=1.0):
        self.m = m
        self.x = x
        self.y = y
        self.oldx = x
        self.oldy = y
        self.newx = x
        self.newy = y
        self.ax = ax
        self.ay = 9.8

    def update(self, delta_t, ax):
        # Verlet Integration
        self.newx = 2.0 * self.x - self.oldx + ax * delta_t * delta_t
        self.newy = 2.0 * self.y - self.oldy + self.ay * delta_t * delta_t
        self.oldx = self.x
        self.oldy = self.y
        self.x = self.newx
        self.y = self.newy

        # Collision Process
        if self.x < 0 or self.x > WIDTH:
            self.x, self.oldx = self.oldx, self.x
        if self.y < 0 or self.y > HEIGHT:
            self.y, self.oldy = self.oldy, self.y

    def draw(self, surf, size):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), size)


class Spring:
    def __init__(self, index0, index1):
        self.index0 = index0
        self.index1 = index1
        delta_x = particles[index0].x - particles[index1].x
        delta_y = particles[index0].y - particles[index1].y
        self.restLength = math.sqrt(delta_x * delta_x + delta_y * delta_y)

    def update(self, k):
        delta_x = particles[self.index1].x - particles[self.index0].x
        delta_y = particles[self.index1].y - particles[self.index0].y
        deltaLength = math.sqrt(delta_x * delta_x + delta_y * delta_y)
        diff = (deltaLength - self.restLength) / deltaLength

        if self.index0 != 0 and self.index0 != NUM_X - 1:
            particles[self.index0].x += k * diff * delta_x
            particles[self.index0].y += k * diff * delta_y
        if self.index1 != 0 and self.index1 != NUM_X - 1:
            particles[self.index1].x -= k * diff * delta_x
            particles[self.index1].y -= k * diff * delta_y

    def draw(self, surf, size):
        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y
        pygame.draw.line(surf, WHITE, (int(x0), int(y0)), (int(x1), int(y1)), size)


class Slider():
    def __init__(self, name, val, maxi, mini, pos):
        self.val = val  # start value
        self.maxi = maxi  # maximum at slider position right
        self.mini = mini  # minimum at slider position left
        self.xpos = pos  # x-location on screen
        self.ypos = 550
        self.surf = pygame.surface.Surface((100, 50))
        self.hit = False  # the hit attribute indicates slider movement due to mouse interaction

        self.txt_surf = font.render(name, 1, BLACK)
        self.txt_rect = self.txt_surf.get_rect(center=(50, 15))

        # Static graphics - slider background #
        self.surf.fill((100, 100, 100))
        pygame.draw.rect(self.surf, GREY, [0, 0, 100, 50], 3)
        pygame.draw.rect(self.surf, ORANGE, [10, 10, 80, 10], 0)
        pygame.draw.rect(self.surf, WHITE, [10, 30, 80, 5], 0)

        self.surf.blit(self.txt_surf, self.txt_rect)  # this surface never changes

        # dynamic graphics - button surface #
        self.button_surf = pygame.surface.Surface((20, 20))
        self.button_surf.fill(TRANS)
        self.button_surf.set_colorkey(TRANS)
        pygame.draw.circle(self.button_surf, BLACK, (10, 10), 6, 0)
        pygame.draw.circle(self.button_surf, ORANGE, (10, 10), 4, 0)

    def draw(self):
        """ Combination of static and dynamic graphics in a copy of
    the basic slide surface
    """
        # static
        surf = self.surf.copy()

        # dynamic
        pos = (10 + int((self.val - self.mini) / (self.maxi - self.mini) * 80), 33)
        self.button_rect = self.button_surf.get_rect(center=pos)
        surf.blit(self.button_surf, self.button_rect)
        self.button_rect.move_ip(self.xpos, self.ypos)  # move of button box to correct screen position

        # screen
        screen.blit(surf, (self.xpos, self.ypos))

    def move(self):
        """
    The dynamic part; reacts to movement of the slider button.
    """
        self.val = (pygame.mouse.get_pos()[0] - self.xpos - 10) / 80 * (self.maxi - self.mini) + self.mini
        if self.val < self.mini:
            self.val = self.mini
        if self.val > self.maxi:
            self.val = self.maxi


delta_t = 0.1
NUM_ITER = 10

font = pygame.font.SysFont("Verdana", 25)
windspeed = Slider("WindSpeed", 10, 15, 1, 0)
k = Slider("k", 0, 1, 0, 225)
acce = Slider("Acce", 0, 100, 0, 450)
ballsize = Slider("BallSize", 200, 200, 20, 675)
slides = [windspeed, k, acce, ballsize, ]

# create particles
NUM_X = 15
NUM_Y = 20
particles = []
for j in range(NUM_Y):
    for i in range(NUM_X):
        x = 350 + i * 20.0
        y = (j+2) * 20.0
        p = Particle(x, y, acce.val)
        particles.append(p)

# create springs
springs = []
for j in range(NUM_Y):
    for i in range(NUM_X):
        if i < (NUM_X - 1):
            index0 = i + j * NUM_X
            index1 = (i + 1) + j * NUM_X
            c = Spring(index0, index1)
            springs.append(c)
        if j < (NUM_Y - 1):
            index0 = i + j * NUM_X
            index1 = i + (j + 1) * NUM_X
            c = Spring(index0, index1)
            springs.append(c)

while True:
    screen.fill(BLACK)
    # Move slides
    for s in slides:
        if s.hit:
            s.move()

    for s in slides:
        s.draw()

    # particles update
    for i in range(len(particles)):
        if i == 0 or i == NUM_X - 1:
            continue
        particles[i].update(delta_t, acce.val)

    # particles draw
    for i in range(len(particles)):
        particles[i].draw(screen, 3)

    # springs update
    for i in range(NUM_ITER):
        for ii in range(len(springs)):
            springs[ii].update(k.val)

    # springs draw
    for i in range(len(springs)):
        springs[i].draw(screen, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for s in slides:
                if s.button_rect.collidepoint(pos):
                    s.hit = True
        elif event.type == pygame.MOUSEBUTTONUP:
            for s in slides:
                s.hit = False

    pygame.display.update()
    fpsClock.tick(FPS)
