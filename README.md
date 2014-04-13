RogueDetective
==============

A python + curses-based roguelike centered around solving a murder, originally started as part of the 7DRL contest. It didn't make the deadline (not by miles), and is still in active development.

Prerequisites
=============

Linux: 
* Python (2.7 or greater)
* ncurses (Tested with 5.9-6)

Windows:
* Python (2.7 or greater)
* Unoffical [curses binary for Python](www.lfd.uci.edu/~gohlke/pythonlibs/)

Yeah, I managed to write something that isn't terribly portable. It may work on earlier Python versions, but I've almost certainly got some backwards-incompatible stuff in there somewhere.

In the future, I'll be investigating py2exe for creating binaries, but until then.. You're gonna have to deal with the prereqs.

Running
=======

On both Linux and Windows,
    python main.py
will run the game.

Windows Note
============

The wall characters may draw incorrectly on your system. To fix this, run
    chcp 437
before you call
    python main.py

This doesn't do anything changes, it simply changes the code page that the console uses for that session. It will revert once you close cmd.exe.