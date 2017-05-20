# -*- coding: utf-8 -*-
"""
Created on Sun May 14 12:53:30 2017

@author: Martin
"""

import tkinter as tk

from time import sleep

def unpack_kwargs(kw, items=[], mode='normal'):
    """ allows to return desired list of items from kwargs
        either in normal mode or invers (rest of the list)
        if item cannot be found, default value is used
    """
    
    assert isinstance( kw     , dict ) , 'kw should be dict, not %r'      % type( kw      )
    assert isinstance( items  , list ) , 'items should be list, not %r'   % type( items   )
    assert isinstance( mode   , str  ) , 'mode should be str, not %r'     % type( items   )
    assert mode in ['normal', 'invers'], 'unknown mode: %s' % mode

    kwargs = {}
    
    if mode == 'normal':
        for k in items:
            kwargs[k] = kw.get(k)
            
    elif mode == 'invers':
        for k,v in kw.items():
            if k not in items:
                kwargs[k] = kw.get(k)
            
    return kwargs

        
class Well:
    
    _defaultTags = ('well', 'notClicked')
    
    def __init__(self, master, wellId=-1, x=0, y=0, dia=0, **kw):
        
        assert isinstance(wellId, int) and wellId > -1, 'wellId should be int and >-1, not %s' % wellId
        
        self._master  = master
        self._id      = -1
        self._wellId  = wellId
        self._x       = x
        self._y       = y
        self._dia     = dia
        self._drug    = kw.get('drug')  # type of drug
        self._conc    = kw.get('conc')  # concentration of drug
        self._tags    = kw.get('tags', tuple()) + self._defaultTags
        self._clicked = False
        
        # we need some colors to make it nice
        self._defaultColor      = 'white'
        self._clickedColor      = 'red'
        self._highlightedColor  = 'CadetBlue1'
        self._clickAndHighColor = 'deep pink'
        
        # draw well
        self.Draw()
        
### --------------------------------------------------------------------------------------------------
                    
    def Draw(self):
        """ draw well on master canvas """
        
        self._id = self._master.create_oval(
                            (self._x, self._y, self._x+self._dia, self._y+self._dia),
                            fill = self._defaultColor,
                            tags = self._defaultWellTags
                        )
        
### --------------------------------------------------------------------------------------------------
                    
    def SetColor(self, **kw):
        """ function to set the color of wells
            no check for correct color yet
        """
        
        self._defaultColor      = kw.get( 'default'     , self._defaultColor      )
        self._clickedColor      = kw.get( 'clicked'     , self._clickedColor      )
        self._highlightedColor  = kw.get( 'highlight'   , self._highlightedColor  )
        self._clickAndHighColor = kw.get( 'clickAndHigh', self._clickAndHighColor )
        
### --------------------------------------------------------------------------------------------------
                    
    def _UpdateTags(self, tags):
        
        assert self._id > -1, 'incorrect id: %s' % self._id
        
        self._tags = tags
        
        self.itemconfig(self._id, tags=self._tags)
        
### --------------------------------------------------------------------------------------------------
                    
    def _UpdateColor(self):
        
        assert self._id > -1, 'incorrect id: %s' % self._id
        
        if 'notClicked' in self._tags:
            color = self._defaultColor
        elif 'clicked' in self._tags:
            color = self._clickedColor
            
        self.itemconfig(self._id, fill=color)
        
### --------------------------------------------------------------------------------------------------
                    
    def SetClicked(self):
        """ set well to clicked state """

        # if it wasn't clicked already, add it...
        if not self._clicked:
                
            # first remove 'notClicked' tag
            tags = tuple(tag for tag in self._tags if tag != 'notClicked')
            
            # now add clicked tag
            tags += ('clicked',)
            
            # update tags
            self._UpdateTags(tags)
            
            # update color
            self._UpdateColor()
            
            # update status
            self._clicked = True
                
