from settings import *
from game_clock import *
from pygame import *
from level_class import *

import sys
import level_data_intro as levels_intro
import level_data_dad as levels_dad
import level_data_cora as levels_cora
import level_data_intermediate as levels_intermediate
import level_data_expert as levels_expert

import time

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK_X = int(WIN_WIDTH / 5)
CAMERA_SLACK_Y = int(WIN_HEIGHT / 5)


def my_print(message):
    if False:
        print
        message


def main():
    global DISPLAYSURF, TIMER, levels, screen, SOUND_LIFE, SOUND_BOUNCE_LARGE, SOUND_BOUNCE_MED
    global SOUND_HURT2, SOUND_HURT1, SOUND_DIE, SOUND_PIT_DIE, SOUND_JUMP, SOUND_PORTAL
    global SOUND_STICKY_ON, SOUND_STICKY_MOVE, SOUND_STICKY_OFF, SOUND_BOUNCE_SMALL

    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Little Square, Long Journey! Producers: Link, Mark")

    TIMER = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    SOUND_LIFE = pygame.mixer.Sound(SOUND_LIFE_FILE)
    SOUND_STICKY_MOVE = pygame.mixer.Sound(SOUND_STICKY_MOVE_FILE)
    SOUND_STICKY_MOVE.set_volume(0.3)
    SOUND_STICKY_ON = pygame.mixer.Sound(SOUND_STICKY_ON_FILE)
    SOUND_STICKY_OFF = pygame.mixer.Sound(SOUND_STICKY_OFF_FILE)
    SOUND_HURT1 = pygame.mixer.Sound(SOUND_HURT_FILE1)
    SOUND_HURT2 = pygame.mixer.Sound(SOUND_HURT_FILE2)
    SOUND_BOUNCE_LARGE = pygame.mixer.Sound(SOUND_BOUNCE_LARGE_FILE)
    SOUND_BOUNCE_MED = pygame.mixer.Sound(SOUND_BOUNCE_MEDIUM_FILE)
    SOUND_BOUNCE_SMALL = pygame.mixer.Sound(SOUND_BOUNCE_SMALL_FILE)
    SOUND_BOUNCE_SMALL.set_volume(0.5)
    SOUND_JUMP = pygame.mixer.Sound(SOUND_JUMP_FILE)
    SOUND_JUMP.set_volume(0.5)
    SOUND_DIE = pygame.mixer.Sound(SOUND_DIE_FILE)
    SOUND_PIT_DIE = pygame.mixer.Sound(SOUND_PIT_DIE_FILE)
    SOUND_PORTAL = pygame.mixer.Sound(SOUND_PORTAL_FILE)

    # TODO show_start_screen
    instructions_message()
    while True:
        levels = level_pack_choice_screen()
        start_level_num = level_num_choice_screen(levels)
        run_game(levels, start_level_num)


