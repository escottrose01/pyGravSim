import pygame

class SceneBase:
	def __init__(self):
		self.next = self
	
	def ProcessInput(self, events, pressed_keys):
		# Put anything that involves input in here
		print("uh-oh, you didn't override this in the child class")

	def Update(self):
		# Put anything that happens regardless of input here
		print("uh-oh, you didn't override this in the child class")

	def Render(self, screen):
		# Draw the screen!
		print("uh-oh, you didn't override this in the child class")

	def SwitchToScene(self, next_scene):
		self.next = next_scene
	
	def Terminate(self):
		self.SwitchToScene(None)

def main(width, height, fps, start_scene):
	pygame.init()
	screen = pygame.display.set_mode((width, height))
	pygame.display.set_caption('Gravity')
	clock = pygame.time.Clock()
	
	active_scene = start_scene
	
	while active_scene != None:
		
		pressed_keys = pygame.key.get_pressed()
		
		# Filter events
		filtered_events = []
		for event in pygame.event.get():
			quit_attempt = False
			if event.type == pygame.QUIT:
				quit_attempt = True
			elif event.type == pygame.KEYDOWN:
				alt_pressed = pressed_keys[pygame.K_LALT] or \
					pressed_keys[pygame.K_RALT]
				if event.key == pygame.K_ESCAPE:
					quit_attempt = True
				elif event.key == pygame.K_F4 and alt_pressed:
					quit_attempt = True
					
			if quit_attempt:
				active_scene.Terminate()
			else:
				filtered_events.append(event)
				
		active_scene.ProcessInput(filtered_events, pressed_keys) # determine and process inputs
		active_scene.Update() # ???
		active_scene.Render(screen) # Draw
		
		active_scene = active_scene.next
		
		pygame.display.flip()
		clock.tick(fps)

fonts = {}
def textBox(screen, pos, message, bgcolor=(255,255,255), fgcolor=(0,0,0), sfont='freesansbold.ttf', ftsize=32):
	if sfont in fonts.keys():
		font = fonts[sfont]
	else:
		font = pygame.font.Font(sfont, ftsize)
		fonts[sfont] = font
	rendered = font.render(message, True, fgcolor)
	rendered_rect = rendered.get_rect()
	rendered_rect.x = pos[0]
	rendered_rect.y = pos[1]
	
	pygame.draw.rect(screen, bgcolor, rendered_rect)
	screen.blit(rendered, rendered_rect)