### --------------------------------------------------------------------------------------------------
                    
    def SetNotClicked(self):
        """ set well to not clicked state """

        # if it was clicked already, remove it...
        if self._clicked:
                
            # first remove 'notClicked' tag
            tags = tuple(tag for tag in self._tags if tag != 'clicked')
            
            # now add clicked tag
            tags += ('notClicked',)
            
            # update tags
            self._UpdateTags(tags)
            
            # update color
            self._UpdateColor()
            
            # update status
            self._clicked = False
        
### --------------------------------------------------------------------------------------------------

        

# let's make a new class to clean up things a bit
class WellPlate(tk.Frame):
    
    _objectKwArgs    = ['bd','relief']
    _defaultWellTags = ('well', 'notClicked')
    
    def __init__(self, master, rows=8, cols=12, dia=24, mar=4, **kw):
        """ init our class """
        tk.Frame.__init__(self, master, unpack_kwargs(kw, self._objectKwArgs))
        self.pack(unpack_kwargs(kw, self._objectKwArgs, mode='invers'))
        
        # copy stuff to members
        self.master      = master
        self._rows       = rows
        self._cols       = cols
        self._dia        = dia
        self._mar        = mar
        self._rectMargin = 2
        self._winMargin  = 10
        
        # we need some colors to make it nice
        self._defaultColor       = 'white'
        self._clickedColor       = 'green'
        self._highlightedColor   = 'CadetBlue1'
        self._clickAndHighColor  = 'deep pink'
        self._clickAndMoveColor  = 'grey'
        self._dropForbiddenColor = 'red'
        
        # we need a last moved-to element
        # and maybe for later also a last clicked one...
        self._lastMovedToWell    = None
        self._lastClickedWell    = None
        self._lastDraggedWell    = None
        self._lastDragAndMovWell = None
        self._drag               = False
        self._lastMarkRect       = None
        
        # contains list of WellSetup class to store all info about the wells
        # default is created upon drawing the well plate
        self._wells = []
    
        # and how about to draw some paintings today...?!    
        self._canvas = tk.Canvas(self)
        self._canvas.pack()
        
        # we wanna see what's going on, so let's define some events...
        # we want to click on the wells, so connect the left+right click event
        self._canvas.bind( '<Button-1>', self._ClickHandler )
        self._canvas.bind( '<Button-3>', self._ClickHandler )
        # we wanna see what's going on, so let's define some events...
        # we want to click on the wells, so connect the double left click event
        self._canvas.bind( '<Double-Button-1>', self._DoubleClickHandler )
        # and since it's nice to see where we are and because we can
        # highlight the well with the motion event
        self._canvas.bind( '<Motion>'  , self._MotionHandler )
        # we might want to move the set parameters from one well to another
        # let's link that to left+right mouse button pressed movement
        self._canvas.bind( '<B1-Motion>', self._PressedMotionHandler )
        self._canvas.bind( '<B3-Motion>', self._PressedMotionHandler )
        # for this we also need the release button event
        # the user wants to drop the well somewhere...
        self._canvas.bind( '<ButtonRelease-1>', self._ReleaseHandler )
        self._canvas.bind( '<ButtonRelease-3>', self._ReleaseHandler )
        

### --------------------------------------------------------------------------------------------------

    def Draw(self):
        """ draw the well plate on given master canvas """
        
        
        # does the whole thing still fit on the canvas and in the window?
        # if, not let's just change that
        # consider some margin
        
