import pygame, math, random, engine

class GarmentColor:
    lights = {
        'shirt': [
            'light_shirt01.bmp',
            'light_shirt03.bmp'
            ],
        'pants': [
            'light_pants01.bmp',
            'light_pants02.bmp',
            'light_shorts01.bmp',
            'light_skirt01.bmp'
            ],
        'sock': [ 
            'light_socks01.bmp',
            'light_socks03.bmp',
            'light_socks04.bmp',
            'light_socks05.bmp'
            ],
        'undies': [ 
            'light_bra01.bmp',
            'light_bra02.bmp', 
            'light_briefs01.bmp',
            'light_briefs02.bmp'
            ]
    }

    darks = {
        'shirt': [
            "dark_shirt01.bmp",
            "dark_shirt02.bmp",
            "dark_shirt03.bmp",
            "dark_shirt04.bmp",
            "dark_shirt05.bmp",
            "dark_shirt06.bmp",
            "dark_shirt07.bmp",
            "dark_shirt08.bmp",
            "dark_shirt09.bmp",
        ],
        'pants': [
            "dark_pants01.bmp",
            "dark_pants02.bmp",
            "dark_shorts01.bmp",
            "dark_shorts02.bmp",
            "dark_skirt01.bmp",
            "dark_skirt02.bmp",
        ],
        'sock': [
            "dark_socks01.bmp",
            "dark_socks02.bmp",
            "dark_socks03.bmp",
            "dark_socks04.bmp",
            "dark_socks05.bmp",
        ],
        'undies': [
            "dark_bra01.bmp",
            "dark_briefs01.bmp",
            "dark_thong01.bmp",
            "dark_thong02.bmp",
            "dark_thong03.bmp",
        ],
    }

class Garment:
    def __init__(self, kernel, screen, garment_type, biohazard, coins, color_cat):
        self.kernel = kernel
        self.screen = screen

        # Initialize our various properties
        # Image Stuff
        self.image_choices = {
            'shirt': [ "shirt1.bmp" ],
            'pants': [ "pants1.bmp" ],
            'sock': [ "sock1.bmp" ],
            'undies': [ "undies1.bmp" ] 
        }

        self.stink_image, self.stink_rect = kernel.image_manager.load("stinks.bmp", True)

        # Random Color
        self.color_cat = color_cat

        if color_cat == 'lights':
            self.image_name = random.choice(GarmentColor.lights[garment_type])
        else:
            self.image_name = random.choice(GarmentColor.darks[garment_type])

        self.type = garment_type
        self.biohazard = biohazard
        self.coinage = coins

        # Properties Go Here
        self.position = [400, 75]

        self.falling = True
        self.gravity = 0.05
        self.velocity = 0

        self.image, self.rect = kernel.image_manager.load(self.image_name, True)
        self.rect.center = self.position

    def pick_up(self):
        self.falling = False
        self.velocity = 0

    def put_down(self):
        self.falling = True

    def shake(self):
        # Drop some coins if we so care to here
        if self.coinage:
            self.screen.coins.extend([ Coin(self.kernel, self.screen, self.position) for x in range(self.coinage) ])
            self.screen.coin_total += self.coinage
            self.coinage = 0

    def update(self, delta):
        # Update our position if we're falling
        if self.falling:
            self.velocity += self.gravity
            self.position[1] += self.velocity

        if self.position[1] > 600:
            self.screen.garments.remove(self)

    def draw(self, surface):
        if self.image and self.rect:
            # Position the rectangle for correct drawing
            self.rect.center = self.position
            
            self.stink_rect.center = self.position
            self.stink_rect.top = self.stink_rect.top - 20

            surface.blit(self.image, self.rect)

            if self.biohazard:
                surface.blit(self.stink_image, self.stink_rect)


