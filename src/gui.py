"""
Copyright 2019, Aleksandar Stojimirovic <stojimirovic@yahoo.com>

Licence: MIT
Source: https://github.com/hooppler/pyHopfieldNeuralNetwork

NOTE: Code is based on: https://github.com/cprn/pong
"""

screen_x = 640
screen_y = 480

try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    from socket import *
    from pygame.locals import *
    from neural_network import NeuralNetwork
except ImportError(err):
    print("couldn't load module. %s" % (err))
    sys.exit(2)

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error(message):
        print('Cannot load image:', fullname)
        raise SystemExit(message)
    return image, image.get_rect()

class Ball(pygame.sprite.Sprite):
    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('ball.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.vector = vector
        self.hit = 0

    def update(self):
        newpos = self.calcnewpos(self.rect,self.vector)
        self.rect = newpos
        (angle,z) = self.vector

        if not self.area.contains(newpos):
            tl = not self.area.collidepoint(newpos.topleft)
            tr = not self.area.collidepoint(newpos.topright)
            bl = not self.area.collidepoint(newpos.bottomleft)
            br = not self.area.collidepoint(newpos.bottomright)
            if tr and tl or (br and bl):
                angle = -angle
            if tl and bl:
                #self.offcourt()
                angle = math.pi - angle
            if tr and br:
                angle = math.pi - angle
                #self.offcourt()
        else:
            # Deflate the rectangles so you can't catch a ball behind the bat
            player1.rect.inflate(-3, -3)
            player2.rect.inflate(-3, -3)

            if self.rect.colliderect(player1.rect) == 1 and not self.hit:
                angle = math.pi - angle
                self.hit = not self.hit
            elif self.rect.colliderect(player2.rect) == 1 and not self.hit:
                angle = math.pi - angle
                self.hit = not self.hit
            elif self.hit:
                self.hit = not self.hit
        self.vector = (angle,z)

    def calcnewpos(self,rect,vector):
        (angle,z) = vector
        (dx,dy) = (z*math.cos(angle),z*math.sin(angle))
        return rect.move(dx,dy)
        
    def get_position(self):
        x = self.rect.centerx
        y = self.rect.centery
        return (float(x)/screen_x, float(y)/screen_y)
        
    def get_angle(self):
        (angle, z) = self.vector
        k = math.floor(angle/(2*math.pi))
        anglep = angle - k*2*math.pi

        return anglep/(2*math.pi)
    

class Player(pygame.sprite.Sprite):
    def __init__(self, side):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('player.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.side = side
        self.speed = 10
        self.state = "still"
        self.reinit()

    def reinit(self):
        self.state = "still"
        self.movepos = [0,0]
        if self.side == "left":
            self.rect.midleft = self.area.midleft
        elif self.side == "right":
            self.rect.midright = self.area.midright

    def update(self):
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos
        pygame.event.pump()

    def moveup(self):
        self.movepos[1] = self.movepos[1] - (self.speed)
        self.state = "moveup"

    def movedown(self):
        self.movepos[1] = self.movepos[1] + (self.speed)
        self.state = "movedown"

    def get_position(self):
        x = self.rect.centerx
        y = self.rect.centery
        return (x,y)

def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((screen_x, screen_y))
    pygame.display.set_caption('Pong Game Controlled by Artificial Neural Network')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    # Initialise players
    global player1
    global player2
    player1 = Player("left")
    player2 = Player("right")

    # Initialise ball
    speed = 13
    rand = ((0.1 * (random.randint(5,8))))
    ball = Ball((0.47,speed))

    # Initialise sprites
    playersprites = pygame.sprite.RenderPlain((player1, player2))
    ballsprite = pygame.sprite.RenderPlain(ball)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()
    
    # Initialise NeuralNetwork
    nn = NeuralNetwork()
    nn.set_random_w()
    input=[0,0,0]
    output=[0]
    t_output=[0]
    
    # Font Initialization
    pygame.font.init()
    font_title = pygame.font.SysFont('Comic Sans MS', 20)
    font_comment = pygame.font.SysFont('Comic Sans MS', 12)
    text_title = font_title.render("Neural Network Pong", False, (0,0,0))
    text_controls = font_comment.render("Keyboard control: 'a' - Player Up, 'y' - Player Down", False, (100, 100, 100))

    # Event loop
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_a:
                    player1.moveup()
                if event.key == K_z:
                    player1.movedown()
                if event.key == K_UP:
                    player2.moveup()
                if event.key == K_DOWN:
                    player2.movedown()
            elif event.type == KEYUP:
                if event.key == K_a or event.key == K_z:
                    player1.movepos = [0,0]
                    player1.state = "still"
                if event.key == K_UP or event.key == K_DOWN:
                    player2.movepos = [0,0]
                    player2.state = "still"

        
        (x,y) = ball.get_position()
        angle = ball.get_angle()
        (xp,yp) = player2.get_position()
        
        input[0] = x
        input[1] = y
        input[2] = angle
        
        nn.set_input(input)
        nn.feed_forward()
        output = nn.get_output()
        
        t_output[0] = y
        
        nn.set_delta_output(t_output)
        
        nn.back_propagation()
        nn.adjust_w()
        
        if output[0] > y:
            player2.moveup()
        else:
            player2.movedown()
        print('Output = {} Position = {}'.format(output[0], x))
                    
        screen.blit(text_title, (230,0))
        screen.blit(text_controls, (20,450))
        screen.blit(background, ball.rect, ball.rect)
        screen.blit(background, player1.rect, player1.rect)
        screen.blit(background, player2.rect, player2.rect)
        ballsprite.update()
        playersprites.update()
        ballsprite.draw(screen)
        playersprites.draw(screen)
        pygame.display.flip()


if __name__ == '__main__': main()