#        self.master.minsize(
#                width  = (self._xOff+self._rectMargin+self._winMargin+(self._cols+1)*(self._dia+self._mar)),
#                height = (self._yOff+self._rectMargin+self._winMargin+(self._rows+1)*(self._dia+self._mar))
#            )
        self._canvas.configure(
                width  = (self._rectMargin+(self._cols+1)*(self._dia+self._mar)),
                height = (self._rectMargin+(self._rows+1)*(self._dia+self._mar))
            )

        # go through all the rows
        # we need one more, we have the numbers
        for row in range(self._rows+1):
            
            # what's my next y-coordinate?
            y = row * (self._dia+self._mar)
            
            # go through all the columns
            # also here we need one more, we have letters
            for col in range(self._cols+1):
                
                # what's my next x-coordinate?
                x = col * (self._dia+self._mar)
                
                # let's put the numbers in the first row
                # but skip the first column
                # there're only letters, no wells...
                if row == 0 and col > 0:
                    # we also want to give the guy a name, so we can find it later
                    self._canvas.create_text(
                            x+self._dia/2,
                            y+self._dia/2,
                            text=str(col),
                            tags='column%s' % col
                        )
                
                # we are done with the numbering
                # let's do the other rows now
                else:
                
                    # but first we have to make sure that every row has a latter
                    if col == 0 and row > 0:
                        
                        # use chr to convert to letter
                        # NOTE: ASCII 'A' starts at 65
                        # but we have already row==1...so remove -1
                        # and don't forget the name, otherwise these here feel alone
                        self._canvas.create_text(
                                x+self._dia/2,
                                y+self._dia/2,
                                text=chr(65+row-1),
                                tags='row%s' % row
                            )
                
                    # now we finally have our labels
                    # let's get started with the wells...
                    # but don't put one in the corner x=0,y=0
                    elif row > 0 and col > 0:
                        self._canvas.create_oval(
                                (x, y, x+self._dia, y+self._dia),
                                fill=self._defaultColor,
                                tags=self._defaultWellTags
                            )
                        
#                        # get a brand new setup for this well
#                        wellId = row*(self._cols+1)+col 
#                        self._wellSetups.append( WellSetup(wellId) )
                        
                        # Well class would be nice
                        # but still problems with ID tracking
                        # canvas ID different from well ID
                        # dict would solve the problem
                        # but makes the internal storage of the ID obsolete
                        # collector class for wells could be another option
#                        wellId = (row-1)*(self._cols)+col
#                        self._wells.append( Well(self._canvas, wellId, x, y, self._dia) )
                        

        # draw a rectangle around the whole thing, if we are finished
        self._canvas.create_rectangle(
                self._rectMargin,
                self._rectMargin,
                self._rectMargin+(self._cols+1)*(self._dia+self._mar),
                self._rectMargin+(self._rows+1)*(self._dia+self._mar)
            )
        
### --------------------------------------------------------------------------------------------------
        
    def _ClickHandler(self, event):
        """ function to process click actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        # what tags does this guy already have?
        well, tags = self._GetWellAndTags()
        
        # left mouse button
        if event.num == 1:
        
            # have we found something?
            # ...maybe a well...
            if len(well) > 0 and 'well' in tags:
                
                # if it wasn't clicked already, add it...
                if 'notClicked' in tags:
                    
                    # first remove 'notClicked' tag
                    tags = tuple(tag for tag in tags if tag != 'notClicked')
                    
                    # now add clicked tag
                    tags += ('clicked',)
                    
                    # the user also needs to see that it was clicked
                    # so let's change the color...
                    # don#t use clicked color, since the mouse is still over the well
                    # don't forget to update the tags
                    self._canvas.itemconfig(well, fill=self._clickAndHighColor, tags=tags)
            
                    # we need to update the last clicked item...we found another one
                    self._lastClickedWell = well
        
        # right mouse button
        elif event.num == 3:
            
            # store coordinates for the upper left edge of a rectangle
            self._xMarkStart = self._canvas.canvasx(event.x)
            self._yMarkStart = self._canvas.canvasy(event.y)
                
### --------------------------------------------------------------------------------------------------
        
    def _DoubleClickHandler(self, event):
        """ function to process double-click actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        # what tags does this guy already have?
        well, tags = self._GetWellAndTags()
        
        # have we found something?
        # ...maybe a well...
        if len(well) > 0 and 'well' in tags:
            
            # if the guy was clicked, then let's reset it
            if 'clicked' in tags:
                
                # first remove 'clicked' tag
                tags = tuple(tag for tag in tags if tag != 'clicked')
                
                # now add clicked tag
                tags += ('notClicked',)
                
                # the user also needs to see that it was clicked
                # so let's change the color...
                # don't forget to update the tags
                self._canvas.itemconfig(well, fill=self._defaultColor, tags=tags)
        
                # we need to update the last clicked item...we found another one
                self._lastClickedWell = well
                