def run_game(levels, start_level_num):
    global cameraX, cameraY
    global message_life, message_life2
    global DISPLAYSURF, BASICFONT

    start_the_clock()

    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    player = Player(32, 32)
    num_levels = len(levels)

    for level_number in range(start_level_num, num_levels):
        global bg, message_prompt, message_end
        player.finished_level = False
        player.reset_position(32, 32)
        player.last_hurt_time = current_time() - 10.0

        level = levels[level_number]
        level_layout = level.layout
        level_width = len(level_layout[0]) * 32
        level_height = len(level_layout) * 32
        up = down = left = right = False
        bg = Surface((32, 32))
        bg.convert()
        bg.fill(Color("#000032"))
        entities = pygame.sprite.Group()
        platforms = []
        start_message = 'Level {}: {}'.format(level_number + 1, level.name)
        info_message = level.message
        message_prompt = 'Press any arrow or space to continue'
        message_life2 = 'lives = {}'.format(player.lives - 1)

        x = y = 0
        cameraX = cameraY = 0
        message_life = ""

        # build the level
        for row in level_layout:
            for col in row:
                if col == "P":
                    p = Platform(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "D":
                    d = PlatformPit(x, y)
                    platforms.append(d)
                    entities.add(d)
                if col == "H":
                    h = PlatformHurtFull(x, y)
                    platforms.append(h)
                    entities.add(h)
                if col == "h":
                    h = PlatformHurt(x, y)
                    platforms.append(h)
                    entities.add(h)
                if col == "L":
                    l = PlatformLife(x, y)
                    platforms.append(l)
                    entities.add(l)
                if col == "B":
                    b = PlatformBouncy1(x, y)
                    platforms.append(b)
                    entities.add(b)
                if col == "S":
                    s = PlatformSticky(x, y)
                    platforms.append(s)
                    entities.add(s)
                if col == "M":
                    m = Platformmovingcarpetright(x, y)
                    platforms.append(m)
                    entities.add(m)
                if col == "I":
                    i = PlatformIllusion(x, y)
                    platforms.append(i)
                    entities.add(i)
                if col == "G":
                    g = PlatformGlass(x, y)
                    platforms.append(g)
                    entities.add(g)
                if col == "U":
                    u = PlatformFly(x, y)
                    platforms.append(u)
                    entities.add(u)
                if col == "W":
                    w = Platformmovingcarpetleft(x, y)
                    platforms.append(w)
                    entities.add(w)
                if col == "F":
                    f = FakeExitBlock(x, y)
                    platforms.append(f)
                    entities.add(f)
                if col == "E":
                    e = ExitBlock(x, y)
                    platforms.append(e)
                    entities.add(e)
                x += 32
            y += 32
            x = 0

        entities.add(player)
        # print "Level {}".format(level_number + 1)

        # start interactive part of level
        player.running_level = False
        while not player.finished_level:
            TIMER.tick(60)

            for e in pygame.event.get():
                if e.type == QUIT:
                    raise SystemExit("QUIT")

                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    raise SystemExit("ESCAPE")
                if e.type == KEYDOWN and e.key == K_F5:
                    return
                if e.type == KEYDOWN and (e.key == K_UP or e.key == K_SPACE):
                    up = True
                    player.running_level = True
                    if player.up_was_released:
                        player.last_up_time = current_time()
                if e.type == KEYDOWN and e.key == K_DOWN:
                    down = True
                    player.running_level = True
                if e.type == KEYDOWN and e.key == K_LEFT:
                    left = True
                    player.running_level = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                    player.running_level = True

                if e.type == KEYUP and (e.key == K_UP or e.key == K_SPACE):
                    up = False
                if e.type == KEYUP and e.key == K_DOWN:
                    down = False
                if e.type == KEYUP and e.key == K_RIGHT:
                    right = False
                if e.type == KEYUP and e.key == K_LEFT:
                    left = False
                if e.type == KEYUP and e.key == K_RIGHT:
                    right = False

            # draw background
            for y in range(32):
                for x in range(32):
                    screen.blit(bg, (x * 32, y * 32))

            # update player, draw everything else
            if player.running_level:
                player.update(up, down, left, right, platforms, level_width, level_height)

            if player.hp <= 0:
                SOUND_DIE.play()
                player.lives -= 1
                player.hp = NUM_HP
                up = left = right = down = False
                die_message("Ouch, you lost a life", screen, TIMER, bg)
                my_print("Died: lives left = {}".format(player.lives))
                player.reset_position(32, 32)
                player.running_level = False
                pygame.event.get()  # clear out event queue

            if player.lives <= 0:
                end_game_message(screen, TIMER, bg)
                my_print("No lives left. Game over!")
                pygame.event.get()  # clear out event queue
                return

                # camera movement
            for entity in entities:
                if isinstance(entity, Platform):
                    entity.update(cameraX, cameraY)

            # redraw entities
            entities.draw(screen)

            # draw text
            if not player.running_level:
                SOUND_LIFE.stop()
                SOUND_STICKY_MOVE.stop()
                SOUND_STICKY_ON.stop()
                SOUND_STICKY_OFF.stop()
                SOUND_HURT1.stop()
                SOUND_HURT2.stop()
                SOUND_BOUNCE_SMALL.stop()
                SOUND_BOUNCE_MED.stop()
                SOUND_BOUNCE_LARGE.stop()
                SOUND_JUMP.stop()
                SOUND_DIE.stop()

                draw_big_message(start_message, color=BLUE, pulse_time=1.0)
                draw_small_message(info_message, color=BLUE, pulse_time=1.0)
                draw_prompt_message(message_prompt, color=BLUE, pulse_time=1.5)
                level_start_time = current_time()

            message_time = 'Time = {:3.1f}'.format(elapsed_time(level_start_time))
            message_life2 = 'lives = {}'.format(player.lives - 1)
            message_life = 'lives = {}'.format(player.lives)
            draw_life_message(message_life, color=BLUE, pulse_time=1.5)
            draw_hp(player.hp)
            draw_time_message(message_time, color=RED, pulse_time=1.5)

            pygame.display.update()

        # Add the time spent on the just-finished level
        this_level_time = elapsed_time(level_start_time)
        get_one_up = this_level_time < level.fast_time
        player.all_previous_level_times = player.all_previous_level_times + this_level_time
        print
        "Finished level {}, total playing time = {:3.1f}".format(level_number + 1, player.all_previous_level_times)

        message_big = "Finished level: time = {:3.1f}".format(this_level_time)
        message_small = ["total time = {:3.1f}".format(player.all_previous_level_times),
                         "press spacebar to continue..."]

        if get_one_up:
            player.lives += 1
            message_big += '  Fast! 1 UP!!'
        end_message(message_life, message_big, message_small, TIMER, screen, bg, player.hp)

        if level_number + 1 == num_levels:
            print
            "You win!!!!!!"
            message_big = "You WIN!!!!!!!"
            message_small = ["total time = {:3.1f}".format(player.all_previous_level_times),
                             "playing {} out of {} levels".format(num_levels - start_level_num, num_levels),
                             "press spacebar to play again!",
                             "press escape to terminate the game."]
            end_message(message_life, message_big, message_small, TIMER, screen, bg, player.hp)
            return


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Player(Entity):

    def __init__(self, x, y):
        Entity.__init__(self)
        self.player_size = 30
        self.image = Surface((self.player_size, self.player_size))
        self.image.fill((0, 225, 0))
        self.image.convert()
        self.rect = Rect(x, y, self.player_size, self.player_size)
        self.last_hurt_time = current_time() - 10.0
        self.last_fly_time = 0
        self.lives = NUM_LIVES
        self.hp = NUM_HP
        self.running_level = False
        self.finished_level = False
        self.all_previous_level_times = 0
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.onFly = False
        self.onSticky = False
        self.onIce = False
        self.groundSpeed = 0
        self.is_jumping = False
        self.is_flying = False
        self.last_up_time = -10.0
        self.last_bounce_time = -10.0
        self.up_was_released = True

    def reset_position(self, x, y):
        global cameraX, cameraY
        cameraX = cameraY = 0
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.onFly = False
        self.onIce = False
        self.groundSpeed = 0
        self.last_up_time = -10.0
        self.last_bounce_time = -10.0

        self.rect = Rect(x, y, self.player_size, self.player_size)
        self.last_hurt_time = current_time() - 10.0
        self.last_fly_time = 0
        self.image.fill((0, 225, 0))

    def add_jump_boost(self):
        # A fresh jump will add some speed up to a point
        self.yvel = min(self.yvel, max(-18.0, self.yvel - 3.0))

    def update(self, up, down, left, right, platforms, level_width, level_height):
        global cameraX, cameraY
        if up:
            # only jump if on the ground
            if self.onSticky:
                self.is_jumping = True  # This is counter intuitive, but allows the slide up off the stickies.
                self.yvel = self.yvel - 0.65
                # SOUND_STICKY_MOVE.play()
            elif (self.onGround or self.is_flying) and self.up_was_released:
                # start a new jump
                self.is_jumping = True
                self.up_was_released = False
                self.yvel -= 10.2
                SOUND_JUMP.play()
            elif not self.onGround and self.up_was_released and elapsed_time(self.last_bounce_time) < UP_JUMP_TIME:
                self.add_jump_boost()
                self.is_jumping = True
                self.up_was_released = False

        else:
            self.is_jumping = False
            self.up_was_released = True

        if down:
            if self.onSticky:
                self.yvel = self.yvel + 0.65
            self.onSticky = False

        if left:
            if self.xvel > 0.0:
                if self.onGround and not self.onIce:
                    # self.xvel = 0.0
                    self.xvel = self.xvel * 0.4  # extra help changing direction on ground
                else:
                    self.xvel = self.xvel - 0.3  # extra help changing direction in air

            if self.onGround:
                self.xvel = self.xvel - 0.65
            else:
                self.xvel = self.xvel - 0.4

        if right:
            if self.xvel < 0.0:
                if self.onGround and not self.onIce:
                    # self.xvel = 0.0
                    self.xvel = self.xvel * 0.3  # extra help changing direction on ground
                else:
                    self.xvel = self.xvel + 0.3  # extra help changing direction in air

            if self.onGround:
                self.xvel = self.xvel + 0.65
            else:
                self.xvel = self.xvel + 0.4

        # if not self.onGround and not self.onSticky:
        if not self.onSticky:
            # only accelerate with gravity if in the air
            self.yvel += GRAVITY
            if not self.is_jumping and self.yvel < 0:
                # This allows you to have big and little jumps depending on how long you hold up.
                self.yvel += 1.3 * GRAVITY
            # max falling speed
            if self.yvel > 90:
                self.yvel = 90
        if self.onGround and not (left or right) and not self.onIce:
            # this will let you change direction quickly but not immediately
            self.xvel = self.xvel * .2
            if abs(self.xvel) < 0.2:
                self.xvel = 0.

        # only move up or down on stickies when you press up or down.
        if self.onSticky and not (up or down):
            self.yvel = 0

        # give the player a little help... let them fight the groundspeed if they jump
        # if they are actively pushing in the opposite direction of the carpet, lessen the effect of the carpet
        # by shrinking the groundspeed
        if not self.onGround and ((self.xvel > 0) - (self.xvel < 0)) != (
                (self.groundSpeed > 0) - (self.groundSpeed < 0)) and (left or right):
            self.groundSpeed *= 0.975

        # increment in x direction
        self.rect.left += self.xvel + self.groundSpeed

        # reset things that are set in collision detection
        last_onSticky = self.onSticky
        self.onSticky = False
        if elapsed_time(self.last_fly_time) > FLY_TIME:
            self.is_flying = False

        # do x-axis collisions
        self.collide(self.xvel + self.groundSpeed, 0, platforms)

        # limit horizontal speed
        if self.xvel < -8.0:
            self.xvel = -8.0
        if self.xvel > 8.0:
            self.xvel = 8.0

        # increment/move in y direction
        if self.yvel > 0:
            # This makes sure that gravity (when onGround) will move player enough downward to ensure it
            # goes down at least 1 pixel so that collisions will happen and set OnGround appropriately again after
            # the reset a few lines below.
            self.rect.top = self.rect.top + max(1.0, self.yvel)
        else:
            self.rect.top = self.rect.top + self.yvel

        # assuming we're in the air
        if not self.onSticky:
            self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)

        # Limit Vertical Speed
        if self.onSticky:
            if self.yvel < -5.0:
                self.yvel = -5.0
            if self.yvel > 5.0:
                self.yvel = 5.0

        if not last_onSticky and self.onSticky:
            SOUND_STICKY_ON.play()

        if last_onSticky and not self.onSticky:
            SOUND_STICKY_OFF.play()

        if self.onSticky and (abs(self.yvel) + abs(self.xvel)) > 2.0:
            SOUND_STICKY_MOVE.play()
        else:
            SOUND_STICKY_MOVE.stop()

        # calculate new x camera
        old_cameraX = cameraX

        if (cameraX + HALF_WIDTH) - (self.rect.centerx + cameraX) > CAMERA_SLACK_X:
            cameraX = (self.rect.centerx + cameraX) + CAMERA_SLACK_X - HALF_WIDTH
        elif (self.rect.centerx + cameraX) - (cameraX + HALF_WIDTH) > CAMERA_SLACK_X:
            cameraX = (self.rect.centerx + cameraX) - CAMERA_SLACK_X - HALF_WIDTH

        if cameraX < 0:
            cameraX = 0
        if cameraX > level_width - WIN_WIDTH:
            cameraX = level_width - WIN_WIDTH

        # calculate new camera y
        old_cameraY = cameraY

        if (cameraY + HALF_HEIGHT) - (self.rect.centery + cameraY) > CAMERA_SLACK_Y:
            cameraY = (self.rect.centery + cameraY) + CAMERA_SLACK_Y - HALF_HEIGHT
        elif (self.rect.centery + cameraY) - (cameraY + HALF_HEIGHT) > CAMERA_SLACK_Y:
            cameraY = (self.rect.centery + cameraY) - CAMERA_SLACK_Y - HALF_HEIGHT

        if cameraY < 0:
            cameraY = 0
        if cameraY > level_height - WIN_HEIGHT:
            cameraY = level_height - WIN_HEIGHT

        # update player, based on camera movement.
        self.rect.centerx = self.rect.centerx - (cameraX - old_cameraX)
        self.rect.centery = self.rect.centery - (cameraY - old_cameraY)

        # making you turn red after hurt
        if elapsed_time(self.last_hurt_time) < BANDAID_TIME:
            self.image.fill((255, 0, 0, 5))
        elif self.is_flying:
            self.image.fill(DARKGREEN)
        else:
            self.image.fill((0, 225, 0))

    def bouncy_sound(self, vel):
        if abs(vel) >= 15.0:
            SOUND_BOUNCE_LARGE.play()
        if 8.0 <= abs(vel) < 15.0:
            SOUND_BOUNCE_MED.play()
        if 3.0 < abs(vel) < 8.0:
            SOUND_BOUNCE_SMALL.play()

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):

                # Handle collision with an Exit Block
                if isinstance(p, ExitBlock):
                    SOUND_PORTAL.play()
                    self.finished_level = True

                if isinstance(p, FakeExitBlock):
                    self.groundSpeed = 0
                    self.reset_position(32, 32)
                    self.cameraX = self.cameraY = 0
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.yvel = 0

                if isinstance(p, PlatformGlass):
                    self.groundSpeed = 0
                    self.onIce = True
                    self.onGround = True
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.yvel = 0

                if isinstance(p, PlatformFly):
                    self.groundSpeed = 0
                    self.is_flying = True
                    self.last_fly_time = current_time()
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = 0
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0

                # Handle collision with an Bouncy Block
                elif isinstance(p, PlatformBouncy1):
                    my_print("Bouncy: ")
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        my_print("collide left")
                        self.xvel = -self.xvel
                        self.groundSpeed = -self.groundSpeed
                        self.bouncy_sound(self.xvel)
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        my_print("collide right")
                        self.xvel = -self.xvel
                        self.groundSpeed = -self.groundSpeed
                        self.bouncy_sound(self.xvel)
                    if yvel < 0:
                        self.groundSpeed = 0
                        self.rect.top = p.rect.bottom
                        self.yvel = -self.yvel
                        my_print("collide bottom bounce off")
                        self.bouncy_sound(self.yvel)
                    if yvel > 0:
                        self.groundSpeed = 0
                        self.rect.bottom = p.rect.top
                        my_print('Bounce start yvel {}'.format(self.yvel))

                        # lose a bit of energy
                        self.yvel = -max(0.0, self.yvel - 1.45 * GRAVITY) * 0.85

                        if elapsed_time(self.last_up_time) < UP_JUMP_TIME:
                            self.add_jump_boost()
                        else:
                            self.last_bounce_time = current_time()

                        if self.yvel > -3 * GRAVITY:
                            self.yvel = 0.0
                            self.is_jumping = False
                            self.onGround = True
                            # self.up_was_released = True
                        else:
                            self.is_jumping = True
                            self.up_was_released = False
                            self.onGround = False

                        self.bouncy_sound(self.yvel)

                        my_print("collide top bounce off")

                elif isinstance(p, PlatformIllusion):
                    my_print("Illusion: ")
                    if xvel > 0:
                        pass
                    if xvel < 0:
                        pass
                    if yvel < 0:
                        pass
                    if yvel > 0:
                        pass

                elif isinstance(p, PlatformHurt):
                    self.is_flying = False
                    self.last_fly_time = 0
                    SOUND_HURT1.stop()
                    SOUND_HURT2.stop()
                    SOUND_LIFE.stop()
                    self.groundSpeed = 0
                    if self.hp == 3:
                        SOUND_HURT1.play()
                    if self.hp == 2:
                        SOUND_HURT2.play()
                    if elapsed_time(self.last_hurt_time) > BANDAID_TIME:
                        self.hp -= 1
                        self.last_hurt_time = current_time()
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = -6.0
                        my_print("collide left")
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 6.0
                        my_print("collide right")
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 6.0
                        my_print("collide bottom")
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = False
                        self.yvel = -6.0
                        self.last_bounce_time = current_time()
                        my_print("collide top")

                elif isinstance(p, PlatformHurtFull):
                    self.is_flying = False
                    self.last_fly_time = 0
                    SOUND_HURT1.stop()
                    SOUND_HURT2.stop()
                    SOUND_LIFE.stop()
                    self.groundSpeed = 0
                    if self.hp == 3:
                        SOUND_HURT1.play()
                    if self.hp == 2:
                        SOUND_HURT2.play()
                    if elapsed_time(self.last_hurt_time) > BANDAID_TIME:
                        self.hp -= 1
                        self.last_hurt_time = current_time()
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        my_print("collide left")
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        my_print("collide right")
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        my_print("collide bottom")
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = False
                        self.yvel = -6.0
                        my_print("collide top")

                elif isinstance(p, PlatformPit):
                    self.lives -= 1
                    self.hp = NUM_HP
                    self.groundSpeed = 0
                    self.reset_position(32, 32)
                    self.running_level = False
                    SOUND_PIT_DIE.play()

                elif isinstance(p, PlatformLife):
                    self.groundSpeed = 0
                    self.last_hurt_time = current_time() - 10.0
                    if self.hp < NUM_HP:
                        SOUND_HURT1.stop()
                        SOUND_HURT2.stop()
                        SOUND_LIFE.stop()
                        SOUND_LIFE.play()
                    self.hp = NUM_HP
                    my_print("Healed: HP = {}".format(self.hp))
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = 0
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0

                elif isinstance(p, Platformmovingcarpetleft):
                    my_print("Left carpet: ")
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = 0
                        my_print("collide right")
                        self.groundSpeed = 0
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 0
                        my_print("collide left")
                        self.groundSpeed = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                        my_print("collide bottom")
                        self.groundSpeed = 0
                    if yvel > 0:
                        self.onGround = True
                        self.yvel = 0
                        self.rect.bottom = p.rect.top
                        self.groundSpeed = -7
                        my_print("collide top")

                elif isinstance(p, Platformmovingcarpetright):
                    my_print("Right carpet: ")
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = 0
                        my_print("collide right")
                        self.groundSpeed = 0
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 0
                        my_print("collide left")
                        self.groundSpeed = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                        my_print("collide bottom")
                        self.groundSpeed = 0
                    if yvel > 0:
                        self.onGround = True
                        self.yvel = 0
                        self.rect.bottom = p.rect.top
                        self.groundSpeed = 7
                        my_print("collide top")

                elif isinstance(p, PlatformSticky):
                    my_print("Sticky: ")
                    self.groundSpeed = 0
                    self.onGround = True
                    self.onSticky = True

                    # See if only collided/overlapped by 1
                    if self.rect.right == p.rect.left + 1 or self.rect.left == p.rect.right - 1 \
                            or self.rect.top == p.rect.bottom - 1 or self.rect.bottom == p.rect.top + 1:

                        pass

                        # Determine if we are on the top or, say, a side. Only allow side movement when checking
                        # collisions based on the yvel (not when checking horizontal)
                        # if self.rect.bottom != p.rect.top + 1 and yvel != 0.0:
                        #     self.yvel = 0.0

                        # if xvel != 0 and self.rect.top == p.rect.bottom - 1:
                        #     print "Hit the clause"

                    else:
                        if xvel > 0:
                            self.rect.right = p.rect.left + 1
                            my_print("collide right")
                            # self.yvel = 0.0
                            self.xvel = 0.0
                        if xvel < 0:
                            self.rect.left = p.rect.right - 1
                            my_print("collide left")
                            # self.yvel = 0.0
                            self.xvel = 0.0
                        if yvel < 0:
                            self.rect.top = p.rect.bottom - 1
                            self.yvel = 0.0
                            my_print("collide bottom")
                        if yvel > 0:
                            self.rect.bottom = p.rect.top + 1
                            self.yvel = 0.0
                            my_print("collide top")

                else:  # Must be a normal platform
                    my_print("Platform: ")
                    self.groundSpeed = 0
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = 0
                        my_print("collide right")
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = 0
                        my_print("collide left")
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0
                        my_print("collide top")
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0


