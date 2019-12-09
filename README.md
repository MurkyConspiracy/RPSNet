Nicholas Reeder
Python Scripting

RPSNet: an AWS based Rock, Paper, Scissors game client!
***IMPORTANT NOTICE***
RPSNet is running on my personal AWS and will only be available until January first, 2020. I have provided video proof of the software running and working as intended in case something happens between now and then. All code will be submitted to my course, as well as posted on GitHub publicly.

Video explanation/Walkthrough:
https://www.youtube.com/watch?v=tNorctURtrQ&feature=youtu.be

Public GitHub:
https://github.com/MurkyConspiracy/RPSNet

RPSNet is roughly 1100 lines of code, it isn’t perfectly optimized, however it gets the job done, and done well. As long as the intention of the player is not to exploit the system, it works as intended. There are plenty of cautionary measures in place, however there are a few security flaws here and there. The data is also not encrypted so players could edit their stats.

All of the python code is commented with what it does to a point, however I did not annotate it line by line. The game is broken up into two different system: Client, Server.

Client:

The Client (GameClient.py) houses and runs the game itself, and is a GUI based RPS game. GameClient.py handles all server sent data such as player lists, game requests, score updates, login messages, etc. GameClient.py uses a class system as to encapsulate all of the data, doing so makes it easier to keep things stable. It also helped me avoid multithreading on the client, do to everything being a self-handled method. Game client can run on Windows and Linux without issue; however, it seems to run better on Windows machines.

Server:

The Server (RPSNet-server.py) houses all the game logic, and back end login details, as well as storage for requests, player data, scoring, etc. RPSNet-server.py uses multithreading to handle incoming requests and sends clients any data is asks for in a reasonable manner. The Server is much more compact than the client, but still creates a server object, however not all methods are object methods.



