# -*- coding: utf-8 -*-
"""
Created on Sun May 14 12:53:30 2017

@author: Martin
"""

import tkinter as tk


# let's make a new class to clean up things a bit
class WellPlate:
    
    def __init__(self, master, rows=8, cols=12, dia=24, mar=4, xOff=100, yOff=50, *args, **kwargs):
        """ init our class """
        
        # copy stuff to members
        self.master      = master
        self._rows       = rows
        self._cols       = cols
        self._dia        = dia
        self._mar        = mar
        self._xOff       = xOff
        self._yOff       = yOff
        self._rectMargin = 2
        self._winMargin  = 10
        
        # we need some colors to make it nice
        self._defaultColor      = 'white'
        self._clickedColor      = 'red'
        self._highlightedColor  = 'CadetBlue1'
        self._clickAndHighColor = 'deep pink'
        
        # we need a last moved-to element
        # and maybe for later also a last clicked one...
        self._lastMovedToWell = None
        self._lastClickedWell = None
        
        self._defaultWellTags = ('well', 'notClicked')
    
        # and how about to draw some paintings today...?!    
        self._canvas = tk.Canvas(master)
        self._canvas.pack()
        # we wanna see what's going on, so let's define some events...
        # we want to click on the wells, so connect the left click event
        self._canvas.bind( '<Button-1>', self._ClickHandler )
        # we wanna see what's going on, so let's define some events...
        # we want to click on the wells, so connect the double left click event
        self._canvas.bind( '<Double-Button-1>', self._DoubleClickHandler )
        # and since it's nice to see where we are and because we can
        # highlight the well with the motion event
        self._canvas.bind( '<Motion>'  , self._MotionHandler )

### --------------------------------------------------------------------------------------------------

    def Draw(self):
        """ draw the well plate on given master canvas """
        
        
        # does the whole thing still fit on the canvas and in the window?
        # if, not let's just change that
        # consider some margin
        
        self.master.minsize(
                width  = (self._xOff+self._rectMargin+self._winMargin+(self._cols+1)*(self._dia+self._mar)),
                height = (self._yOff+self._rectMargin+self._winMargin+(self._rows+1)*(self._dia+self._mar))
            )
        self._canvas.configure(
                width  = (self._xOff+self._rectMargin+(self._cols+1)*(self._dia+self._mar)),
                height = (self._yOff+self._rectMargin+(self._rows+1)*(self._dia+self._mar))
            )

        # go through all the rows
        # we need one more, we have the numbers
        for row in range(self._rows+1):
            
            # what's my next y-coordinate?
            y = self._yOff + row * (self._dia+self._mar)
            
            # go through all the columns
            # also here we need one more, we have letters
            for col in range(self._cols+1):
                
                # what's my next x-coordinate?
                x = self._xOff + col * (self._dia+self._mar)
                
                # let's put the numbers in the first row
                # but skip the first column
                # there're only letters, no wells...
                if row == 0 and col > 0:
                    # we also want to give the guy a name, so we can find it later
                    self._canvas.create_text( x+self._dia/2, y+self._dia/2, text=str(col), tags='column%s' % col )
                
                # we are done with the numbering
                # let's do the other rows now
                else:
                
                    # but first we have to make sure that every row has a latter
                    if col == 0 and row > 0:
                        
                        # use chr to convert to letter
                        # NOTE: ASCII 'A' starts at 65
                        # but we have already row==1...so remove -1
                        # and don't forget the name, otherwise these here feel alone
                        self._canvas.create_text( x+self._dia/2, y+self._dia/2, text=chr(65+row-1), tags='row%s' % row )
                
                    # now we finally have our labels
                    # let's get started with the wells...
                    # but don't put one in the corner x=0,y=0
                    elif row > 0 and col > 0:
                        self._canvas.create_oval( (x, y, x+self._dia, y+self._dia), fill=self._defaultColor, tags=self._defaultWellTags)
    
        # draw a rectangle around the whole thing, if we are finished
        self._canvas.create_rectangle(
                self._xOff+self._rectMargin,
                self._yOff+self._rectMargin,
                self._xOff+self._rectMargin+(self._cols+1)*(self._dia+self._mar),
                self._yOff+self._rectMargin+(self._rows+1)*(self._dia+self._mar)
            )
        