class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#888888"))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y


class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.color = Color("#DD33FF")
        self.other_colors = [RED, YELLOW, LIMEGREEN, BLUE]
        self.image.fill(Color("#DD33FF"))
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        # CHANGE pulse time to change width of color band. Change pulse start time to change speed of transition.
        use_color = get_pulse_color([self.color] + self.other_colors, pulse_time=0.5, pulse_start_time=-self.x / 64)
        self.image.fill(Color(*use_color))


class FakeExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.color = Color("#DD33FF")
        self.other_colors = [DARKRED, BYELLOW, DARKGREEN]
        self.image.fill(Color("#DD33FF"))
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        # CHANGE pulse time to change width of color band. Change pulse start time to change speed of transition.
        use_color = get_pulse_color([self.color] + self.other_colors, pulse_time=1.0, pulse_start_time=-self.x / 64)
        self.image.fill(Color(*use_color))


class PlatformIllusion(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#898989"))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y


class PlatformGlass(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(LIGHTBLUE)
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y


class PlatformFly(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(DARKGREEN)
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y


class PlatformBouncy1(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#5533FF"))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y


class PlatformHurt(Platform):
    def __init__(self, x, y):
        dip_height = 10
        Entity.__init__(self)
        self.color = RED
        self.other_color = DARKERRED
        self.image = Surface((32, 32 - dip_height))
        self.image.convert()
        self.image.fill(Color(*self.color))
        self.rect = Rect(x, y + dip_height, 32, 32 - dip_height)
        self.x = x
        self.y = y + dip_height

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        # CHANGE pulse time to change width of color band. Change pulse start time to change speed of transition.
        use_color = get_pulse_color([self.color, self.other_color], pulse_time=4.0, pulse_start_time=self.y / 128.0)
        self.image.fill(Color(*use_color))


class PlatformHurtFull(PlatformHurt):
    def __init__(self, x, y):
        self.color = RED
        self.other_color = DARKERRED
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#FF0000"))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y


class PlatformPit(Platform):
    def __init__(self, x, y):
        dip_height = 8
        Entity.__init__(self)
        self.image = Surface((32, 32 - dip_height))
        self.image.convert()
        self.image.fill(Color(0, 0, 0))
        self.rect = Rect(x, y + dip_height, 32, 32 - dip_height)
        self.x = x
        self.y = y + dip_height


class PlatformLife(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.color = LIFECOLOR
        self.other_color = BYELLOW
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color(*self.color))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        # CHANGE pulse time to change width of color band. Change pulse start time to change speed of transition.
        use_color = get_pulse_color([self.color, self.other_color], pulse_time=2.0)
        self.image.fill(Color(*use_color))


class PlatformSticky(Platform):
    def __init__(self, x, y):
        extra = 1
        Entity.__init__(self)
        self.image = Surface((32 + 2 * extra, 32 + 2 * extra))
        self.image.convert()
        self.image.fill(Color(128, 128, 0))
        self.rect = Rect(x - extra, y - extra, 32 + 2 * extra, 32 + 2 * extra)
        self.x = x - extra
        self.y = y - extra


class Platformmovingcarpetleft(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.color = LIGHTBLUE
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color(*self.color))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        # CHANGE pulse time to change width of color band. Change pulse start time to change speed of transition.
        use_color = get_pulse_color([self.color, LIGHTGRAY], pulse_time=2.0, pulse_start_time=-self.x / 256.0)
        self.image.fill(Color(*use_color))


class Platformmovingcarpetright(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.color = (255, 0, 255)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color(*self.color))
        self.rect = Rect(x, y, 32, 32)
        self.x = x
        self.y = y

    def update(self, camera_x, camera_y):
        self.rect.x = self.x - camera_x
        self.rect.y = self.y - camera_y
        use_color = get_pulse_color([self.color, LIGHTGRAY], pulse_time=2.0, pulse_start_time=self.x / 256.0)
        self.image.fill(Color(*use_color))


########################
# Helper Functions
########################


def end_message(message_life, message_big, message_small, timer, screen, bg, num_hp):
    time_to_exit = False
    while not time_to_exit:
        timer.tick(60)
        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        # entities.draw(screen)
        draw_life_message(message_life, color=BLUE, pulse_time=1.5)
        draw_hp(num_hp)
        draw_big_message(message_big)
        draw_small_message(message_small)
        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit
            elif e.type == KEYDOWN and e.key == K_SPACE:
                time_to_exit = True

        pygame.display.update()


def draw_big_message(message, color=BLUE, pulse_time=8.0, height=HALF_HEIGHT - 25):
    use_color = get_pulse_color([color, GREEN], pulse_time=pulse_time)

    proposed_size = 50 * 28 / len(message)
    font_size = min(50, proposed_size)

    if message is not None:
        font = pygame.font.Font('freesansbold.ttf', int(font_size))
        surf = font.render(message, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (HALF_WIDTH, height)
        DISPLAYSURF.blit(surf, rect)


def draw_life_message(message_life, color=RED, pulse_time=8.0):
    use_color = get_pulse_color([color, DARKRED], pulse_time=pulse_time)

    if message_life is not None:
        font = pygame.font.Font('freesansbold.ttf', 15)
        surf = font.render(message_life, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (WIN_WIDTH - WIN_WIDTH + 50, WIN_HEIGHT - WIN_HEIGHT + 10)
        DISPLAYSURF.blit(surf, rect)


def draw_hp(num_hp):
    pulse_time = 8.0
    use_color = get_pulse_color([LIMEGREEN, DARKGREEN], pulse_time=pulse_time)

    for ii in range(num_hp):
        pygame.draw.rect(DISPLAYSURF, use_color, (3 * DEPTH + ii * (DEPTH / 2 + 2), DEPTH / 4, DEPTH / 2, DEPTH / 2))


def die_message(message_die, screen, timer, bg):
    message_small = ["Press spacebar to continue"]
    time_to_exit = False
    while not time_to_exit:
        timer.tick(60)
        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        draw_life_message(message_life2, color=RED, pulse_time=1.0)
        draw_small_message(message_small, color=BLUE, pulse_time=1.0)
        draw_die_message(message_die)
        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit
            elif e.type == KEYDOWN and e.key == K_SPACE:
                time_to_exit = True

        pygame.display.update()


def draw_time_message(message_time, color=RED, pulse_time=8.0):
    use_color = get_pulse_color([color, DARKRED], pulse_time=pulse_time)

    if message_time is not None:
        font = pygame.font.Font('freesansbold.ttf', 15)
        surf = font.render(message_time, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (WIN_WIDTH - 50, WIN_HEIGHT - WIN_HEIGHT + 10)
        DISPLAYSURF.blit(surf, rect)


def draw_die_message(message_time, color=DARKERRED, pulse_time=8.0):
    use_color = get_pulse_color([color, DARKGREEN], pulse_time=pulse_time)

    if message_time is not None:
        font = pygame.font.Font('freesansbold.ttf', 50)
        surf = font.render(message_time, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (HALF_WIDTH, HALF_HEIGHT - 25)
        DISPLAYSURF.blit(surf, rect)


def instructions_message():
    global TIMER, DISPLAYSURF

    message_big = "Little Square, Long Journey"
    message_instructions = ["How to Play:",
                            '* Use arrow keys to move',
                            '* Tap up or space to jump small',
                            '* Hold up or space to jump big',
                            '* You can press multiple keys at a time'
                            ]
    message_small_2 = ["Press spacebar to continue",
                       "Good luck to you!",
                       ]

    time_to_exit = False
    while not time_to_exit:
        TIMER.tick(60)
        DISPLAYSURF.fill(0x000000)

        draw_big_message(message_big, color=GOLD, pulse_time=2.0, height=WIN_HEIGHT / 4)
        draw_small_message(message_instructions, color=DARKRED, start_height=WIN_HEIGHT / 4 + 100)
        draw_small_message(message_small_2, start_height=WIN_HEIGHT / 2 + 100)

        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit
            elif e.type == KEYDOWN and e.key == K_SPACE:
                time_to_exit = True

        pygame.display.update()


def draw_end_message(message_die, color=DARKERRED, pulse_time=4.0):
    use_color = get_pulse_color([color, DARKGREEN], pulse_time=pulse_time)

    if message_die is not None:
        font = pygame.font.Font('freesansbold.ttf', 50)
        surf = font.render(message_die, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (HALF_WIDTH, HALF_HEIGHT - 25)
        DISPLAYSURF.blit(surf, rect)


def end_game_message(screen, timer, bg):
    message_end = 'Game Over!'
    message_small = ["Uh, Oh",
                     "You ran out of lives",
                     "Press spacebar to restart",
                     "Press escape to quit"]
    time_to_exit = False
    while not time_to_exit:
        timer.tick(60)
        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        draw_life_message(message_life2, color=RED, pulse_time=1.0)
        draw_small_message(message_small, color=BLUE, pulse_time=1.0)
        draw_end_message(message_end, color=RED, pulse_time=1.0)
        for e in pygame.event.get():
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit
            elif e.type == KEYDOWN and e.key == K_SPACE:
                time_to_exit = True

        pygame.display.update()


def draw_prompt_message(message_prompt, color=BLUE, pulse_time=8.0):
    use_color = get_pulse_color([color, DARKGREEN], pulse_time=pulse_time)

    if message_prompt is not None:
        font = pygame.font.Font('freesansbold.ttf', 15)
        surf = font.render(message_prompt, True, use_color)
        rect = surf.get_rect()
        rect.midtop = (HALF_WIDTH, WIN_HEIGHT - 25)
        DISPLAYSURF.blit(surf, rect)


def draw_small_message(message_list, color=BLUE, pulse_time=8.0, start_height=HALF_HEIGHT + 50, font_size=25):
    use_color = get_pulse_color([color, GREEN], pulse_time=pulse_time)

    for m, message in enumerate(message_list):
        if message is not None:
            font = pygame.font.Font('freesansbold.ttf', int(font_size))
            surf = font.render(message, True, use_color)
            rect = surf.get_rect()
            rect.midtop = (HALF_WIDTH, start_height + (m * int(font_size)))
            DISPLAYSURF.blit(surf, rect)


def get_pulse_color(colors, pulse_time=2.0, pulse_start_time=0.0):
    num_colors = len(colors)
    one_color_time = pulse_time / num_colors

    mod_time = ((current_time() - pulse_start_time) % pulse_time)
    norm_time = mod_time / one_color_time
    ix1 = int(norm_time)
    ix2 = (ix1 + 1) % num_colors
    fraction = norm_time - ix1

    use_color = list(colors[0])
    for ii in range(3):
        use_color[ii] = int((1.0 - fraction) * float(colors[ix1][ii]) + fraction * float(colors[ix2][ii]))

    use_color = tuple(use_color)
    return use_color


def terminate():
    pygame.quit()
    sys.exit()


def check_for_key_press():
    for event in pygame.event.get():
        if event.type == QUIT:  # event is quit
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # event is escape key
                terminate()
            else:
                return event.key  # key found return with it
    # no quit or key events in queue so return None
    return None


def level_pack_choice_screen():
    global TIMER, DISPLAYSURF

    level_choice_messages = [
        "1: Lincoln's Intro",
        "2: Lincoln's Intermediate",
        "3: Lincoln's Expert",
        "4: Dad's",
        "5: Cora's",
    ]

    pygame.event.get()  # clear out event queue

    while True:
        DISPLAYSURF.fill(0x000000)
        draw_big_message('Which level pack?', height=WIN_HEIGHT / 4)
        draw_small_message(level_choice_messages, start_height=WIN_HEIGHT / 2)

        #
        pygame.display.update()

        key = check_for_key_press()
        if key:
            if key == K_1:
                return levels_intro.levels
            elif key == K_2:
                return levels_intermediate.levels
            elif key == K_3:
                return levels_expert.levels
            elif key == K_4:
                return levels_dad.levels
            elif key == K_5:
                return levels_cora.levels

        TIMER.tick(60)


def level_num_choice_screen(levels):
    global TIMER

    pygame.event.get()  # clear out event queue
    num_levels = len(levels)

    level_names = ['{}: {}'.format(ii + 1, l.name) for ii, l in enumerate(levels)]
    level_names = ['Enter number and hit return', ''] + level_names

    entered_number_string = ''
    small_font_size = min(25, int(25 * 17 / num_levels))  # Shrink the font as needed so they fit.
    while True:
        DISPLAYSURF.fill(0x000000)
        draw_big_message('Which level in the pack?', height=HALF_HEIGHT / 5)
        draw_small_message(level_names, start_height=HALF_HEIGHT / 4 + 50, font_size=small_font_size)

        pygame.display.update()

        key = check_for_key_press()
        if key:
            if K_0 <= key <= K_9:
                entered_number_string += str(key - K_0)
            elif key == K_BACKSPACE:
                entered_number_string = entered_number_string[0:-1]
            elif key == K_RETURN:
                if len(entered_number_string) == 0:
                    level_choice = 1
                else:
                    level_choice = int(entered_number_string)

                if 1 <= level_choice <= num_levels:
                    return level_choice - 1
                else:
                    entered_number_string = ''

        TIMER.tick(60)


if __name__ == "__main__":
    main()
