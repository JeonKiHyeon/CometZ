"""
    core.py - all the menu, game, gameOver, etc. event handling, logic and 
              drawing comes here
    
    ---------------------------------------------------------------------------
    
    Copyright 2014 Alexandre Lopes <aalopes@ovi.com>
    
    This file is part of CometZ.

    CometZ is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CometZ is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CometZ.  If not, see <http://www.gnu.org/licenses/>.
    
    ---------------------------------------------------------------------------
"""

import pygame,sys
import pickle
from pygame.locals import *
from constants     import *
from player        import *
from enemies       import *
from background    import Background
from random        import randint
from powerUps      import Health25, Health100
from menu          import Menu
from credits       import Credits
from volume        import Volume

class Game():

    def __init__(self):

        # variables -----------------------------------------------

        # load background
        self.backg = Background(BKG_FOLDER + "stars.png")
        
        # set initial score
        self.score = 0
        
        # load sound and music volume from file
        # if there's a problem with the file, simply create a new one with default values
        try:
            volume = pickle.load( open( "volume.p", "rb" ) )
        except:
            volume = { "sound": 100, "music": 30 }
            pickle.dump( volume, open( "volume.p", "wb" ) )

        # sounds
        self.laserSnd   = pygame.mixer.Sound(SND_FOLDER + "laser.wav")
        self.explodeSnd = pygame.mixer.Sound(SND_FOLDER + "explosion.wav")    
        self.powerUpSnd = pygame.mixer.Sound(SND_FOLDER + "powerUp.wav")
        
        # put everything into a list so it's easier to change the volume
        # the list elements are the same objects as the initial ones
        # as python copies by reference and not by value (I would have
        # preferred to use pointers, to avoid ambiguity, but oh well...)
        self.sounds = [self.laserSnd,self.explodeSnd,self.powerUpSnd]       

        # set volume for all sound objects                
        for snd in self.sounds:
            snd.set_volume(volume["sound"]/100.) # set new volume
        
        # music
        self.music = pygame.mixer.music.load(MUS_FOLDER + "reachingForTheSun.mp3")
        pygame.mixer.music.play(-1) # loop
        pygame.mixer.music.set_volume(volume["music"]/100.)
        
        # creating user ship
        self.userShip1 = ShipY001()
        self.userShip2 = ShipY002()
        self.userShip3 = ShipY003()
        self.userShip1.speed = 10
        self.userShip2.speed = 10
        self.userShip3.speed = 10
        # group of all sprites
        self.userSprites1    = pygame.sprite.Group()
        self.userSprites2    = pygame.sprite.Group()
        self.userSprites3    = pygame.sprite.Group()
        self.laserSprites   = pygame.sprite.Group()
        self.aiSprites      = pygame.sprite.Group()
        self.powerUpSprites = pygame.sprite.Group()
        
        
        # add to groups
        self.userSprites1.add(self.userShip1)
        self.userSprites2.add(self.userShip2)
        self.userSprites3.add(self.userShip3)

        # Creating main menu
        self.menu = Menu(["Quit","Credits","Volume","Play"],self.backg)

        # Creating game_mode
        self.mode = Menu(["HELL","HARD","NORMAL"],self.backg)
        self.modeBack = 0
        
        # Creating pause menu (could be generated later, but shouldn't impact performance)
        self.pause = Menu(["Quit","Volume","Restart","Continue"],self.backg)
        
        # Creating volume menu (could be generated later, but shouldn't impact performance)
        self.volume = Volume(self.backg,volume)
        self.volumeBack = 0 # some stupid flag to tell us whether we came from the main menu
                            # of from the pause menu 

        
        # Creating credits
        self.credits = Credits(["Sound: Obtained from Freesound",
                       "Music: 'Reaching for the Sun' by Deshiel and Bacon92",
                       "Graphics: Filipa Silva",
                       "Code: Alexandre Lopes"],
                       self.backg)
        
        # gameState
        # Available states: menu, credits ,game, gameOver
        self.gameState = "menu"
        
        # -----------------------------------------------
        
    def handle(self,event):
    
        # some flags (this could be re-done in a better way, but for now it works)
        wasPressedNow = 0 # this is for some stupid hack, see below
        # Menu ===============================================================
        if self.gameState == "menu":
        
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.menu.press() == 3:     # play pressed
                        self.gameState = "mode"    # show mode
                        wasPressedNow = 1
                    elif self.menu.press() == 2:   # volume pressed
                        self.gameState = "volume"  # show volume menu
                        wasPressedNow = 1
                        self.volumeBack = 1
                    elif self.menu.press() == 1:   # credits pressed
                        self.gameState = "credits" # show credits
                        wasPressedNow = 1 # stupid hack to prevent event from being
                                          # read here and in the credits
                                          # probably the best solution would be to change
                                          # the way everything is structured
                                          # but this proved to be easier
                    elif self.menu.press() == 0: # quit pressed
                        pygame.quit()
                        sys.exit()
                    else:
                        pass # throw exception
                if event.key == pygame.K_DOWN:
                    self.menu.down()
                if event.key == pygame.K_UP:
                    self.menu.up()
        #  mode===================================================================
        if self.gameState == "mode" and wasPressedNow == 0:
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.mode.press() == 2:
                        self.modeBack = 0
                        print(self.modeBack)
                        self.gameState = "game_Normal"
                    elif self.mode.press() == 1:
                        self.modeBack = 1
                        self.gameState = "game_Hard"
                    elif self.mode.press() == 0:
                        self.modeBack = 2
                        self.gameState ="game_Hell"
                    else:
                        pass
                if event.key == pygame.K_DOWN:
                    self.mode.down()
                if event.key == pygame.K_UP:
                    self.mode.up()
        
        # Pause===============================================================
        if self.gameState == "pause":
        
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.pause.press() == 3:   # continue pressed
                        if self.modeBack == 0:
                            self.gameState = "game_Normal"   
                        elif self.modeBack == 1:
                            self.gameState = "game_Hard"
                        elif self.modeBack == 2:
                            self.gameState = "game_Hell"
                    elif self.pause.press() == 2:               
                        self.__init__()
                        if self.modeBack == 0:
                            self.gameState = "game_Normal"   
                        elif self.modeBack == 1:
                            self.gameState = "game_Hard"
                        elif self.modeBack == 2:
                            self.gameState = "game_Hell"
                                           
                    elif self.pause.press() == 1:                     
                        self.gameState = "volume"                        
                        self.volumeBack = 0
                        wasPressedNow = 1
                    elif self.pause.press() == 0: # quit pressed
                        pygame.quit()
                        sys.exit()
                    else:
                        pass # throw exception
                if event.key == pygame.K_DOWN:
                    self.pause.down()
                if event.key == pygame.K_UP:
                    self.pause.up()
        #  ===================================================================
         
        # Volume =============================================================
        if self.gameState == "volume" and wasPressedNow == 0:
        
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.volume.press() == 0:     # back pressed
                        if self.volumeBack == 1:      # then we should go back to menu
                            self.gameState = "menu"
                        elif self.volumeBack == 0:    # then we should go back to the pause menu
                            self.gameState = "pause"
                    else:
                        pass # throw exception
                # move "cursor" down
                if event.key == pygame.K_DOWN:
                    self.volume.down()
                # move "cursor" up
                if event.key == pygame.K_UP:
                    self.volume.up()
                    
                # raise music volume if it is selected
                if event.key == pygame.K_RIGHT and self.volume.press() == 2:
                    pygame.mixer.music.set_volume(self.volume.right()) # update volume
                    
                    # newVolume = pygame.mixer.music.get_volume() + .1 # get current volume and increment
                    # if newVolume > 1.:    # if it exceeds the maximum
                        # newVolume = 1.
                    # pygame.mixer.music.set_volume(newVolume)
                    # #save new volume to file
                    # pickle.dump( {"sound": self.sounds[0].get_volume(), 
                                  # "music": pygame.mixer.music.get_volume()}, 
                                  # open( "volume.p", "wb" ) )
                                  
                # lower music volume if it is selected
                if event.key == pygame.K_LEFT and self.volume.press() == 2:
                    pygame.mixer.music.set_volume(self.volume.left()) # update volume
                    
                    # if newVolume < 0.:    # if it exceeds the maximum
                        # newVolume = 0.
                    # pygame.mixer.music.set_volume(newVolume)
                    # # save new volume to file
                    # pickle.dump( {"sound": self.sounds[0].get_volume(), 
                                  # "music": pygame.mixer.music.get_volume()}, 
                                  # open( "volume.p", "wb" ) )

                # raise volume if it is selected
                if event.key == pygame.K_RIGHT and self.volume.press() == 1:
                    newVolume = self.volume.right()
                    for snd in self.sounds:
                        snd.set_volume(newVolume) # set new volume
                        
                    # newVolume = self.sounds[0].get_volume() + .1 # get current volume and increment
                    # if newVolume > 1.:    # if it exceeds the maximum
                        # newVolume = 1.
                    # # set now for every sound object we have
                
                    # # save new volume to file
                    # pickle.dump( {"sound": self.sounds[0].get_volume(), 
                                  # "music": pygame.mixer.music.get_volume()}, 
                                  # open( "volume.p", "wb" ) )
                         
                        
                # lower volume if it is selected
                if event.key == pygame.K_LEFT and self.volume.press() == 1:
                    newVolume = self.volume.left()
                    for snd in self.sounds:
                        snd.set_volume(newVolume) # set new volume              
                
                    # newVolume = self.sounds[0].get_volume() - .1 # get current volume and increment
                    # if newVolume < 0.:    # if it exceeds the maximum
                        # newVolume = 0.
                    # # set now for every sound object we have
                    # for snd in self.sounds:
                        # snd.set_volume(newVolume) # set new volume
                    # # save new volume to file
                    # pickle.dump( {"sound": self.sounds[0].get_volume(), 
                                  # "music": pygame.mixer.music.get_volume()}, 
                                  # open( "volume.p", "wb" ) )
                    
        #  ===================================================================
        
        # Credits=============================================================
        if self.gameState == "credits" and wasPressedNow == 0:
        
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.gameState = "menu" # return to menu
                else:
                    pass # throw exception
        #  ===================================================================
        
        # Game ===============================================================
        elif self.gameState == "game_Normal":
            self.modeBack = 0
            if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
            # only on KEYDOWN event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x = self.userShip1.rect.x
                    y = self.userShip1.rect.y
                    self.laserSprites.add(Laser(x+12,y+28))
                    self.laserSnd.play()
                elif event.key == pygame.K_ESCAPE:
                    self.gameState = "pause"
              
        elif self.gameState == "game_Hard":
            self.modeBack = 1
            if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
            # only on KEYDOWN event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x = self.userShip2.rect.x
                    y = self.userShip2.rect.y
                    self.laserSprites.add(Laser(x+12,y+28))
                    self.laserSnd.play()
                elif event.key == pygame.K_ESCAPE:
                    self.gameState = "pause"
                    
        elif self.gameState == "game_Hell":
            self.modeBack = 2
            if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
            # only on KEYDOWN event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x = self.userShip3.rect.x
                    y = self.userShip3.rect.y
                    self.laserSprites.add(Laser(x+12,y+28))
                    self.laserSnd.play()
                elif event.key == pygame.K_ESCAPE:
                    self.gameState = "pause"
         
        #  ===================================================================
        # Game Over ==========================================================

        elif self.gameState == "gameOver":
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # only on KEYDOWN event - restart game with return or quit with escape
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.modeBack == 0:
                        self.__init__()
                        self.gameState = "game_Normal"
                    elif self.modeBack == 1:
                        self.__init__()
                        self.gameState = "game_Hard"
                    elif self.modeBack == 2:
                        self.__init__()
                        self.gameState = "game_Hell"
                        
                elif event.key == pygame.K_ESCAPE:
                    self.__init__()
                    self.gameState = "menu"

        else:
            pass # throw exception!  
        #  ===================================================================

    def keys(self,keys):
        #  Game ==============================================================
    
        if self.gameState == "game_Normal":
            self.modeBack = 0
            if keys[pygame.K_UP]:
                if self.userShip1.rect.y >= 0: 
                    # prevent sprite from leaving window
                    self.userShip1.up()
            if keys[pygame.K_DOWN]:
                if self.userShip1.rect.y + self.userShip1.rect.height <= WINDOW_HEIGHT: 
                    # prevent sprite from leaving window
                    self.userShip1.down()
            if keys[pygame.K_LEFT]:
                if self.userShip1.rect.x >= 0:
                    # prevent sprite from leaving window                    
                    self.userShip1.left()
            if keys[pygame.K_RIGHT]:
                if self.userShip1.rect.x + self.userShip1.rect.width <= WINDOW_WIDTH:
                    # prevent sprite from leaving window
                    self.userShip1.right()
    
        elif self.gameState == "game_Hard":
            self.modeBack = 1
            if keys[pygame.K_UP]:
                if self.userShip2.rect.y >= 0: 
                    # prevent sprite from leaving window
                    self.userShip2.up()
            if keys[pygame.K_DOWN]:
                if self.userShip2.rect.y + self.userShip2.rect.height <= WINDOW_HEIGHT: 
                    # prevent sprite from leaving window
                    self.userShip2.down()
            if keys[pygame.K_LEFT]:
                if self.userShip2.rect.x >= 0:
                    # prevent sprite from leaving window                    
                    self.userShip2.left()
            if keys[pygame.K_RIGHT]:
                if self.userShip2.rect.x + self.userShip2.rect.width <= WINDOW_WIDTH:
                    # prevent sprite from leaving window
                    self.userShip2.right()
    
        elif self.gameState == "game_Hell":
            self.modeBack = 2
            if keys[pygame.K_UP]:
                if self.userShip3.rect.y >= 0: 
                    # prevent sprite from leaving window
                    self.userShip3.up()
            if keys[pygame.K_DOWN]:
                if self.userShip3.rect.y + self.userShip3.rect.height <= WINDOW_HEIGHT: 
                    # prevent sprite from leaving window
                    self.userShip3.down()
            if keys[pygame.K_LEFT]:
                if self.userShip3.rect.x >= 0:
                    # prevent sprite from leaving window                    
                    self.userShip3.left()
            if keys[pygame.K_RIGHT]:
                if self.userShip3.rect.x + self.userShip3.rect.width <= WINDOW_WIDTH:
                    # prevent sprite from leaving window
                    self.userShip3.right()
        #  ===================================================================

    def update(self):
        # Menu ===============================================================
        if self.gameState == "menu":
            pass
        # Mode====================================================================
        if self.gameState == "mode":
            pass
        # Pause ==============================================================
        if self.gameState == "pause":
            pass
        # ====================================================================
        
        # Volume ==============================================================
        if self.gameState == "volume":
            pass
        # ====================================================================
        
        # Credits ============================================================
        if self.gameState == "credits":
            pass
        # ====================================================================
        
        # Game ===============================================================
        if self.gameState == "game_Normal":
            self.modeBack = 0
            # Spawning ====================================================

            # Spawn X001 enemy ships at random in a random y position
            # Probability: 1 in 60 per frame.
            if randint(1,70) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX001(WINDOW_WIDTH, 0,-6)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)
            
            # Spawn X002 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,70) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX002(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)            

            # Spawn X003 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,70) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX003(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.yInitial = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                enemyObj.rect.y   =  enemyObj.yInitial
                self.aiSprites.add(enemyObj)
                # Movement ====================================================
            # Move enemy ships forward according to their speed
            for enemy in self.aiSprites:
                enemy.update()
                
            # Move lasers forward according to their speed
            for laser in self.laserSprites:
                laser.update()
                
            #Move powerUps forward according to their speed
            for powerUp in self.powerUpSprites:
                powerUp.update()
            # =============================================================
            
            # Erasing =====================================================
            # Erase lasers that are out of the screen
            for laser in self.laserSprites:
                if laser.rect.x > WINDOW_WIDTH:
                    self.laserSprites.remove(laser)
                    
            # Erase enemy ships that are out of the screen
            for enemy in self.aiSprites:
                if enemy.rect.x < -10:
                    self.aiSprites.remove(enemy)
                    
            # Erase powerUps that are out of the screen
            for powerUp in self.powerUpSprites:
                if powerUp.rect.x < -10:
                    self.powerUpSprites.remove(powerUp)
            # =============================================================

            # Collisions ==================================================
            
            # check for collisions between user lasers and enemy sprites
            for laser in self.laserSprites:
                enemyHitList = pygame.sprite.spritecollide(laser,self.aiSprites,True) 
                
                # if there was a collision
                if enemyHitList:
                    self.laserSprites.remove(laser)             # remove laser
                    self.explodeSnd.play()
                # iterate over all enemy ships that collided
                for enemy in enemyHitList:
                    thereIsPowerUp = 0 # enemy ship has not spawned power up
                    self.score = self.score + enemy.score # add to score
                    # Spawn Health 25 at random in the place of destroyed enemy ship
                    # Probability: 1 per 50 destroyed enemies
                    if randint(1,50) == 1:
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health25(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                        thereIsPowerUp = 1 # to prevent enemy ship from spawning two powerups
                    # Spawn Health 100 random in the place of destroyed enemy ship
                    # but only if enemy ship has not spawned another powerUp
                    # Probability: 1 per 125 destroyed enemies
                    if randint(1,125) == 1 and thereIsPowerUp != 1: 
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health100(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                                        
                    
            
            # check for collisions between enemyShips and the user
            for enemy in self.aiSprites:
                userHit = pygame.sprite.spritecollide(enemy,self.userSprites1,False,
                                                      pygame.sprite.collide_mask)
                
                # if there was a collision
                if userHit:
                    self.aiSprites.remove(enemy) # remove object
                    self.userShip1.shield -= 25
                    self.score = self.score + enemy.score # add to score
                    self.explodeSnd.play()
                    
            # check for collisions between powerUps and the user
            for powerUp in self.powerUpSprites:
                userHit = pygame.sprite.spritecollide(powerUp,self.userSprites1,False)
                
                # if there was a collision
                if userHit:
                    self.powerUpSprites.remove(powerUp) # remove object
                    powerUp.pickUp(self.userShip1)
                    self.powerUpSnd.play()                # no sound yet!!
            # =============================================================
                    
            # if user is dead
            if self.userShip1.shield <= 0:
                self.userShip1.shield = 0        # round shield to 0
                self.modeBack = 0
                self.gameState = "gameOver"     # change state to gameOver

        elif self.gameState == "game_Hard":
            self.modeBack = 1
            # Spawning ====================================================

            # Spawn X001 enemy ships at random in a random y position
            # Probability: 1 in 60 per frame.
            if randint(1,50) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX001(WINDOW_WIDTH, 0,-6)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)
            
            # Spawn X002 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,50) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX002(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)            

            # Spawn X003 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,50) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX003(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.yInitial = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                enemyObj.rect.y   =  enemyObj.yInitial
                self.aiSprites.add(enemyObj)
           
            # Movement ====================================================
            # Move enemy ships forward according to their speed
            for enemy in self.aiSprites:
                enemy.update()
                
            # Move lasers forward according to their speed
            for laser in self.laserSprites:
                laser.update()
                
            #Move powerUps forward according to their speed
            for powerUp in self.powerUpSprites:
                powerUp.update()
            # =============================================================
            
            # Erasing =====================================================
            # Erase lasers that are out of the screen
            for laser in self.laserSprites:
                if laser.rect.x > WINDOW_WIDTH:
                    self.laserSprites.remove(laser)
                    
            # Erase enemy ships that are out of the screen
            for enemy in self.aiSprites:
                if enemy.rect.x < -10:
                    self.aiSprites.remove(enemy)
                    
            # Erase powerUps that are out of the screen
            for powerUp in self.powerUpSprites:
                if powerUp.rect.x < -10:
                    self.powerUpSprites.remove(powerUp)
            # =============================================================

            # Collisions ==================================================
            
            # check for collisions between user lasers and enemy sprites
            for laser in self.laserSprites:
                enemyHitList = pygame.sprite.spritecollide(laser,self.aiSprites,True) 
                
                # if there was a collision
                if enemyHitList:
                    self.laserSprites.remove(laser)             # remove laser
                    self.explodeSnd.play()
                # iterate over all enemy ships that collided
                for enemy in enemyHitList:
                    thereIsPowerUp = 0 # enemy ship has not spawned power up
                    self.score = self.score + enemy.score # add to score
                    # Spawn Health 25 at random in the place of destroyed enemy ship
                    # Probability: 1 per 50 destroyed enemies
                    if randint(1,50) == 1:
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health25(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                        thereIsPowerUp = 1 # to prevent enemy ship from spawning two powerups
                    # Spawn Health 100 random in the place of destroyed enemy ship
                    # but only if enemy ship has not spawned another powerUp
                    # Probability: 1 per 125 destroyed enemies
                    if randint(1,125) == 1 and thereIsPowerUp != 1: 
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health100(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                                        
                    
            
            # check for collisions between enemyShips and the user
            for enemy in self.aiSprites:
                userHit = pygame.sprite.spritecollide(enemy,self.userSprites2,False,
                                                      pygame.sprite.collide_mask)
                
                # if there was a collision
                if userHit:
                    self.aiSprites.remove(enemy) # remove object
                    self.userShip2.shield -= 50  
                    self.score = self.score + enemy.score # add to score
                    self.explodeSnd.play()
                    
            # check for collisions between powerUps and the user
            for powerUp in self.powerUpSprites:
                userHit = pygame.sprite.spritecollide(powerUp,self.userSprites2,False)
                
                # if there was a collision
                if userHit:
                    self.powerUpSprites.remove(powerUp) # remove object
                    powerUp.pickUp(self.userShip2)
                    self.powerUpSnd.play()                # no sound yet!!
            # =============================================================
                    
            # if user is dead
            if self.userShip2.shield <= 0:
                self.userShip2.shield = 0        # round shield to 0
                self.modeBack = 1
                self.gameState = "gameOver"     # change state to gameOver

        elif self.gameState == "game_Hell":
            self.modeBack = 2
            # Spawning ====================================================

            # Spawn X001 enemy ships at random in a random y position
            # Probability: 1 in 60 per frame.
            if randint(1,20) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX001(WINDOW_WIDTH, 0,-6)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)
            
            # Spawn X002 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,20) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX002(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.rect.y = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                self.aiSprites.add(enemyObj)            

            # Spawn X003 enemy ships at random in a random y position
            # Probability: 1 in 120 per frame. 
            if randint(1,20) == 1:
                # create temporary instance so we can grab the height of the sprite
                enemyObj = EnemyShipX003(WINDOW_WIDTH, 0,-4)
                # random y position on the screen
                enemyObj.yInitial = randint(0, WINDOW_HEIGHT - enemyObj.rect.height)
                enemyObj.rect.y   =  enemyObj.yInitial
                self.aiSprites.add(enemyObj)
                 
            # =============================================================

                
            # Movement ====================================================
            # Move enemy ships forward according to their speed
            for enemy in self.aiSprites:
                enemy.update()
                
            # Move lasers forward according to their speed
            for laser in self.laserSprites:
                laser.update()
                
            #Move powerUps forward according to their speed
            for powerUp in self.powerUpSprites:
                powerUp.update()
            # =============================================================
            
            # Erasing =====================================================
            # Erase lasers that are out of the screen
            for laser in self.laserSprites:
                if laser.rect.x > WINDOW_WIDTH:
                    self.laserSprites.remove(laser)
                    
            # Erase enemy ships that are out of the screen
            for enemy in self.aiSprites:
                if enemy.rect.x < -10:
                    self.aiSprites.remove(enemy)
                    
            # Erase powerUps that are out of the screen
            for powerUp in self.powerUpSprites:
                if powerUp.rect.x < -10:
                    self.powerUpSprites.remove(powerUp)
            # =============================================================

            # Collisions ==================================================
            
            # check for collisions between user lasers and enemy sprites
            for laser in self.laserSprites:
                enemyHitList = pygame.sprite.spritecollide(laser,self.aiSprites,True) 
                
                # if there was a collision
                if enemyHitList:
                    self.laserSprites.remove(laser)             # remove laser
                    self.explodeSnd.play()
                # iterate over all enemy ships that collided
                for enemy in enemyHitList:
                    thereIsPowerUp = 0 # enemy ship has not spawned power up
                    self.score = self.score + enemy.score # add to score
                    # Spawn Health 25 at random in the place of destroyed enemy ship
                    # Probability: 1 per 50 destroyed enemies
                    if randint(1,50) == 1:
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health25(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                        thereIsPowerUp = 1 # to prevent enemy ship from spawning two powerups
                    # Spawn Health 100 random in the place of destroyed enemy ship
                    # but only if enemy ship has not spawned another powerUp
                    # Probability: 1 per 125 destroyed enemies
                    if randint(1,125) == 1 and thereIsPowerUp != 1: 
                        # create temporary instance so we can grab the height of the sprite
                        powerUpObj = Health100(WINDOW_WIDTH, 0,-5)
                        powerUpObj.rect.x = enemy.rect.x
                        powerUpObj.rect.y = enemy.rect.y
                        self.powerUpSprites.add(powerUpObj) 
                                        
                    
            
            # check for collisions between enemyShips and the user
            for enemy in self.aiSprites:
                userHit = pygame.sprite.spritecollide(enemy,self.userSprites3,False,
                                                      pygame.sprite.collide_mask)
                
                # if there was a collision
                if userHit:
                    self.aiSprites.remove(enemy) # remove object
                    self.userShip3.shield -= 100
                    self.score = self.score + enemy.score # add to score
                    self.explodeSnd.play()
                    
            # check for collisions between powerUps and the user
            for powerUp in self.powerUpSprites:
                userHit = pygame.sprite.spritecollide(powerUp,self.userSprites3,False)
                
                # if there was a collision
                if userHit:
                    self.powerUpSprites.remove(powerUp) # remove object
                    powerUp.pickUp(self.userShip3)
                    self.powerUpSnd.play()                # no sound yet!!
            # =============================================================
                    
            # if user is dead
            if self.userShip3.shield <= 0:
                self.userShip3.shield = 0        # round shield to 0
                self.modeBack = 2
                self.gameState = "gameOver"     # change state to gameOver            
        # ====================================================================
        
        # Game Over ==========================================================
        elif self.gameState == "gameOver":            
            pass
        # ====================================================================
        else:
            pass # throw exception!
            
    def draw(self,screen):
    
        # Menu ===============================================================
        if self.gameState == "menu":
            self.menu.draw(screen)
        # Mode====================================================================
        if self.gameState == "mode":
            self.mode.draw(screen)
        # Pause ==============================================================
        if self.gameState == "pause":
            self.pause.draw(screen)
        
        # Volume =============================================================
        if self.gameState == "volume":
            self.volume.draw(screen)
        # ====================================================================
        
        # Credits ============================================================
        if self.gameState == "credits":           
            self.credits.draw(screen)
        # ====================================================================
        
        # Game ===============================================================
        elif self.gameState == "game_Normal":
            # erase screen
            screen.fill(BLACK)

            # draw background - since the background is scrolling
            # we shall draw two side by side to prevent the background from ending
            # this way it repeats itself
            screen.blit(self.backg.image,(self.backg.x,self.backg.y))
            screen.blit(self.backg.image,(self.backg.x + self.backg.width,self.backg.y))
                           
            # draw sprites onto the screen
            self.userSprites1.draw(screen)
            self.laserSprites.draw(screen)
            self.aiSprites.draw(screen)
            self.powerUpSprites.draw(screen)

            
            # drawing text
            font = pygame.font.SysFont("Arial", 25)
            shieldTxt = font.render("Shield: " + str(self.userShip1.shield), True, WHITE)
            scoreTxt = font.render("Score: " + str(self.score), True, WHITE)
            screen.blit(shieldTxt, [0,0])
            screen.blit(scoreTxt,  [0,30])           
            
            # animations
            self.backg.scroll(1)          # update background
            self.userShip1.animate()       # update animation
            for enemy in self.aiSprites:
                enemy.animate()       # update animation
            for powerUp in self.powerUpSprites:
                powerUp.animate()
                
        elif self.gameState == "game_Hard":
            # erase screen
            screen.fill(BLACK)

            # draw background - since the background is scrolling
            # we shall draw two side by side to prevent the background from ending
            # this way it repeats itself
            screen.blit(self.backg.image,(self.backg.x,self.backg.y))
            screen.blit(self.backg.image,(self.backg.x + self.backg.width,self.backg.y))
                           
            # draw sprites onto the screen
            self.userSprites2.draw(screen)
            self.laserSprites.draw(screen)
            self.aiSprites.draw(screen)
            self.powerUpSprites.draw(screen)

            
            # drawing text
            font = pygame.font.SysFont("Arial", 25)
            shieldTxt = font.render("Shield: " + str(self.userShip2.shield), True, WHITE)
            scoreTxt = font.render("Score: " + str(self.score), True, WHITE)
            screen.blit(shieldTxt, [0,0])
            screen.blit(scoreTxt,  [0,30])           
            
            # animations
            self.backg.scroll(1)          # update background
            self.userShip2.animate()       # update animation
            for enemy in self.aiSprites:
                enemy.animate()       # update animation
            for powerUp in self.powerUpSprites:
                powerUp.animate()

        elif self.gameState == "game_Hell":
            # erase screen
            screen.fill(BLACK)

            # draw background - since the background is scrolling
            # we shall draw two side by side to prevent the background from ending
            # this way it repeats itself
            screen.blit(self.backg.image,(self.backg.x,self.backg.y))
            screen.blit(self.backg.image,(self.backg.x + self.backg.width,self.backg.y))
                           
            # draw sprites onto the screen
            self.userSprites3.draw(screen)
            self.laserSprites.draw(screen)
            self.aiSprites.draw(screen)
            self.powerUpSprites.draw(screen)

            
            # drawing text
            font = pygame.font.SysFont("Arial", 25)
            shieldTxt = font.render("Shield: " + str(self.userShip3.shield), True, WHITE)
            scoreTxt = font.render("Score: " + str(self.score), True, WHITE)
            screen.blit(shieldTxt, [0,0])
            screen.blit(scoreTxt,  [0,30])           
            
            # animations
            self.backg.scroll(1)          # update background
            self.userShip3.animate()       # update animation
            for enemy in self.aiSprites:
                enemy.animate()       # update animation
            for powerUp in self.powerUpSprites:
                powerUp.animate()
                
        # ====================================================================
    
        # Game Over ==========================================================

        elif self.gameState == "gameOver":
        
            # display game over and continue text
            font80      = pygame.font.SysFont("Arial", 80)
            font30      = pygame.font.SysFont("Arial", 30)
            gameOverTxt = font80.render("Game Over!", True, WHITE)
            continueTxt = font30.render("(Press Enter to restart, go to menu ESC)", True, WHITE)
            
            screen.blit(gameOverTxt, [WINDOW_WIDTH/2-gameOverTxt.get_width()/2, 
                        WINDOW_HEIGHT/2-gameOverTxt.get_height()/2])
            screen.blit(continueTxt, [WINDOW_WIDTH/2-continueTxt.get_width()/2, 
                        WINDOW_HEIGHT/2-continueTxt.get_height()/2+55])
            pygame.display.update()
        else:
        
            pass # throw exception!!
