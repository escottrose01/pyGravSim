#Evan Rose
#January 9 2019
#Gravity Simulation

# F = ma
# F = G(m1)(m2)/r^2

# position = position + velocity * dt;
# velocity = velocity + ( force / mass ) * dt;
# t += dt;

from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Body:
	'''
	Implements a body that can be manipulated via gracitational fields.
	
	ATTRIBUTES:
	coordinates: numpy array of coordinates
	
	METHODS:
	getCoordinates(): returns body coordinates
	setCoordinates(coordinates): sets body coordinates
	flowVertex(vector_function, speed): moves vertex according to vector function and speed
	'''
	
	def __init__(self, coordinates=np.zeros(2), mass = 100., radius=0., velocity=np.zeros(2), i=0):
		self.coordinates = coordinates
		self.mass = mass
		self.radius = radius
		self.velocity = velocity
		self.max_trails = 50
		self.trail_every = 25
		self.trail = []
		self.i = i
		
	def copy(self):
		'''
		Returns a copy of the body object
		'''
		return Body(self.coordinates, self.mass, self.radius, self.velocity)
		
	def getCoordinates(self):
		'''
		Returns body's coordinates.
		'''
		return self.coordinates
		
	def setCoordinates(self, coordinates):
		'''
		Sets new coordinates for body.
		'''
		self.coordinates = coordinates
		
	def getVelocity(self):
		'''
		Returns body's velocity.
		'''
		return self.velocity
		
	def setVelocity(self, velocity):
		'''
		Sets body's velocity.
		'''
		self.velocity = velocity
		
	def getMass(self):
		'''
		Returns body's mass.
		'''
		return self.mass
	
	def setMass(self, mass):
		'''
		Sets body's mass.
		'''
		self.mass = mass
		
	def getRadius(self):
		'''
		Returns body's radius.
		'''
		return self.radius
		
	def setRadius(self, radius):
		'''
		Sets body's radius.
		'''
		self.radius = radius
		
	def getTrail(self):
		'''
		Returns body's 
		'''
		return self.trail
		
	def setTrailEvery(self, trail_every):
		'''
		Sets body's trail_every.
		'''
		self.trail_every = trail_every
		
	def detect_collision(self, bodies):
		'''
		Detects collisions between other bodies.
		Returns either None or the body first detected in collision.
		'''
		for body in bodies:
			if body != self:
				R = body.getCoordinates() - self.getCoordinates()
				r = np.sqrt(R.dot(R))
				if r < (self.radius + body.radius): return body
		return None

	def calcForce(self, body, G):
		'''
		Calculates the force vector of another body acting upon this one.
		'''
		R = body.getCoordinates() - self.getCoordinates()
		r = np.sqrt(R.dot(R))
		F = (G * self.getMass() * body.getMass() / r**3) * R
		return F

	def calcForces(self, bodies, G):
		'''
		Calculates the net force acting on the body (vector).
		Any bodies with the same coordinates as self are not considered in calculations.
		'''
		L = []
		for body in bodies:
			if not np.all(self.getCoordinates() == body.getCoordinates()):
				L.append(self.calcForce(body, G))
		F = np.add.reduce(L)
		return F
		
	def updateVelocity(self, bodies, G, dt):
		'''
		Accelerates the body linearly across one timestep according to forces.
		Does not move the body!
		'''
		F = self.calcForces(bodies, G)
		a = F / self.getMass()
		v = self.getVelocity() + a * dt
		self.setVelocity(v)
		
	def addTrail(self):
		'''
		Updates the body's trail using its current position
		'''
		self.trail.insert(0, self.getCoordinates())
		while len(self.getTrail()) > self.max_trails:
			self.trail.pop(-1)
		
	def moveBody(self, dt):
		'''
		Moves the body linearly across one timestep based on current velocity.
		'''
		dr = self.getVelocity() * dt
		coordinates = self.getCoordinates() + dr
		self.setCoordinates(coordinates)
		if not self.i % self.trail_every:
			self.addTrail()
		self.i += 1
	
def collide(bodies):
	'''
	Finds collisions (if any) and merges colliding bodies using conversation of momentum.
	Maximum one collision per pass
	'''
	for body in bodies:
		collision = body.detect_collision(bodies)
		if collision != None:
			new_mass = body.mass + collision.mass
			new_radius = np.sqrt(body.radius**2 + collision.radius**2)
			new_velocity = (1/new_mass) * (body.mass*body.velocity + collision.mass*collision.velocity)
			new_coordinates = (1/(new_mass) * (body.mass*body.coordinates + collision.mass*collision.coordinates))
			new_body = Body(new_coordinates, new_mass, new_radius, new_velocity)
			bodies.remove(body)
			bodies.remove(collision)
			bodies.append(new_body)
			return (body, collision)
	return
	

def writeGraph(bodies):
	'''
	Writes the coordinates of each body to a list.
	'''
	graph = []
	for body in bodies:
		graph.append(body.getCoordinates())
	return graph

def runStep(bodies, dt, G):
	'''
	Moves forward one timestep in the simulation.
	'''
	for body in bodies:
		body.moveBody(dt)
	for body in bodies:
		body.updateVelocity(bodies, G, dt)
		