### --------------------------------------------------------------------------------------------------
        
    def _ClickHandler(self, event):
        """ function to process click actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        eventItem = self._canvas.find_withtag('current')

        # what tags do this guy already have?
        tags = self._canvas.gettags(eventItem)
        
        # have we found something?
        # ...maybe a well...
        if len(eventItem) > 0 and 'well' in tags:
        
            # we need to update the last clicked item...we found another one
            self._lastClickedWell = eventItem
            
            # if it wasn't clicked already, add it...
            if 'notClicked' in tags:
                
                # first remove 'notClicked' tag
                tags = tuple(tag for tag in tags if tag != 'notClicked')
                
                # now add clicked tag
                tags += ('clicked',)
                
                # the user also needs to see that it was clicked
                # so let's change the color...
                # don't forget to update the tags
                self._canvas.itemconfig(eventItem, fill=self._clickedColor, tags=tags)
        
### --------------------------------------------------------------------------------------------------
        
    def _DoubleClickHandler(self, event):
        """ function to process double-click actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        eventItem = self._canvas.find_withtag('current')

        # what tags do this guy already have?
        tags = self._canvas.gettags(eventItem)
        
        # have we found something?
        # ...maybe a well...
        if len(eventItem) > 0 and 'well' in tags:
        
            # we need to update the last clicked item...we found another one
            self._lastClickedWell = eventItem
            
            # if the guy was clicked, then let's reset it
            if 'clicked' in tags:
                
                # first remove 'clicked' tag
                tags = tuple(tag for tag in tags if tag != 'clicked')
                
                # now add clicked tag
                tags += ('notClicked',)
                
                # the user also needs to see that it was clicked
                # so let's change the color...
                # don't forget to update the tags
                self._canvas.itemconfig(eventItem, fill=self._defaultColor, tags=tags)
        
### --------------------------------------------------------------------------------------------------
        
    def _MotionHandler(self, event):
        """ function to process motion actions on canvas element to change well color accordingly """
        
        # we can easily find our current well with the tag 'current'
        eventItem = self._canvas.find_withtag('current')

        # what tags do this guy already have?
        tags = self._canvas.gettags(eventItem)
        
        # have we found something?
        # ...maybe a well...
        if len(eventItem) > 0 and 'well' in tags:
            
            # is this well the same as the last one?
            # if not, we need to reset the color and update the last move-to item
            # we don't need to care about _lastMovedToWell=None at the moment
            if eventItem != self._lastMovedToWell:
                
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
                    self._canvas.itemconfig( eventItem, fill=self._clickAndHighColor )
                else:
                    self._canvas.itemconfig( eventItem, fill=self._highlightedColor  )
                
                # update last move-to item after updating
                self._lastMovedToWell = eventItem
                
                
        # but wait, what if we leave the well area?
        # we still need to reset the last moved-to element...
        elif (len(eventItem) == 0 or 'row' in tags or 'col' in tags) and self._lastMovedToWell:
            if 'clicked' in self._canvas.gettags(self._lastMovedToWell):
                self._canvas.itemconfig( self._lastMovedToWell, fill=self._clickedColor )
                
            # only if not clicked, default color is ok
            else:
                self._canvas.itemconfig( self._lastMovedToWell, fill=self._defaultColor )
            
                
### --------------------------------------------------------------------------------------------------
                    
    def SetDefaultColor(self, color):
        """ function to set the color of clicked wells
            no check for correct color yet
        """
        
        # is it really different?
        if color != self._defaultColor:
            # well, then we need to redraw our plate
            self._UpdateColorScheme(color)
            
            # and then update the member variable
            self._defaultColor = color
                
### --------------------------------------------------------------------------------------------------
                    
    def SetClickedColor(self, color):
        """ function to set the color of clicked wells
            no check for correct color yet
        """
        
        # is it really different?
        if color != self._clickedColor:
            # well, then we need to redraw our plate
            self._UpdateColorScheme(color, 'clicked')
            
            # and then update the member variable
            self._clickedColor = color
                
### --------------------------------------------------------------------------------------------------
                    
    def SetHichlightedColor(self, color):
        """ function to set the color of highlighted wells (mouse moves over them)
            no check for correct color yet
        """
        
        # is it really different?
        if color != self._clickAndHighColor:
            
            # update the member variable
            self._highlightedColor = color
                
### --------------------------------------------------------------------------------------------------
                    
    def SetClickedAndHighlightedColor(self, color):
        """ function to set the color of clicked and highlighted wells (mouse moves over them)
            no check for correct color yet
        """
        
        # is it really different?
        if color != self._clickAndHighColor:
            
            # update the member variable
            self._clickAndHighColor = color
          
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
    wellPlate = WellPlate(master)
    
    # draw our well plate
    wellPlate.Draw()
    
    # we cannot see anything yet, let's get started...
    master.mainloop()