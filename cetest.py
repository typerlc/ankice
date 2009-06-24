# -*- coding: utf-8 -*-
import os
import sys

def isWinCE():
    return os.name == 'ce'

if not isWinCE():
    print "This version of anki is for Windows CE devices only"
    #sys.exit(1)

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

def testGui(txt):
    import ppygui as gui

    class MainFrame(gui.CeFrame):
    # subclass to create our own main frame type
        def __init__(self, title="MainFrame", txt=""):
             gui.CeFrame.__init__(self, title=title)
             #self.button = gui.Button(self, "Press me")
             self.font = gui.Font(charset='japanese', size=12)
             self.button = gui.Button(self, txt)
             self.button.font = self.font
             self.label = gui.Label(self, txt)
             self.label.font = self.font
             self.text="blahblah"

             sizer=gui.VBox(border=(2,2,2,2), spacing=2)
             sizer.add(self.button)
             sizer.add(self.label)
             self.sizer=sizer

    app = gui.Application(MainFrame(title=txt, txt=txt))
    # create an application bound to our main frame instance
    
    app.run()
    #launch the app !    


def testAnki():
    rv=""
    try:
        print "loading anki"
        import anki
        # Open a deck:
        print "loading deck"
        deck = anki.DeckStorage.Deck( 'testdeck.anki', rebuild=True, backup=True, lock=True )
        print "deck loaded"

        # Get a card:
        card = deck.getCard()
        if not card:
            print "deck is finished"
        # Show the card:
        else:
            print "hi"
            rv=card.answer
            print card.question, card.answer

        # Answer the card:
        #deck.answerCard(card, ease)
        #Edit the card:
        #fields = card.fact.model.fieldModels
        #for field in fields:
        #    card.fact[field.name] = "newvalue"
        #    card.fact.setModified(textChanged=True)
        #    deck.setModified()

        #Get all cards via ORM (slow):
        #    from anki.cards import Card
        #    cards = deck.s.query(Card).all()
        #

        #Get all q/a/ids via SQL (fast):
        #cards = deck.s.all("select id, question, answer from cards")
        #print cards

        #Save & close:
        #deck.save()
        deck.close()
    except Exception:
        e, v, t = sys.exc_info()
        print "Exception:", sys.excepthook( e, v, t )

    return rv

def main():
    txt = testAnki()
    #txt = u"日本語"
    #txt = u"にほんご"
    #txt = "hi"
    if isWinCE():
        testGui(txt)
        #import time
        #time.sleep(60)
    else:
        x=sys.stdin.readline()



if __name__ == '__main__' : main()