class GarmentRandomizer:
    def __init__(self, kernel, screen):
        self.kernel = kernel
        self.screen = screen
        self.weights = {'pants': 20, 'shirt': 30, 'sock': 25, 'undies': 25 }
        self.choice_list = []

        for item, weight in self.weights.iteritems():
            self.choice_list.extend([item] * weight)

    def next(self):
        garment_choice = random.choice(self.choice_list)
        garment_color = random.choice(['lights', 'darks'])

        # Choose if Biohazard
        if garment_choice == 'undies':
            biohazard_choice = (random.randint(0, 99) < 70)
        elif garment_choice == 'sock':
            biohazard_choice = (random.randint(0, 99) < 25)
        else:
            biohazard_choice = False

        # Choose how many coins in pockets
        if garment_choice == 'pants':
            coinage = random.randint(5, 20)
        else: 
            coinage = 0 

        return Garment(self.kernel, self.screen, garment_choice, biohazard_choice, coinage, garment_color)

class Bins:
    def __init__(self, kernel, screen):
        self.kernel = kernel
        self.screen = screen

        self.bins = [
            'lights',
            'darks',
            'biohazard'
        ]

        light_icon, light_rect = kernel.image_manager.load("icon_light.bmp", True)
        dark_icon, dark_rect = kernel.image_manager.load("icon_dark.bmp", True)
        biohazard_icon, biohazard_rect = kernel.image_manager.load("icon_biohazard.bmp", True)

        self.bin_icons = {
            'lights': light_icon,
            'darks': dark_icon,
            'biohazard': biohazard_icon
        }

        self.bin_image, self.bin_image_rect = kernel.image_manager.load("bins.bmp", True)
        self.bin_image_rect.left = 100

        self.bin_icon_rects = [
            pygame.Rect(190, 345, light_rect.width, light_rect.height),
            pygame.Rect(350, 320, light_rect.width, light_rect.height),
            pygame.Rect(500, 350, light_rect.width, light_rect.height)
        ]

        self.bin_rects = [
            pygame.Rect(100, 475, 184, 100),
            pygame.Rect(286, 475, 192, 100),
            pygame.Rect(480, 475, 190, 100)
        ]

        # How long we've stayed in position
        self.ticks = 0
        self.randomize_time = 15000
        self.move_counter = 0

        self.y_position = 500

    def spin(self):
        # Randomize the order of the bins
        random.shuffle(self.bins)
        self.screen.add_scores()

    def garment_check(self, garment):
        for (bin, rect) in zip(self.bins, self.bin_rects):
            if rect.collidepoint((garment.rect.center[0], garment.rect.bottom)):
                return bin

        return None

    def update(self, delta):
        self.ticks += delta

        if self.ticks >= self.randomize_time and not self.screen.current_garment:
            max_counter = 20

            t = (self.move_counter / float(max_counter)) * math.pi

            # We need to know what the max value we're going to get is in order
            # for us to scale the movement function between 0 and 1
            midpoint = (((max_counter / 2) - 1) / float(max_counter)) * math.pi

            # Make sure we avoid the asymptote for position updating
            if t != (math.pi / 2):
                movement = math.tan(t) / math.tan(midpoint)
                self.y_position += 100 * movement

            # Spin our bins when we're off the bottom of the screen
            if self.move_counter == max_counter / 2:
                self.spin()

            # Make sure we reset the bin when we're done
            if self.move_counter >= max_counter:
                self.move_counter = 0
                self.ticks = 0

            self.move_counter += 1

    def draw(self, surface):
        self.bin_image_rect.top = self.y_position - 100

        surface.blit(self.bin_image, self.bin_image_rect)

        for bin, rect, icon_rect in zip(self.bins, self.bin_rects, self.bin_icon_rects):
            bin_icon = self.bin_icons[bin]
            surface.blit(bin_icon, icon_rect)

        for rect in self.bin_rects:
            rect.top = self.y_position


class Coin:
    def __init__(self, kernel, screen, start_position):
        self.kernel = kernel
        self.screen = screen

        coin_images = [
            "coin01.bmp",
            "coin02.bmp"
        ]

        self.image, self.rect = kernel.image_manager.load(random.choice(coin_images), True)

        self.gravity = 0.5
        self.velocity = [ random.randint(-5, 5), -10 - random.randint(0, 5) ]
        self.position = [ start_position[0], start_position[1] ]

    def update(self, delta):
        self.velocity[1] += self.gravity

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        if self.position[1] >= 650:
            self.screen.coins.remove(self)

    def draw(self, surface):
        self.rect.center = self.position

        surface.blit(self.image, self.rect)
