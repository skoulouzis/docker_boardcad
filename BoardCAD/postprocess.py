import boardcad.gui.jdk.BoardCAD
from javax.swing import *
from java.io import *

def process():
    fc = JFileChooser()
    fc.setCurrentDirectory(File(boardcad.gui.jdk.BoardCAD.getInstance().defaultDirectory))
    returnVal = fc.showOpenDialog(boardcad.gui.jdk.BoardCAD.getInstance().getFrame())
    if (returnVal != JFileChooser.APPROVE_OPTION):
        return
    mfile = fc.getSelectedFile()
    filename = mfile.getPath()
    if(filename == None):
        return
    f=open(filename, 'r')
    f2=open(filename.replace('.ngc', '_post.ngc'), 'w')
    for str in f:
        if(str.find('[')>-1 or str.find('M')>-1):
            print 'Skipping line:' + str
        else:
            print str
            if(str.find('A-')>0):
                f2.write(str.replace('A-', 'A'))
            else:
                f2.write(str.replace('A', 'A-'))
    f2.write('M2')
    f2.flush()
    f.close
    f2.close

process()

