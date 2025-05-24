# HA_SaveEditor
Savegame Editor for Hollywood Animals
Currently, the stable version of the save editor allows the user to edit:

Studio stats:
Budget (maxed out at 1 billion), cash, reputation and influence.
Max plot elements (max 10), max contract years/movies (currently both maxed out at 10).

Cinemas:
Number of total cinemas and the number of cinemas owned by each studio. The remaining (independent cinemas) are shown but not modifyable. If the total number of cinemas owned by studios exceed the number of total cinemas available, independent cinema will be shown in red as a warning.

Policy:
User can alter the studio policy at wish (once studio policy is unlocked).

Version info:
The version of the first savegame in this playthrough and the current version of the game.

I have uploaded a compiler as well for those who don't want to bother figuring out how. As long as you have python and pyinstaller installed and put the py file and the bat file in the same folder, it should be able to turn it into an exe file in a folder named dist.
