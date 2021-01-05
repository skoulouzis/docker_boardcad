import boardcad.gui.jdk.BoardCAD
import boardcam.cutters.STLCutter
import boardcam.BoardMachine
import cadcore.NurbsPoint
from javax.swing import *
import math

###########################################################################
# Generate the g-code as a parallel task

machine=boardcam.BoardMachine()

machine.read_machine_data()
width_steps=machine.deckCuts
length_steps=50

filename=machine.deckFileName
zmax=machine.zMaxHeight

feedrate=machine.speed
feedrate_stringer=machine.stringerSpeed
feedrate_outline=machine.outlineSpeed

axis4_rail_start=machine.deckRailAngle
axis4_rail_stop=machine.bottomRailAngle
deck_cuts=machine.deckCuts
rail_cuts=machine.deckRailCuts

supportEnd=machine.endSupportPosition
supportEndX=supportEnd[0]
supportEndY=supportEnd[1]
supportEndZ=supportEnd[2]


cutter=boardcam.cutters.STLCutter()
cutter_name=machine.toolName
cutter.init(cutter_name)
axis4_offset_x=machine.axis4_offset.x
axis4_offset_y=machine.axis4_offset.y
axis4_offset_z=machine.axis4_offset.z
offsetRotation=machine.axis4_offsetRotation
offsetRotation5=machine.axis5_offsetRotation
cutter.setRotationCenter(axis4_offset_x, axis4_offset_y, axis4_offset_z);
cutter.scale(machine.toolScaleX,machine.toolScaleY,machine.toolScaleZ);


stringerOffsetZ=[5, 0]
stringerCutoff=machine.stringerCutoff

outlineOffsetZ=[20, 0, -30]
outlineOffsetY=machine.outlineOffset

# get a copy of the deck surface from BoardCAD

boardhandler=boardcad.gui.jdk.BoardCAD.getInstance().getBoardHandler()
board=boardhandler.getActiveBoard();
deck=board.getDeck()

# find tail parameter
t=(deck.getMaxT()+deck.getMinT())/2
s=deck.getMinS()
p = deck.getPoint(s, t)	
p2=p
while (p.x-p2.x<15):
	s=s+0.01
	p = deck.getPoint(s, t)	

start_s=s

s=deck.getMinS()
p = deck.getPoint(s, t)	
p2=p
while (p.x-p2.x<50):
	s=s+0.01
	p = deck.getPoint(s, t)	

tail_s=s
# find parameter value for outline

max_width = 0.0
t=deck.getMinT()

p = deck.getPoint((deck.getMaxS()-deck.getMinS())/2, t)

while (max_width - math.fabs(p.z) <= 0):
	t=t+0.01
	p = deck.getPoint((deck.getMaxS()-deck.getMinS())/2, t)	
	if (math.fabs(p.z) > max_width):
		max_width = math.fabs(p.z)

t_outline=t

# find parameter value for rail

t=deck.getMinT()
angle=180

while (angle>axis4_rail_start):
	t=t+0.01
	p = deck.getPoint((deck.getMaxS()-deck.getMinS())/2, t)
	n=deck.getNormal((deck.getMaxS()-deck.getMinS())/2, t)
	angle=math.fabs(180.0/math.pi*math.atan2(n.z, n.y))

t_rail=t	

#Find uniform distances for t and their angles

wval=[]
tval=[]
aval=[]

t=t_rail
n=deck.getNormal((deck.getMaxS()-deck.getMinS())/2, t)
p=cutter.calcOffset(p,n)
max_width = math.fabs(p.z)+.1
i=p.z
step=p.z/deck_cuts

while i>0.001:
	wval.append(p.z-i)
	i=i-step

print wval
print '\nmax width = %0.3f\n' % max_width

for w in wval:
	while (max_width - math.fabs(p.z) <= math.fabs(w)):
		t=t+0.01
		p=deck.getPoint((deck.getMaxS()-deck.getMinS())/2, t)	
	n=deck.getNormal((deck.getMaxS()-deck.getMinS())/2, t)
	angle=math.fabs(180.0/math.pi*math.atan2(n.z, n.y))
	aval.append(angle)
	tval.append(t)

print tval, aval

# add rail angles

rval=[]
for i in range(rail_cuts):
	rval.append(axis4_rail_stop-i*1.0/(rail_cuts-1)*(axis4_rail_stop-axis4_rail_start))
	
print rval

# Setup progress bar info...

# calculate tool path stringer
stringer_cut=[]
step=0.25

t=(deck.getMaxT()-deck.getMinT())/2
s=deck.getMaxS()
cutter.setRotation(0.0)
p=deck.getPoint(s,t)
#n=deck.getNormal(t,s)
p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(1,0,0))
stringer_cut.append([p.x,-p.z,p.y, 0.0])
while (s>deck.getMinS()):
	p=deck.getPoint(s,t)
	n=deck.getNormal(s,t)
	p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(n.x,n.y,n.z))
	stringer_cut.append([p.x,-p.z,p.y, 0.0])
	s=s-step

s=deck.getMinS()
p=deck.getPoint(s,t)	
p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(-1,0,0))
stringer_cut.append([p.x,-p.z,p.y, 0.0])

# calculate tool path outline

outline_cut=[]
step=0.25

t=t_outline
s=deck.getMinS()
cutter.setRotation(0.0)
while (s<deck.getMaxS()):
	p=deck.getPoint(s,t)
	n=deck.getNormal(s,t)
	p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(n.x,n.y,n.z))
	outline_cut.append([p.x,-p.z,p.y, 0.0])
	s=s+step

# calculate tool path deck

deck_right=[]
deck_left=[]
step=0.25
s=start_s

