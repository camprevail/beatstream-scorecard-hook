# Beatstream Scorecard ~~Hook~~
#### *It's not really a hook lol but it sounds more pro*

This program fetches score data from beatstream animtribe and sends it off to a scorecard server. The server 
should return an image file and the program will download and save it locally, and optionally upload it to discord.

### *But why? Beatstream already has a scorecard button built-in.*
I made this as a temporary solution until my server of choice supports the game's built-in scorecard function (which is still 
just an xml request containing stage data) and the scorecard generator I wrote, and also as an excercise to see I could figure out where stage data was stored 
in the game and if python was able to retrieve it, since I don't know enough cpp to make an actual hook or any of this in 
another language. Needless to say the venture was successful. 

# Installation
Current version: 1.0  
[Grab the latest release here](https://github.com/camprevail/beatstream-scorecard-hook/releases/latest).  
Place the main exe, config.ini and dx9osd64.dll in your game's contents folder.  If you're using this on a cab, see the note at the bottom.  
Edit your gamestart.bat - add `start bst-scorecard-hook.exe` on a line above launcher or spice64 so it runs in the 
background, and add -k dx9osd64.dll to your launcher/spice arguments. (capital -K for launcher).  
Open config.ini and add the scorecard generator url if it was not included (I won't be posting my server url to github but 
you can ask me for it on discord). Be sure to go over the rest of the settings while you're in there.  
PC users will need to make the program run as admin in the file properties, cabs will run it as admin automatically. Start 
it manually once to make sure it runs, optionally change the key mapping by pressing F12.  
If everything looks good, close it and launch your gamestart.bat.


**Cab Owners: you'll need to put 
`api-ms-win-core-path-l1-1-0.dll` in c:\windows\system32 and make sure the system clock is up to date. Run `timedate.cpl`, sync the 
time in the dialog and then run `ewfmgr c: -commit & shutdown /r /t 0` to save the changes.


# Usage
The default key bindings are as follows:
```
ESC - Exit (not configurable)
F12 - Remap keys (not configurable)
current stage: `/~
stage 1: 1
stage 2: 2
stage 3: 3
stage 4: 4
```
Press the current stage key when you complete a song to generate a scorecard. A message should pop up in the middle of the 
screen saying either Scorecard Saved or Scorecard Failed. If it failed or no message appeared, check the console to see what 
went wrong.  
The reason for individual stage keys is in case you missed/forgot it during the results screen. You can grab the score from
any stage you have already completed until the game logs you out. A warning will be printed to the console if you try to 
grab stage data before a song is complete.  

<img src="images/scorecard-example.png" width="500">
<br><br>
<img src="images/osd-example.png" width="500">


## External Links
dx9osd - https://github.com/setsumi/dx9osd  
api-ms-win-core-path dll - https://github.com/nalexandru/api-ms-win-core-path-HACK  
-- This is an implementation of api-ms-win-core-path-l1-1-0.dll based on Wine code. It is made to run Blender 2.93 
(specifically, Python 3.9) on Windows 7.  
bemani-scorecards - https://github.com/camprevail/bemani-scorecards