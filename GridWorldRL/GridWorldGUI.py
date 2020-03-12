import pygame as pg
from GridWorldTestbed import World

### TESTING/DEBUG IMAGE FILE NAME ###
filepath = '/home/mitchell/Desktop/Dynamic_Fear_Reponse_for_Colony_Foraging/GridWorldRL/images/'
imagename = 'testmap'
fileext = '.png'
filename = filepath + imagename + fileext
### 

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
AGENTCOLOUR = (0, 0, 255)

class Application:
    def __init__(self, filename, rounds, w=800, h=600):
        pg.init()
        self.display_width = w
        self.display_height = h
        self.display = pg.display.set_mode((self.display_width, self.display_height))
        self.clock = pg.time.Clock()
        self.crashed = False
        self.topleft_x = w * 0.1
        self.topleft_y = h * 0.1

        self.pixels = self.getPixelArray(filename)

        pg.display.set_caption('Grid World')

        self.worldstates = self.world_init(filename, rounds)

    def world_init(self, filename, rounds):
        world = World(filename)
        worldstates = world.run(rounds)
        return worldstates

    # Takes pixel array as input
    def mapper(self, x, y, pxlArray):
        img = pg.surfarray.make_surface(pxlArray)
        img = pg.transform.scale(img, (448, 448))
        self.display.blit(img, (x, y))
    
    def getPixelArray(self, filename):
        """ Convert image to pixel array """
        try:
            image = pg.image.load(filename)
        except (pg.error, message):
            print ("Cannot load image:", filename)
            raise (SystemExit, message)
        
        return pg.surfarray.array3d(image)
    
    # Save image after changes to pixels
    def saveSurface(self, pixels, filename):
        try:
            surf = pg.surfarray.make_surface(pixels)
        except (IndexError):
            (width, height, colours) = pixels.shape
            surf = pg.display.set_mode((width, height))
            pg.surfarray.blit_array(surf, pixels)
        
        pg.image.save(surf, filename)
    
    def run(self, debug=False):
        currStep = 0
        roundnum = 1
        if debug:
            print(len(self.worldstates))
            for i in range(len(self.worldstates)):
                print("Number of steps in round ", i, ": ", len(self.worldstates[i]))
        print("Round: 0")
        while not self.crashed:
            
            nextStep = currStep + 1

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.crashed = True
                    
            
            self.display.fill(BLACK)
            # Replay all of the rounds at the same time using different shades of blue for each round
            
            if roundnum < len(self.worldstates):
                if nextStep < len(self.worldstates[roundnum]):
                    
                    currpos = self.worldstates[roundnum][currStep][0]
                    nextpos = self.worldstates[roundnum][nextStep][0]
                    if not currStep == 0:
                        self.pixels[currpos[0], currpos[1]] = WHITE
                        self.pixels[nextpos[0], nextpos[1]] = AGENTCOLOUR
                    else:
                        self.pixels[currpos[0], currpos[1]] = RED
                else:
                    roundnum += 1
                    print("Round:", roundnum)


            self.mapper(self.topleft_x, self.topleft_y, self.pixels)
            pg.display.update()
            self.clock.tick(60)
            currStep += 1
        
        print("Game has finished.")
        #save = 1 if input("Save map? [y/n] ") == "y" else 0
        save = False
        if save:
            filesavename = filepath + filename + "test" + fileext
            self.saveSurface(self.pixels, filesavename)
            print("Image has been saved to: " + filesavename)
        else:
            print("Goodbye!")
        pg.quit()

def main():
    app = Application(filename, rounds=20)
    app.run(True)

    quit()

if __name__ == '__main__':
    main()