### --------------------------------------------------------------------------------------------------
        
    def _MotionHandler(self, event):
        """ function to process motion actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        # what tags does this guy already have?
        well, tags = self._GetWellAndTags()
        
        # have we found something?
        # ...maybe a well...
        if len(well) > 0 and 'well' in tags:
            
            # is this well the same as the last one?
            # if not, we need to reset the color and update the last move-to item
            # we don't need to care about _lastMovedToWell=None at the moment
            if well != self._lastMovedToWell:
                
                # we want to reset the color of the wells if we move out
                # so let's get the wells...
                # but watch out, don't reset the ones that were already clicked
                if self._lastMovedToWell:
                    if 'clicked' in self._canvas.gettags(self._lastMovedToWell):
                        self._canvas.itemconfig( self._lastMovedToWell, fill=self._clickedColor )
                        
                    # only if not clicked, default color is ok
                    else:
                        self._canvas.itemconfig( self._lastMovedToWell, fill=self._defaultColor )
                
                
                # after we have reset the left well, we can deal with the new one...
                # here we also need to consider if it was already clicked or not
                if 'clicked' in tags:
                    self._canvas.itemconfig( well, fill=self._clickAndHighColor )
                else:
                    self._canvas.itemconfig( well, fill=self._highlightedColor  )
                
                # update last moved-to item after updating
                self._lastMovedToWell = well
                
                
        # but wait, what if we leave the well area?
        # we still need to reset the last moved-to element...
        elif (len(well) == 0 or 'row' in tags or 'col' in tags) and self._lastMovedToWell:
            if 'clicked' in self._canvas.gettags(self._lastMovedToWell):
                self._canvas.itemconfig( self._lastMovedToWell, fill=self._clickedColor )
                
            # only if not clicked, default color is ok
            else:
                self._canvas.itemconfig( self._lastMovedToWell, fill=self._defaultColor )
            
                
### --------------------------------------------------------------------------------------------------
                    
    def _PressedMotionHandler(self, event):
        """ function that tells us if a well is about to be moved by the user """
        
        well, tags = self._GetWellAndTags(event)
        
        # left button was clicked
        if event.state == 256:
                
            # there is actually not much to do here
            # just store the dragged well
            if self._lastDraggedWell != self._lastClickedWell:
                self._lastDraggedWell = self._lastClickedWell
                self._drag        = True
            
            # have we found something?
            # ...maybe a well...
            if len(well) > 0 and 'well' in tags:
                
                if self._lastDragAndMovWell:
                    
                    # forbidden to drop the well on another well...or for later ask for overwrite
                    if 'clicked' in self._canvas.gettags(self._lastDragAndMovWell):
                        self._canvas.itemconfig( self._lastDragAndMovWell, fill=self._clickedColor )
                        
                    # only if not clicked, default color is ok
                    else:
                        self._canvas.itemconfig( self._lastDragAndMovWell, fill=self._defaultColor )
                    
                # after we have reset the left well, we can deal with the new one...
                # here we also need to consider if it was already clicked or not
                if 'clicked' in tags:
                    self._canvas.itemconfig( well, fill=self._dropForbiddenColor )
                else:
                    self._canvas.itemconfig( well, fill=self._clickAndMoveColor  )
                
                # update last drag-and-move-to item after updating
                self._lastDragAndMovWell = well
                
        
        # right mouse button
        elif event.state == 1024:
            
            # get proper coordinates for the lower right corner of the rectangle
            self._xMarkStop= self._canvas.canvasx(event.x)
            self._yMarkStop = self._canvas.canvasy(event.y)
            
            # delete old ranctangle
            # otherwise we get nasty tracks on the screen
            self._canvas.delete(self._lastMarkRect)
            
            # but let's get a new one cause the size changed
            self._lastMarkRect = self._canvas.create_rectangle(
                                                    self._xMarkStart,
                                                    self._yMarkStart,
                                                    self._xMarkStop,
                                                    self._yMarkStop,
                                                    dash=True,
                                                    outline='red',
                                                    fill=''
                                                )
            
            # let's highlight all well in the box
            # we first need to get them
            wells = self._canvas.find_overlapping(
                                        self._xMarkStart,
                                        self._yMarkStart,
                                        self._xMarkStop,
                                        self._yMarkStop
                                    )
            
            
            for well in wells:
                
                # after we have reset the left well, we can deal with the new one...
                # here we also need to consider if it was already clicked or not
                if 'clicked' in self._canvas.gettags(well):
                    self._canvas.itemconfig( well, fill=self._clickAndHighColor )
                else:
                    self._canvas.itemconfig( well, fill=self._highlightedColor  )
            
### --------------------------------------------------------------------------------------------------
                    
    def _ReleaseHandler(self, event):
        """ function to drop settings of a well to another one...
            drag & drop functionality
        """
        
        # we can easily find our current well with the tag 'current'
        # what tags does this guy already have?
        well, tags = self._GetWellAndTags()
        
        # left mouse button
        if event.num == 1:
        
            # was it dragged or is it a normal released button?
            # only start if it's a new well
            if self._drag and well != self._lastDraggedWell:
                
                self._lastMovedToWell = well
                self._lastClickedWell = well
                
                
                # swap setups
#                dum                                          = self._wellSetups[list(well)[0]]
#                self._wellSetups[list(well)[0]]              = self._wellSetups[list(self._draggedWell)[0]]
#                self._wellSetups[list(self._draggedWell)[0]] = dum

        # right mouse button
        elif event.num == 3:
            
            # just delete the rectangle so far
            self._canvas.delete(self._lastMarkRect)
            
            
            # let's highlight all well in the box
            # we first need to get them
            wells = self._canvas.find_overlapping(
                                        self._xMarkStart,
                                        self._yMarkStart,
                                        self._xMarkStop,
                                        self._yMarkStop
                                    )
            
            
            for well in wells:
                
                tags = self._canvas.gettags(well)
                
                # if it wasn't clicked already, add it...
                if 'notClicked' in tags:
                    
                    # first remove 'notClicked' tag
                    tags = tuple(tag for tag in tags if tag != 'notClicked')
                    
                    # now add clicked tag
                    tags += ('clicked',)
                    
                    # the user also needs to see that it was clicked
                    # so let's change the color...
                    # don#t use clicked color, since the mouse is still over the well
                    # don't forget to update the tags
                    self._canvas.itemconfig(well, fill=self._clickedColor, tags=tags)
                    
                self._lastMovedToWell = well
                self._lastClickedWell = well
            
            
### --------------------------------------------------------------------------------------------------
                    
    def _GetWellAndTags(self, event=None):
        
        # no event was given, use 'current' tag as default
        if not event:
            # we can easily find our current well with the tag 'current'
            well = self._canvas.find_withtag('current')
            
        else:
            
            # get proper coordinates
            x = self._canvas.canvasx(event.x)
            y = self._canvas.canvasy(event.y)
            
            well = self._canvas.find_overlapping(x,y,x,y)
            
        # what tags do this guy already have?
        tags = self._canvas.gettags(well)
        
        return well, tags
          
### --------------------------------------------------------------------------------------------------
              
    def _UpdateColorScheme(self, color, tags=('notClicked',)):
        """ function to update default and clicked well color """
        
        # just update color with given tags
        for well in self.master.find_withtag(tags):
            self._canvas.itemconfig(well, fill=color)





#######################################
#######################################
###       --- MAIN SECTION ---      ###
#######################################
#######################################

# Am I the master here?
if __name__ == '__main__':
    
    # we need a master to draw on
    master = tk.Tk()
    
    master.title('WellPlateApp')
    
    # next, let's init our well plate
    wellPlate = WellPlate(master, bd=5, relief=tk.SUNKEN)
    
#    canv = tk.Canvas(master)
#    canv.pack()
#    
#    well1 = Well(canv, 1, 10,10,40)
#    well2 = Well(canv, 2)
    
    # draw our well plate
    wellPlate.Draw()
    
    # we cannot see anything yet, let's get started...
    master.mainloop()