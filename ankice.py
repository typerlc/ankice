# -*- coding: utf-8 -*-
import unicodedata, ctypes, sqlite3, socket
import os
import sys

def isWinCE():
    return os.name == 'ce'

if not isWinCE():
    print "This version of anki is for Windows CE devices only"
    sys.exit(1)

def winCEHacks():
    # assume additional libraries are in ../extlibs/
    top = os.path.dirname( os.path.dirname( sys.argv[0] ) )
    sys.path.append( os.path.join( top, 'libanki' ) )
    sys.path.append( os.path.join( top, 'extlibs' ) )

    # PATH not set on CE ... and anki tries a += op, so set to a dummy value
    os.environ['PATH']=""

    # over-ride some things that don't work on wince (at least on ce4.20)
    import shutil
    shutil.copy2=shutil.copy
    os.utime=lambda a, b: None

winCEHacks()



###########################################################

from threading import Thread
import time
import ppygui as gui

class AnkiCe( gui.CeFrame ):
    def __init__( self, app, config, args ):
        gui.CeFrame.__init__( self, title="Loading Anki..." )

        self.app = app
        self.config = config
        self.deck = None
        self.currentCard = None
        self.question = None
        self.answer = None

	try:
            self.font = gui.Font( size=12, charset='shift-jis' )
	except:
            self.font = gui.Font( size=12 )

        #self.content = gui.Edit( self, multiline=True, line_wrap=True, readonly=True )
        self.content = gui.Label( self )
        self.content.font = self.font
        self.setContent( "" )

        sizer = gui.VSizer()
        sizer.add(self.content)
        self.sizer = sizer

        self.ankiLoader = Thread( target=self.loadAnki )
        self.ankiLoader.start()

    def show( self, val=True ):
        gui.CeFrame.show( self, val )
        if val:
            self.bringtofront()

    def quit( self ):
        if self.deck:
            self.deck.save()
            self.deck.close()
        self.app.quit()

    def setContent( self, text ):
        self.content.text = text

    def loadAnki( self ):
        global anki
        anki = __import__( 'anki' )
        self.version = anki.version
        self.text = "Anki " + self.version
        gui.schedule( self.loadDeck )

    def loadDeck( self ):
        if self.deck: self.deck.close()

        deckname='testdeck.anki'

        self.text = "Loading deck ..."
        self.deck = anki.DeckStorage.Deck( deckname, rebuild=False )
        self.text = "Rebuilding queue ..."
        self.deck.rebuildQueue()
        self.text = "Anki " + self.version

        self.showQuestion()

    def submitAnswer( self, ease ):
        self.deck.answerCard( self.currentCard, ease )
        self.deck.currentCard = None
        self.showQuestion()

    def sleepForQuestion( self ):
        self.refreshTimer = None
        time.sleep( 5 )
        gui.schedule( self.showQuestion )

    def showQuestion( self ):
        if not self.deck:
            self.setContent( "Failed to load: " + deckname )
        else:
            self.currentCard = self.deck.getCard()
            if not self.currentCard:
                self.setContent( "Deck is finished!\r\n\r\nNext due in %s" % self.deck.earliestTimeStr() )
                self.deck.s.flush()
                self.refreshTimer = Thread( target=self.sleepForQuestion )
                self.refreshTimer.start()
            else:
                if not self.question:
                    self.question = QuestionFrame( self )
                self.question.setContent( "Q: " + self.currentCard.question.replace( "<br>", "\r\n" ) )
                self.hide()
                self.question.show()

    def showAnswer( self ):
            if not self.answer:
                self.answer = AnswerFrame( self )
            self.answer.setContent( "Q: " + self.currentCard.question.replace( "<br>", "\r\n" ) + "\r\n\r\n" +
                                    "A: " + self.currentCard.answer.replace( "<br>", "\r\n" ) )
            self.answer.show()

    def setLang( self ):
        pass

    def setupFonts( self ):
        pass

    def setupButtons( self ):
        pass

class QuestionFrame( gui.CeFrame ):
    def __init__( self, mw ):
        gui.CeFrame.__init__( self, title="Question" )
        self.mw = mw
        self.bind(destroy=lambda event : self.mw.quit())

        self.font = gui.Font( size=12, charset='shift-jis' )
        self.content = gui.Label( self )
        self.content.font = self.font
        self.setContent( "" )

        spacer = gui.Spacer( 1, None )
        button = gui.Button( self, "Show answer" )
        button.bind( clicked=self.on_click )

        self.sizer = gui.VBox(border=(2,2,2,2), spacing=2)
        self.sizer.add( self.content )
        self.sizer.add( spacer )
        self.sizer.add( button )

    def show( self, val=True ):
        gui.CeFrame.show( self, val )
        if val:
            self.bringtofront()

    def setContent( self, text ):
        self.content.text = text

    def on_click( self, event ):
        self.hide()
        self.mw.showAnswer()

class AnswerFrame( gui.CeFrame ):
    def __init__( self, mw ):
        gui.CeFrame.__init__( self, title="Answer" )
        self.mw = mw
        self.bind(destroy=lambda event : self.mw.quit())

        self.font = gui.Font( size=12, charset='shift-jis' )
        self.content = gui.Label( self )
        self.content.font = self.font
        self.setContent( "" )

        spacer = gui.Spacer( 1, None )

        hbox = gui.HBox(border=(2,2,2,2), spacing=2)
        button0 = gui.Button( self, "  0  " )
        button0.bind( clicked=self.on_click0 )
        button1 = gui.Button( self, "  1  " )
        button1.bind( clicked=self.on_click1 )
        button2 = gui.Button( self, "  2  " )
        button2.bind( clicked=self.on_click2 )
        button3 = gui.Button( self, "  3  " )
        button3.bind( clicked=self.on_click3 )
        button4 = gui.Button( self, "  4  " )
        button4.bind( clicked=self.on_click4 )
        hbox.add( button0 )
        hbox.add( gui.Spacer(None,1) )
        hbox.add( button1 )
        hbox.add( gui.Spacer(None,1) )
        hbox.add( button2 )
        hbox.add( gui.Spacer(None,1) )
        hbox.add( button3 )
        hbox.add( gui.Spacer(None,1) )
        hbox.add( button4 )

        self.sizer = gui.VBox(border=(2,2,2,2), spacing=2)
        self.sizer.add( self.content )
        self.sizer.add( spacer )
        self.sizer.add( hbox )

    def show( self, val=True ):
        gui.CeFrame.show( self, val )
        if val:
            self.bringtofront()

    def setContent( self, text ):
        self.content.text = text

    def on_click0( self, event ):
        self.mw.show()
        self.hide()
        self.mw.submitAnswer(0)
    def on_click1( self, event ):
        self.mw.show()
        self.hide()
        self.mw.submitAnswer(1)
    def on_click2( self, event ):
        self.mw.show()
        self.hide()
        self.mw.submitAnswer(2)
    def on_click3( self, event ):
        self.mw.show()
        self.hide()
        self.mw.submitAnswer(3)
    def on_click4( self, event ):
        self.mw.show()
        self.hide()
        self.mw.submitAnswer(4)

def main():
    app = gui.Application()
    mw = AnkiCe( app, None, None )
    app.mainframe = mw
    mw.bind(destroy=lambda event : mw.quit())
    app.run()

if __name__ == '__main__' : main()