aval=rval+aval

while aval:
	a=aval.pop()
	print a
	cutter.setRotation(a)
	while (s<deck.getMaxS()):
		t=deck.getMinT()
		angle=180
		while (angle>a and t<(deck.getMaxS()+deck.getMinS())/2):
			t=t+0.01
			p=deck.getPoint(s,t)
			n=deck.getNormal(s,t)
			if(t<t_rail):
				angle=math.fabs(180.0/math.pi*math.atan2(math.sqrt(n.x*n.x+n.z*n.z), n.y))
			else:
				angle=math.fabs(180.0/math.pi*math.atan2(n.z, n.y))
		angle=math.fabs(180.0/math.pi*math.atan2(math.sqrt(n.x*n.x+n.z*n.z), n.y))
		angle5=180.0/math.pi*math.atan2(n.x, n.z)
		cutter.setRotation(angle, angle5)
		p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(n.x,n.y,n.z))
		deck_right.append([p.x,-p.z,p.y, angle, angle5])
		deck_left.append([p.x,p.z,p.y, -angle, -angle5])
		s=s+step	
	a=aval.pop()
	print a	
	cutter.setRotation(a)
	while (s>start_s):
		t=deck.getMinT()
		angle=180
		while (angle>a and t<(deck.getMaxS()+deck.getMinS())/2):
			t=t+0.01
			p=deck.getPoint(s,t)
			n=deck.getNormal(s,t)
			if(t<t_rail):
				angle=math.fabs(180.0/math.pi*math.atan2(math.sqrt(n.x*n.x+n.z*n.z), n.y))
			else:
				angle=math.fabs(180.0/math.pi*math.atan2(n.z, n.y))
		angle=math.fabs(180.0/math.pi*math.atan2(math.sqrt(n.x*n.x+n.z*n.z), n.y))
		angle5=180.0/math.pi*math.atan2(n.x, n.z)
		cutter.setRotation(angle, angle5)
		p=cutter.calcOffset(cadcore.NurbsPoint(p.x,p.y,p.z),cadcore.NurbsPoint(n.x,n.y,n.z))
		deck_right.append([p.x,-p.z,p.y, angle, angle5])
		deck_left.append([p.x,p.z,p.y, -angle, -angle5])
		s=s-step
	deck_right.append([p.x-35,-p.z,p.y, angle, angle5])
	deck_left.append([p.x-35,p.z,p.y, -angle, -angle5])


# write g-code
f=open(filename, 'w')
zsafe='g0 z%d\n' %(zmax)
f.write('(cutting stringer)\n')
for offsetZ in stringerOffsetZ:
	f.write(zsafe)
	p=stringer_cut[0]
	f.write('g0 x%.3f y%.3f a%.3f b0\n' % (p[0]+supportEndX, p[1]+supportEndY, p[3]+offsetRotation))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY, p[2]+supportEndZ+offsetZ-stringerCutoff, p[3]+offsetRotation, feedrate_stringer))
	for p in stringer_cut:
		f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate_stringer))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY, p[2]+supportEndZ+offsetZ-stringerCutoff, p[3]+offsetRotation, feedrate_stringer))

for offsetZ in outlineOffsetZ:
	f.write('(cutting outline right)\n')
	f.write(zsafe)
	p=outline_cut[0]
	f.write('g0 x%.3f y%.3f a%.3f b0\n' % (p[0]+supportEndX, p[1]+supportEndY-outlineOffsetY-200, p[3]+offsetRotation))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY-outlineOffsetY-200, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate))
	mycount=0		
	for p in outline_cut:
		mycount=mycount+1
		f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY-outlineOffsetY, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate_outline))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY-outlineOffsetY-200, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate))
	f.write('(cutting outline left)\n')
	f.write(zsafe)
	p=outline_cut[mycount-1]
	f.write('g0 x%.3f y%.3f a%.3f\n' % (p[0]+supportEndX, -p[1]+supportEndY+outlineOffsetY+200, p[3]+offsetRotation))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, -p[1]+supportEndY+outlineOffsetY+200, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate))
	for i in range(mycount):
		p=outline_cut[mycount-i-1]
		f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, -p[1]+supportEndY+outlineOffsetY, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate))
	f.write('g1 x%.3f y%.3f z%.3f a%.3f f%d\n' % (p[0]+supportEndX, -p[1]+supportEndY+outlineOffsetY+200, p[2]+supportEndZ+offsetZ, p[3]+offsetRotation, feedrate))

f.write(zsafe)
f.write('(cutting deck right)\n');
p=deck_right[0]
f.write('g0 x%.3f y%.3f a%.3f b0\n' % (p[0]+supportEndX, p[1]+supportEndY, p[3]+offsetRotation))
for p in deck_right:
	f.write('g1 x%.3f y%.3f z%.3f a%.3f b%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY, p[2]+supportEndZ, p[3]+offsetRotation, p[4]+offsetRotation5, feedrate))

f.write(zsafe)
f.write('(cutting deck left)\n');	
p=deck_left[0]
f.write('g0 x%.3f y%.3f a%.3f b0\n' % (p[0]+supportEndX, p[1]+supportEndY, p[3]+offsetRotation))
for p in deck_left:
	f.write('g1 x%.3f y%.3f z%.3f a%.3f b%.3f f%d\n' % (p[0]+supportEndX, p[1]+supportEndY, p[2]+supportEndZ, p[3]+offsetRotation, p[4]+offsetRotation5, feedrate))

f.write(zsafe)
f.write('g0 a0 b0')
f.write("M2");
f.close()

JOptionPane.showMessageDialog(None, "Finished g-code generation")

