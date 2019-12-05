import gravsim
import button
import pygame
from engine import SceneBase, main, textBox
import numpy as np
import slider
from datetime import datetime

#CONSTANTS
WIN_X = 950
WIN_Y = 600
FPS = 70
TOOLS = ['new',]

#COLORS
BLACK = (0, 0, 0)
BLUE = (20, 20, 255)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

#PARAMETERS
SCALE = 1e9 # this is in m/px (this times WIN_Y is simulation dimension!)
FOCUS = (0, 0) # center of simulation display (in meters)
MIN_SIZE = 2 # minimum radius in pixels, so all bodies can be seen
TIMESTEP = 3e4 # seconds to pass per frame
SUBSTEP = 1 # number of simulation steps to do per frame (improves precision, runs slower)
G = 6.67408e-11 # Gravitational Constant
TRAILS = True # Whether or not trails should follow bodies
NEWBODY_MASS = 1.e28
NEWBODY_RADIUS = 5.e8


class GameScene(SceneBase):
	def __init__(self):
		SceneBase.__init__(self)
		
		self.time = datetime.now()
		self.bodies = [
						gravsim.Body(np.array([0., 0.]), 1.989e30, 6.9551e8, np.array([0.+1e5, 0.])), # Sun
						gravsim.Body(np.array([1.496e11, 0.]), 5.972e24, 6.371e6, np.array([1e5+0., 2.9786e4])), # Earth
						gravsim.Body(np.array([1.496e11+3.844e8, 0.]), 7.347e22, 1.7371e6, np.array([1e5+0., 2.9786e4+1.023e3])) # Moon
						]
		self.focus = self.genFocus()
		self.new_body = None
		self.trajectory = None
		self.active = TOOLS[0]
		self.flags = {
						'body_placed':False
						}
		self.scale = slider.Slider('Scale', 9., 12., 4., (630, 20))
		self.timestep = slider.Slider('Timestep', 4., 4.5, 0., (630, 90))
		self.g = slider.Slider('G', -10.1756, -5., -11., (630, 160))
		self.minsize = slider.Slider('Min Body Size', 2., 10., 1., (630, 230))
		self.newmass = slider.Slider('Body Mass', 24., 31., 1., (630, 300))
		self.newradius = slider.Slider('Body Radius', 6., 11., 1., (630, 370))
		self.sliders = [
						self.scale,
						self.timestep,
						self.g,
						self.minsize,
						self.newmass,
						self.newradius
						]
		self.trails = button.Button((620, 480, 100, 50), 'Toggle Trails')
		self.x = button.Button((730, 480, 100, 50), '')
		self.reset = button.Button((840, 480, 100, 50), 'Reset All')
		self.delete = button.Button((620, 540, 100, 50), 'Delete Focus')
		self.switch = button.Button((730, 540, 100, 50), 'Switch Focus')
		self.zoom = button.Button((840, 540, 100, 50), 'Zoom Focus')
		self.buttons = [
						self.trails,
						self.x,
						self.reset,
						self.delete,
						self.switch,
						self.zoom
						]
		
	def ProcessInput(self, events, pressed_keys):
		for event in events:
			if 'click' in self.trails.handleEvent(event):
				global TRAILS
				TRAILS = not TRAILS
			if 'click' in self.x.handleEvent(event):
				pass
			if 'click' in self.reset.handleEvent(event):
				self.SwitchToScene(GameScene())
			if 'click' in self.delete.handleEvent(event) and len(self.bodies)>1:
				self.deleteFocus()
			if 'click' in self.switch.handleEvent(event):
				self.switchFocus()
			if 'click' in self.zoom.handleEvent(event):
				self.zoomFocus()
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				for s in self.sliders:
					if s.button_rect.collidepoint(pos):
						s.hit = True
				
				if self.active == 'new' and not self.flags['body_placed'] and pos[0] < WIN_Y:
					calc_r = int(NEWBODY_RADIUS / SCALE)
					r = max([MIN_SIZE, calc_r])
					self.new_body = (pos, r)
					self.flags['body_placed'] = True
			elif event.type == pygame.MOUSEBUTTONUP:
				for s in self.sliders:
					s.hit = False
					
				if self.flags['body_placed']:
					coordinates = (SCALE*(self.new_body[0][0]-WIN_Y/2)+FOCUS[0],
									SCALE*(self.new_body[0][1]-WIN_Y/2)+FOCUS[1])
					velocity = SCALE / 5.e5 * np.subtract(self.new_body[0], pygame.mouse.get_pos()) + self.focus.velocity
					body = gravsim.Body(coordinates, NEWBODY_MASS, NEWBODY_RADIUS, velocity, i=self.focus.i)
					self.bodies.append(body)
					self.new_body = None
					self.trajectory = None
					self.flags['body_placed'] = False
	
	def Update(self):
		# Move sliders
		for s in self.sliders:
			if s.hit:
				s.move()
				
		# Update Parameters
		global SCALE
		global TIMESTEP
		global G
		global MIN_SIZE
		global NEWBODY_MASS
		global NEWBODY_RADIUS
		SCALE = 10 ** self.scale.val
		TIMESTEP = 10 ** self.timestep.val
		G = 10 ** self.g.val
		MIN_SIZE = int(self.minsize.val)
		NEWBODY_MASS = 10 ** self.newmass.val
		NEWBODY_RADIUS = 10 ** self.newradius.val
				
		# Simulate motion on bodies
		for i in range(SUBSTEP):
			gravsim.runStep(self.bodies, TIMESTEP/SUBSTEP, G)
			
		# Determine new focus
		global FOCUS
		FOCUS = self.focus.getCoordinates()
		
		# Simulate trajectory
		if self.new_body != None:
			coordinates = (SCALE*(self.new_body[0][0]-WIN_Y/2)+FOCUS[0],
							SCALE*(self.new_body[0][1]-WIN_Y/2)+FOCUS[1])
			velocity = SCALE / 5.e5 * np.subtract(self.new_body[0], pygame.mouse.get_pos()) + self.focus.velocity
			body = gravsim.Body(coordinates, NEWBODY_MASS, NEWBODY_RADIUS, velocity)
			trail_every = 4
			body.setTrailEvery(trail_every)
			focus_copy = self.focus.copy()
			focus_copy.setTrailEvery(trail_every)
			dummies = [nbody.copy() for nbody in self.bodies if (nbody != self.focus)] + [body] + [focus_copy]
			for i in range(40):
				gravsim.runStep(dummies, 10.*TIMESTEP, G)
			self.trajectory = [body.getTrail(), focus_copy.getTrail()]
		
		# Detect collisions
		collided = gravsim.collide(self.bodies)
		if collided != None:
			if self.focus in collided:
				self.focus = self.genFocus()
			
		
	def Render(self, screen):
		# Background color
		screen.fill(BLACK)
		
		# Draw current focus characteristics
		textBox(screen, (20, 20), 'Focus radius: {:.2e} m'.format(self.focus.radius), bgcolor=BLACK, fgcolor=WHITE, ftsize=12)
		textBox(screen, (20, 40), 'Focus mass: {:.2e} kg'.format(self.focus.mass), bgcolor=BLACK, fgcolor=WHITE, ftsize=12)
		textBox(screen, (20, 60), 'Focus velocity: {:.2e} m/s'.format(np.linalg.norm(self.focus.velocity)), bgcolor=BLACK, fgcolor=WHITE, ftsize=12)
		
		# Draw fps
		dt = datetime.now().timestamp() - self.time.timestamp()
		fps = 1/dt
		textBox(screen, (WIN_Y-100, 20), 'FPS: {:d}'.format(int(fps)), bgcolor=BLACK, fgcolor=WHITE, ftsize=12)
		self.time = datetime.now()
		
		# Draw trails
		if TRAILS:
			for body in self.bodies:
				color = 255
				trail = body.getTrail()
				trail_f = self.focus.getTrail()
				delta = 255. / (len(trail) + 1.)
				for pos, pos_f in zip(trail, trail_f):
					pos_x = int((pos[0] - FOCUS[0]) / SCALE + WIN_Y/2)
					pos_y = int((pos[1] - FOCUS[1]) / SCALE + WIN_Y/2)
					if 0<pos_x<WIN_Y and 0<pos_y<WIN_Y:
						pygame.draw.circle(screen, (int(color),)*3, (pos_x, pos_y), 1)
						color = color - delta
		
		# Draw bodies
		for body in self.bodies:
			drawBody(screen, body)
			
		# Draw body being placed, if any
		if self.new_body != None:
			pygame.draw.circle(screen, WHITE, self.new_body[0], self.new_body[1])
		# And trajectory
		if self.trajectory != None:
			for pos, pos_f in zip(self.trajectory[0], self.trajectory[1]):
				pos_x = int((pos[0] - pos_f[0]) / SCALE + WIN_Y/2)
				pos_y = int((pos[1] - pos_f[1]) / SCALE + WIN_Y/2)
				pygame.draw.circle(screen, WHITE, (pos_x, pos_y), 1)
				
		# Fill in rightside area
		screen.fill(GRAY, rect=(WIN_Y, 0, WIN_X-WIN_Y, WIN_Y))
			
		# Draw screen divisions
		screen.fill(WHITE, rect=(WIN_Y, 0, 10, WIN_Y))
		screen.fill(WHITE, rect=(WIN_Y, 460, WIN_X-WIN_Y, 10))
		
		# Draw sliders
		for s in self.sliders:
			s.draw(screen)
			
		# Draw text next to sliders
		textBox(screen, (750, 32), '{:.2e} m/px'.format(SCALE), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		textBox(screen, (750, 102), '{:.2e} s/frame'.format(TIMESTEP), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		textBox(screen, (750, 172), '{:.2e} m3*kg−1*s−2'.format(G), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		textBox(screen, (750, 242), '{:d} px'.format(MIN_SIZE), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		textBox(screen, (750, 312), '{:.2e} kg'.format(NEWBODY_MASS), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		textBox(screen, (750, 382), '{:.2e} m'.format(NEWBODY_RADIUS), bgcolor=GRAY, fgcolor=WHITE, ftsize=23)
		
		# Draw buttons
		for b in self.buttons:
			b.draw(screen)
		
	def LaunchBody(self, body):
		self.bodies.append(body)
		
	def genFocus(self):
		masses = [body.getMass() for body in self.bodies]
		max_mass = max(masses)
		idx = masses.index(max_mass)
		return self.bodies[idx]
		
	def zoomFocus(self):
		z = self.focus.getRadius() / 5.
		self.scale.val = np.log10(z)
		# z = 20px * m/px = r
		
	def switchFocus(self):
		idx = self.bodies.index(self.focus)
		if idx == len(self.bodies)-1:
			idx = 0
		else:
			idx += 1
		self.focus = self.bodies[idx]
		
	def deleteFocus(self):
		self.bodies.remove(self.focus)
		self.focus = self.genFocus()
		
		
def drawBody(screen, body, color=WHITE):
	'''
	Draws body to screen using a circle
	Draw Radius is determined by looking at scale
	'''
	calc_r = int(body.getRadius() / SCALE) # m / m/px
	r = max([MIN_SIZE, calc_r])
	pos_x = int((body.getCoordinates()[0] - FOCUS[0]) / SCALE + WIN_Y/2)
	pos_y = int((body.getCoordinates()[1] - FOCUS[1]) / SCALE + WIN_Y/2)
	if 0<pos_x<WIN_Y and 0<pos_y<WIN_Y:
		pygame.draw.circle(screen, color, (pos_x, pos_y), r)
		
		
main(WIN_X, WIN_Y, FPS, GameScene())