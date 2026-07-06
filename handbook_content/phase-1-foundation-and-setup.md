This is an automatically generated documentation consolidation from https://en.doc.boardgamearena.com/. The complete handbook is available as Developer_Handbook_v1.md.

## Chapter 1: Introduction to BGA Studio

### What is Board Game Arena Studio?

Board Game Arena Studio is a platform to build online board game adaptations using the Board Game Arena platform. It provides developers with the tools, framework, and infrastructure needed to create digital versions of board games that can be played by millions of users worldwide.

**BGA Studio website**: https://studio.boardgamearena.com

### Discover BGA Studio in 5 Presentations

To get started with BGA Studio, the platform provides five introductory presentations that cover the essential aspects of game development:

1. **5 reasons why you should use BGA Studio for your online board game** - Explains the benefits and advantages of the platform
2. **The 8 steps to create a board game on Board Game Arena** - A complete walkthrough of the development process
3. **The BGA Framework at a glance** - Overview of the technical framework and architecture
4. **Focus on BGA game state machine** - Deep dive into the state machine system that controls game flow
5. **BGA developers guidelines** - Best practices and standards for BGA development

These presentations provide an excellent foundation for understanding both the "why" and "how" of BGA Studio development.

### Is BGA Studio Development Right for You?

Before diving into BGA Studio development, it's important to assess whether it aligns with your goals and skills.

**BGA Studio is right for you if:**
- You like board games and programming and think it would be a good hobby
- You really want to fix bugs in already published games
- You want to create a game from public domain (e.g., Chinese checkers, bridge, etc.)
- You were hired or persuaded by somebody else to create game adaptations on BGA

**BGA Studio is NOT right for you if:**
- You think you can implement any of the games from the top 100 on BoardGameGeek (BGG doesn't have licenses for most of these, or they're already implemented)
- You're an amateur game designer wanting to playtest your prototype (BGA players prefer known games, and digital adaptations are expensive)
- You're trying to create something that's not a board game adaptation (video games, skill tests, etc.)
- You're a student who just took your first programming course (BGA Studio requires significant web development experience)
- You expect to make a lot of money (while possible to earn some, it's not a primary income source)

### Required Skills for BGA Studio Projects

BGA Studio development requires proficiency in multiple technologies and concepts:

**Languages you need to know or learn:**
- JavaScript
- PHP
- SQL
- HTML
- CSS
- English (for documentation and communication)

**Technical concepts you need to understand:**
- Object-oriented programming
- Web development fundamentals
- Database development
- Development tool setup and remote file synchronization
- Image manipulation software (Paint.net, Gimp, Photoshop, etc.)
- Research skills - knowing how to Google and read documentation

### What is Expected from Volunteer Developers

As a volunteer developer for BGA:

- **Nothing is really expected** - but don't expect much from others either
- If you publish a game, it's expected you'll fix bugs, but nobody can force you to (though games may be taken down if no maintainer can be found)
- The code you write remains with BGA (they can do whatever they want with it), but you keep rights to your own copy
- Documentation, forums, and chat with other developers are available for help

### What You Get Out of It

- **Fun and satisfaction** - Developing a game is enjoyable, and you do it all by yourself
- **Skill improvement** - Greatly improve your web development skills with ancient web technology and small databases
- **Industry connections** - Talk directly to game publishers and designers of your favorite games
- **Recognition** - Eventually become famous in small circles of BGA players who read credits

### How to Create a BGA Studio Development Account

Registering on BGA Studio is simple and automatic:

1. Go to https://studio.boardgamearena.com/
2. Find the section "Join the BGA Studio developers team" (you may need to scroll down)
3. Fill out the form and submit
4. If you don't see the form, you're already logged in and registered

To register, you must agree with BGA Terms & Conditions for developers (very light terms to get you to the fun part faster).

**What you receive after registration:**
- One login/password to access files through SFTP
- One login/password to access the database (for your games in progress)
- Ten logins with numeric suffixes (dev0-dev9) for testing with multiple players
- One "admin" login to manage projects

### First Steps with BGA Studio

#### Connect to the BGA Studio Website

Go to the BGA Studio website: http://studio.boardgamearena.com

If you don't have an account, see the section above on creating a development account.

#### Create a New Game Project

Most project-related operations can be done from "Control Panel / Manage games":

1. Click on your profile icon on the top right of any page
2. Click on the Control Panel button (top right, only visible for developer accounts)
3. Click on the "Manage Games" button on the left side of the page

For your first game, start with a tutorial. Your project name should be something like "tutorialbob". Type "0" for Board Game Geek ID and click "Create Project." The new project will appear after you refresh the page.

**Useful Studio Links:**
- **AVAILABLE LICENSES** - List of all available licenses (not public domain): https://studio.boardgamearena.com/licensing
- **STUDIO PROJECTS** - List of all registered studio projects: https://studio.boardgamearena.com/projects
- **CONTROL PANEL** - Manage projects: https://studio.boardgamearena.com/controlpanel (accessible from player popup menu with gear and bargraph blue icon)

#### Set Up Development Environment

From your initial Studio email, you receive:
- The name of the SFTP server to connect to
- Your SFTP login and password

**Important:** This is NOT the same login/password as your dev account. Find the email that talks about SFTP specifically.

**Development Setup Steps:**
1. Your projects are listed in the "home" folder. If you created a new game project, you should see a folder with the project name.
2. To see tutorial projects, go to https://studio.boardgamearena.com/projects, select "Already published," search for "Reversi" or any project, then click "[Get readonly access]." The game folder will be visible in your FTP home folder in read-only mode.
3. Connect to the SFTP server using your SFTP login and password through your favorite SFTP client or IDE integration.
4. Download the remote project folder into a local folder.
5. **Critical:** You must set up AUTOMATED sync between your local and remote folders. Manual FTP file transfers are not sustainable.
6. You can upload your SSH key via the studio control panel to avoid password exchange: https://studio.boardgamearena.com/controlpanel

#### Let's Code!

Now you can launch a new game on BGA Studio from the "Play now" menu:

1. To launch your game from Studio, go to CONTROL PANEL → Manage games → <your_game> → <your_game_page> → Play, or use the direct link: https://studio.boardgamearena.com/studiogame?game=<your_game>
2. Press "Create" to create a table
3. Select the number of players and select "Training mode" in the game configuration panel
4. Click "Express start" (do not use "Start game" buttons in Studio - they add unnecessary complexity). Express start launches your game with the maximum number of players using your dev player accounts (dev0, dev1, dev2, etc.). For Solo mode, use "Start Game" instead.
5. The game opens with an empty canvas - just an empty div for player tables and a fake counter space on each player panel.
6. Switch to your SFTP home folder, go into your game folder, and edit the <your_game>.js file (tutorial: modules/js/Game.js). Add a sentence in the HTML part of the line `this.getGameAreaElement().insertAdjacentHTML`, then save.
7. Go back to your browser and refresh to see the game zone update.
8. Click the red arrow next to a test account's name in the player panel to view the game from that player's perspective.
9. Open the menu (three-line "hamburger" icon at the upper right) and choose 'Express STOP' to end the game automatically.

### BGA Game Licenses

#### What is a "License"?

Almost all games on the Board Game Arena platform are adaptations of existing commercial "real" board games. To host an adaptation of one of these board games on a website, the copyright owners must grant a license/authorization to the website.

#### Are All Games on BGA Licensed?

Yes, for all games that are not in the public domain, BGA has been granted authorization to create and host an online version.

#### Available Licenses List

Check the list of available licenses to see which games BGA can legally implement.

#### What If You Start Developing a Game Not on the Available Licenses List?

BGA allows developers to start any project in the Studio. However, when you submit your project to go live on BGA, it will be rejected during the review process if BGA doesn't hold a proper license for the game.

#### Developing a Game from the Available Licenses List

If you want to develop a game from the available licenses list:

1. Check the list of current projects to see if anyone is already working on it
2. Try establishing contact with the publisher or designer before developing
3. To release as a public game, the publisher must approve during the alpha test phase. Without publisher support, your game will remain private indefinitely.

#### Adding a Game to the Available Licenses List

The copyright owners must grant a license/authorization to BGA. This is typically handled by BGA directly with publishers.

#### Why Aren't All Popular Games on the List?

The more popular a game is, the more difficult it can be to get an agreement to host it on BGA. While BGA has convinced many prestigious publishers, they can't convince everyone.

#### Developing Your Prototype/Unpublished Game

This is possible but generally discouraged because:

- If your game hasn't been published, there's usually a reason - it likely needs more work. Publishing on BGA won't help finalize it.
- Popular BGA games are popular in the real world. Prototypes likely won't get a big audience.
- Game adaptations work better when there's a designer focused on gameplay and a developer focused on implementation.

**Consider developing your prototype if:**
- The game is going to be published in the near future
- The game design is 100% done and ready to publish (self-publishing, crowdfunding, etc.)
- You want to test with many players to fine-tune minor things (balance)

**Note:** Games that cannot be bought will not be published on BGA. They won't go beyond private alpha, so you'll only be able to play with friends.

#### Developing a Game Not on the Available Licenses List

If you really want to develop a particular game not on the list, follow this process:

**0: The game is popular**
If the game is already popular (top 1000 on BGG), BGA likely already contacted them. Check with the dev team on the forum or Discord to see if anyone has more information.

**1: Determine the Publisher**
Find who owns the digital rights. Usually this is the original publisher:
- Check which country the game was first published in (the original publisher is likely from that country)
- Check BoardGameGeek for publisher information
- If the publisher doesn't hold digital rights, they may direct you to the rights holder

**2: Check Publisher Contact**
Search for publisher contact information on their website or BoardGameGeek.

**3: Contact the Publisher**
When contacting publishers:
- Be professional and concise
- Explain you're a BGA developer interested in creating a digital adaptation
- Mention your experience and any previous BGA projects
- Ask if they hold digital rights and would be interested in licensing to BGA

**4: Follow Up**
Publishers are busy. If you don't hear back in 2-3 weeks, send a polite follow-up.

**5: Contact BGA Studio**
If the publisher is interested, have them contact BGA Studio at studio@boardgamearena.com to discuss licensing terms.

### Contact BGA Studio

#### Purpose

This page helps find solutions for technical issues or manual steps related to game development on BGA Studio.

If you're a publisher who couldn't reach BGA through normal channels, you can go to the Developer discord server and ask for developers on the #looking-for-developers channel.

#### Studio Accounts Management

BGA player accounts are different from studio accounts (even if you name them the same).

**Account Management:**
- Create studio account: https://studio.boardgamearena.com (logout first if already logged in)
- Resend welcome email: https://studio.boardgamearena.com/account?page=welcomeemail (same for forgotten database or FTP accounts)
- If you still can't get the email (checked junk folder), contact studio via https://studio.boardgamearena.com/support
- Forgot password: https://studio.boardgamearena.com/account?page=lostpassword
- Upload SSH key: https://studio.boardgamearena.com/controlpanel

#### Studio Games Management

**Game Management Control Panel:**
- Located in Gear link when you click on your Account circle
- Direct link: https://studio.boardgamearena.com/controlpanel
- Allows you to create projects, delete projects, and manage projects

**Access to Other Project's Source Code:**
- Any developer can add themselves to a project as read-only from https://studio.boardgamearena.com/projects (almost any project)
- If a project isn't there, it either has no BGG ID, is already published (check radio button on the page), or wasn't developed on Studio (some old games)
- You can also try the direct link: https://studio.boardgamearena.com/gamepanel?game=template (replace "template" with game name)
- If you prefer GitHub, see https://en.doc.boardgamearena.com/BGA_Code_Sharing

**Access to Frontend:**
- Even without source access, you can see Java code, CSS, and image assets using browser dev tools (see Practical_debugging)

**Push Game to Alpha or Beta:**
- You cannot do this yourself
- Complete the checklist first: https://en.doc.boardgamearena.com/Pre-release_checklist
- Use "Request Alpha" or "Request Beta" button in control panel

**Project Restoration:**
- If your project seems deleted after you return a year later, create a new project with the SAME name (you must remember the name) - it will be restored

**Permission Issues:**
- If you have permission issues syncing files but you're admin, re-add yourself as admin via control panel. DO NOT delete yourself - select "Admin" (double-check you selected Admin, not Read/Write), type your name, and click add.
- If you managed to delete yourself from your own project or are no longer admin, this requires admin intervention - contact studio via https://studio.boardgamearena.com/support

**Take Over Abandoned Game:**
- First ask the developer (via PM, dev forum, or Discord) - it may not actually be abandoned
- Contact Studio support to ask for access: https://studio.boardgamearena.com/support

**Error Creating New Game:**
- If you get "Not authorized adminstudionewproject" error, wait a little longer and try again

#### Help with Game Development or Setup

If you're stuck or looking for help with development (even if you think there's a bug in the framework), contact fellow developers first before attempting to contact admins.

**Resources for Help:**
- Google it - you may find answers unrelated to BGA
- Check the Studio FAQ
- Check the Studio forum
- Join the BGA Developer Discord server
- Search existing game source code for examples

**When to Contact Studio Support:**
- Account-related issues (after trying above resources)
- Game project management issues
- Licensing inquiries (for publishers)
- Bug reports in the framework itself

---

## Chapter 2: Development Environment Setup

### Choosing and Setting Up Your Development Environment

A proper development environment is crucial for efficient BGA Studio development. This chapter covers setting up Visual Studio Code, the recommended IDE for BGA development.

### Visual Studio Code Setup

Microsoft Visual Studio Code is a lightweight IDE/editor available for all desktop platforms. It's the recommended choice for BGA Studio development.

**Download VSCode:** https://code.visualstudio.com

**Optional:** Download and install PHP (8.4) command line interface for local tests and debugging.

### Recommended VSCode Extensions

Use the **BGA Extension Pack** to download all recommended extensions with one click.

**Essential Extensions:**

1. **PHP Intelephense** - https://marketplace.visualstudio.com/items?itemName=bmewburn.vscode-intelephense-client
   - OR PHP IntelliSense - https://marketplace.visualstudio.com/items?itemName=zobo.php-intellisense
   
2. **PHP Debug** - https://marketplace.visualstudio.com/items?itemName=xdebug.php-debug

3. **SQLTools** - https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools

4. **Prettier** - Code formatter - https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode

5. **SFTP (by Natizyskunk)** - https://marketplace.visualstudio.com/items?itemName=Natizyskunk.sftp

### Intellisense and Auto-complete

#### JavaScript Intellisense

Since BGA adopted ES Modules and modernized the framework, we can enjoy full IDE support. If you try this with legacy Dojo projects, it may not work well.

A good way to improve auto-complete is to use TypeScript and SCSS (not required for beginners). See the original wiki: https://en.doc.boardgamearena.com/Using_Typescript_and_Scss

**Note:** The modern framework still uses Dojo libraries (ebg/stock, ebg/zone) internally, so understanding the legacy patterns remains useful.

#### PHP Intellisense

The "_ide_helper.php" file, included in every project, helps your IDE understand the available framework functions. This file may be updated automatically on your FTP folder, so don't hesitate to pull it back if it seems incomplete.

**Option 1: Define class attributes**
If you have `$this->token_types = [...]` in the material file, define them in your Game.php class:
```php
private array $token_types;
```

**Option 2: Disable undefined property warnings**
Add this to your VSCode settings:
```json
"intelephense.diagnostics.undefinedProperties": false
```

#### Unit Testing

If using PHPUnit, install it via Composer in your home directory:
```bash
cd /home/<yourusername>/php-composer
composer require --dev phpunit/phpunit ^13
```

Add this path to include paths in settings:
```json
"intelephense.environment.includePaths": [
    "/home/<yourusername>/php-composer"
]
```

See more about unit testing in "Testing by developer."

### File Sync Setup

You can set up sync using other methods (like rsync) - see Tools_and_tips_of_BGA_Studio#File_Sync. For VSCode, use the SFTP extension:

**Setup Steps:**

1. Install the SFTP extension: https://marketplace.visualstudio.com/items?itemName=Natizyskunk.sftp (File→Preferences→Extensions, type "SFTP", ensure it's by Natizyskunk)

2. Open VSCode on an empty folder that will be the local root of your project

3. Execute Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac) to open the command palette, then type/run: "SFTP: config" - this opens a JSON config file

4. Update the JSON as follows:
```json
{
    "name": "BGA",
    "host": "1.studio.boardgamearena.com",
    "protocol": "sftp",
    "port": 2022,
    "username": "<your SFTP username>",
    "password": "<your SFTP password>",
    "remotePath": "/<your project name>/",
    "uploadOnSave": true,
    "ignore": [
        ".vscode",
        ".git",
        ".DS_Store",
        "package-lock.json",
        "yarn.lock",
        "misc",
        "node_modules",
        "_ide_helper.php",
        "bga-framework.d.ts",
        "**",
        "sync-helper.php"
    ],
    "watcher": {
        "files": "*",
        "autoUpload": false,
        "autoDelete": false
    }
}
```

**Important Notes:**
- Replace `<your SFTP username>`, `<your SFTP password>`, and `<your project name>` with your actual values
- The "ignore" array prevents unnecessary files from being synced
- "uploadOnSave": true automatically uploads when you save files
- Consider using SSH keys instead of passwords for better security

### Studio File Reference

This is a quick reference for the files used to implement a game. For detailed information, follow the wiki links.

#### File Structure Overview

**img/**
- Contains the images for your game (game art)
- See: Game art: img directory

**gameinfos.jsonc**
- Describes meta-information for your game: game name, publisher name, number of players, etc.
- See: Game meta-information: gameinfos.jsonc

**dbmodel.sql**
- Creates specific database tables needed to persist data during the game (e.g., table for cards)
- See: Game database model: dbmodel.sql

**gameoptions.json, gamepreferences.json**
- Describes your game options (or game variants)
- See: Options_and_preferences: gameoptions.json, gamepreferences.json

**<gamename>.css**
- CSS styles specific to your game
- See: Game interface stylesheet: yourgamename.css

**modules/php/Game.php**
- Main file for your game logic. Initialize the game, persist data, implement rules, and notify changes to the client interface
- See: Main game logic: Game.php

**modules/js/Game.js**
- Main file for your game interface. Define:
  - Which actions on the page generate calls to the server
  - What happens when you get notifications for changes from the server and how to show them in the browser
- When this file changes, do a simple reload (F5) of the currently running game

**<gamename>.view.php, <gamename>_<gamename>.tpl**
- **DEPRECATED:** You shouldn't need these if you generate the template from the JS file
- When these files change, do a simple reload (F5)

**material.inc.php**
- **DEPRECATED:** See the dedicated page for more information
- When this file changes, reloading is not required, but if your JS uses data from it, do a simple reload (F5)

**modules/php/States/**
- Classes describing the states of your game

**states.inc.php**
- **DEPRECATED:** You shouldn't need to change this if you use State classes
- When this file changes, it requires a simple reload; if changes are breaking, you need to start a new game

**stats.json**
- Lists statistics to update during the game for presentation to players at the end
- See: Game statistics: stats.json

**modules/**
- Can contain additional PHP files to include in main game.php via include or require
- Can contain additional JS files
- This directory is checked in version control

**misc/**
- Contains files to keep with the project but not needed on the production server
- This directory is checked in version control
- Total limit is 1 MB for this directory

**<other files>**
- You can use other files, but they won't be checked in source control or published in production
- This includes any additional .js or .php files
- If you need them, use the modules/ directory

### Tools and Tips for BGA Studio

#### Server Tools and Tips

**Starting a Game in One Click:**
1. Go to "Play now" and configure game type: Simple game → Turn-based → Manual
2. Select your game and click "Create"
3. If you want to play with 3 players, specify a maximum of 3 players at this table
4. Click "Express Start"

**Stopping a Game in One Click:**
1. Click the "menu" icon on the top right of the screen
2. Click "Express Stop" (or "Quit this game" if playing a solo game)

**Switching Between Users:**
When running a game on Studio, use the little red arrow near each player's name to open a new tab with that player's perspective. You can also modify the URL to view the table as any user (changing &testuser=myid in the URL), allowing you to easily test as a spectator.

**Access to Game Database and Logs:**
At the bottom of the game area, there's a section with 3 useful links:
- "Go to game database" - Immediate access to PhpMyAdmin to view/edit tables of the current game
- "BGA request&SQL logs" - Link to your studio PHP log - all tables, all severities. Anything you print using debugging and tracing functions from PHP and some framework logs
- "BGA unexpected exceptions logs" - Same log as above but only severity warning and higher

See "Practical debugging" for more information.

**Save & Restore State:**
Using these links, you can save the complete current (database) state of your game, then restore it later. You get 3 "slots": 1, 2, and 3.

**Important notes:**
- The "restore" function doesn't work when the game is over
- A saved situation from a given table cannot be restored in another table
- When you "restore" a situation, the current browser page refreshes, but you have to refresh other tabs manually

**Input/Output Debugging Section:**
This section shows:
- AJAX calls made by your game interface to the game server (outputs begin with ">")
- Notifications received by your game interface (inputs begin with "<")

**Note:** If you click on a notification title, you can resend it immediately to the user interface.

**Zombify a Player:**
Using the red arrow, go to the player view and select "Quit game" (make sure you're playing in friendly mode to avoid your studio accounts going to 0 karma while testing zombie mode).

**Stopping Hanging Game:**
If a game is hanging and you cannot enter it to stop, type this URL (replace 12345 with your table number):
```
https://studio.boardgamearena.com/#!table?table=12345
```

#### Desktop and Web Tools

**Code Editors and IDEs:**

**Visual Studio Code**
- Lightweight IDE/Editor for all desktop platforms
- https://code.visualstudio.com

**Eclipse For PHP Developers**
- Eclipse PHP package can be a starting point for development
- You may want to install Tern JS plugins to understand Dojo-style JS
- All desktop platforms
- https://projects.eclipse.org/tools/phpeclipse

**Other Options:**
- Gedit (Linux)
- Sublime Text
- Notepad++ (Windows)
- Any editor that supports PHP/JavaScript syntax highlighting

**Image Editing Software:**
- Gimp (free, open source)
- Paint.net (free, Windows)
- Adobe Photoshop (commercial)
- Any image editor that can handle transparent PNGs

**Debugging Tools:**
- Browser developer tools (Chrome DevTools, Firefox Developer Tools)
- PHP debugging extensions
- Database tools (PhpMyAdmin for remote access)

---

## Chapter 3: Game Project Fundamentals

### Understanding BGA Game Project Structure

A BGA game project consists of multiple files and directories that work together to create a complete game implementation. This chapter covers the fundamental configuration files and their purposes.

### Game Meta-Information: gameinfos.jsonc

The gameinfos.jsonc file contains the meta-information for your game - game name, publisher, player counts, and other configuration settings.

#### Overview

From this file, you can edit various meta-information about your game.

**Note:** If you break gameinfos and cannot load the management page, reload using the direct URL: https://studio.boardgamearena.com/admin/studio/reloadGameInfos.html?game=<your_game_name>

#### Publisher Information

These fields should match the publisher of the game. For public domain games, leave them empty (empty string).

#### Time Profiles

**fast/medium/slow_additional_time:** Set high values here. After the game has been released, a process adjusts these values to match real game duration. Adjustment starts when the game enters beta; after that, these have no effect and require admin intervention to change.

#### Number of Players

```json
"players": [3, 4, 6]
```

**Important notes:**
- During the first step of development, it's recommended to have a "1 player" configuration - much easier to start/stop games without switching players
- If you change the minimum number of players from 1 to 2, make sure new tables you create aren't restricted from 1 to 1 player, otherwise you'll be blocked from creating the game
- You can unblock yourself by changing the number of players again, launching with a larger number, then returning to your desired number

```json
"suggest_player_number": 3,
"not_recommend_player_number": [6]
```

Don't specify anything here (null) if there's no configuration that's REALLY better/worse than another. You can check player polls on BoardGameGeek if you have doubts. Note:
- There can be at most one suggested player count (null or single number)
- There can be several not recommended player counts (null or array of values)

**Important exception:** In the automatic lobby, if 'suggest_player_number' is not specified, the system tries the lowest first. If the lowest player number isn't compatible with default options (especially if there's a Solo mode that can only be played in training mode), you must specify a suggest_player_number so players launching in the automatic lobby don't get errors with default configuration.

#### Player Colors

```json
"player_colors": ["ff0000", "008000", "0000ff", "ffa500", "ffffff"]
```

This array defines default player colors. It can be larger than the maximum number of players, but you must support all players in your game. Your setupNewGame in PHP is responsible for attributing these values to players. See "Player color preferences" in Main_game_logic:_yourgamename.game.php for details.

#### Minimum Screen Size

Settings to specify mobile (or small desktop) screen size are detailed here: https://en.doc.boardgamearena.com/Your_game_mobile_version

#### Losers Not Ranked Between Themselves

By default, all players are ranked, but in some games, rules say all non-winners are losers and not ranked between themselves. Set this to true so your game has only winners and losers, without full ranking of all players.

```json
// If in the game, all losers are equal (no score to rank them or explicit in rules that losers are not ranked between them), set this to true
// The game end result will display "Winner" for the 1st player and "Loser" for all other players
"losers_not_ranked": false
```

**Note:** In some team games like Tichu, Spades, and Belote, players don't gain or lose ELO by teammates (hover over ELO changes to find 'Teammate: -100%').

**Warning:** This modifier should NOT be applied to co-op games or games where 3 or more parties can compete (e.g., individual mode with 3+ players, 2v2v2 6-player mode, etc.).

#### Disable Player Rotation in Case of Rematch

By default, in case of a rematch, players are rotated so the first player changes. If it's better for your game to always have random player order, change this option.

```json
// When doing a rematch, the player order is swapped using a "rotation" so the starting player is not the same
// If you want to disable this, set this to true (even if the comment in your game file says the opposite)
"disable_player_order_swap_on_rematch": false
```

#### Deprecated Fields

The following fields are deprecated and should not be used:
- Game designer (`designer`)
- Game artist (`artist`)
- Year (`year`)
- Id (`id`)

### Game Database Model: dbmodel.sql

The dbmodel.sql file specifies the database schema of your game.

**Note:** You cannot change the database schema during the game.

#### Create Your Schema

To build this file, build the tables you need with the PhpMyAdmin tool (see the BGA user guide), then export them and copy/paste the content to this file.

**Example: Deck component (see Deck)**
```sql
CREATE TABLE IF NOT EXISTS `card` (
  `card_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `card_type` varchar(16) NOT NULL,
  `card_type_arg` int(11) NOT NULL,
  `card_location` varchar(16) NOT NULL,
  `card_location_arg` int(11) NOT NULL,
  PRIMARY KEY (`card_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;
```

**Example: Euro Game (see BGA_Studio_Cookbook#Database_for_The_euro_game)**
```sql
CREATE TABLE IF NOT EXISTS `token` (
  `token_key` varchar(32) NOT NULL,
  `token_location` varchar(32) NOT NULL,
  `token_state` int(10),
  PRIMARY KEY (`token_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

#### Database Design Rules

**Do not overcomplicate** - you're dealing with games with 50-500 pieces!
- If you have 5 tables for a card game with 30 cards, it's overkill

**The database should only store dynamic data** - all static data should be stored in the material file (PHP)
- Example: if cards have power, color, and special abilities, in the database only store the card type. All other properties should not be there unless they change during the game

**Columns should be permanent** - independent of game data (location, type, position, row, etc.)
- Example: do not create columns like Country1, Country2, Country3, etc.

**Do not store translatable strings in the database** - use an integer number "ident" to access properties
- Card type should be "22" or "bob_cat", not "Bob's cat"

**Create a separate module in PHP to handle all database queries** - do a lot of type checking to prevent SQL injections

**Example of method to handle a database query:**
```php
// Set token state
function setTokenState($token_key, $state) {
    self::checkState($state); // ensure state is number
    self::checkKey($token_key); // ensure key is alphanum
    $sql = "UPDATE `{$this->table}`";
    $sql .= " SET `token_state` = '$state'";
    $sql .= " WHERE `token_key` = '$token_key'"; // don't need to escape anymore since we checked key before
    self::DbQuery($sql);
    return $state;
}
```

#### Default Tables

By default, BGA creates four tables for your game: `global`, `stats`, `gamelog`, and `player`.

**The player table:**
You may add columns to the player table. It's very practical to add simple values associated with players. You must not alter existing columns created by the framework.

```sql
ALTER TABLE `player` ADD `player_reserve_size` SMALLINT UNSIGNED NOT NULL DEFAULT '7';
```

**Commonly used columns of the default "player" table:**
- `player_no`: The index of a player in natural playing order (starting with 1)
- `player_id` (int)
- `player_name`: Better to access with getActivePlayerName() or loadPlayersBasicInfos() methods
- `player_score`: Current score of a player (displayed in player panel). Update with $this->playerScore
- `player_score_aux`: Secondary score, used as tie breaker. Update with $this->playerScoreAux according to tie breaking rules (see: Manage_player_scores_and_Tie_breaker)

**player_table_order:** Gives an indication of the rank of the player by order of arrival in the lobby (starting with 1). It's not the same as player_no (player order within the game). player_table_order is useful for setting custom teams in game options (e.g., 1st-2nd vs 3rd-4th). Note: player_table_order only exists during game initialization (in setupNewGame function). It's not added as a column in the players Db table.

**CAUTION:** player_table_order is not guaranteed to equal the rank of the player in the table. For example, in a four-player game, if the table was full but the third player leaves before the game starts, the fourth player becomes third on the table but their player_table_no is still 4! If another player joins, their player_table_no will be 5. Thus, it's essential to normalize this value if you use it for anything.

### Game Material Description: material.inc.php

**IMPORTANT NOTE:** This file is not generated by default anymore, but you can still create it (the name is important - only a `material.inc.php` file at the root of your project will be automatically loaded) to describe the material of your game.

This file is included by the constructor of your main game logic (yourgame.game.php), and variables defined here are accessible everywhere in your game logic file (and also view.php file).

#### Definition

Example from "Eminent Domain":
```php
$this->token_types = [
 'card_role_survey' => [
   'type' => 'card_role',
   'name' => clienttranslate("Survey"),
   'tooltip' => clienttranslate("ACTION: Draw 2 Cards<br/><br/>ROLE: Look at <div class='icon survey'></div> - 1 planet cards, keep 1<br/> <span class='yellow'>Leader:</span> Look at 1 additional card"),
   'b'=>0,
   'p'=>'',
   'i'=>'S',
   'v'=>0,
   'a'=>'dd',
   'r'=>'S', 
   'l'=>'v',
  ],

 'card_tech_1_51' => [
   'type' => 'tech',
   'name' => clienttranslate("Improved Trade"),
   'b' => 3,
   'p' => 'E',
   'i' => 'TP',
   'v' => 0,
   'a' => 'i',
   'side' => 0,
   'tooltip' => clienttranslate("Collect 1 Influence from the supply."),
 ],
 // ... more cards
];
```

This defines all info about cards, including types, names, tooltips (to show on client), rules, payment cost, etc.

You can also define constants:
```php
if (!defined('TAPESTRY')) { // guard since this included multiple times
    define("TAPESTRY", 0);
    define("TRACK_EXPLORATION", 1);
    define("TRACK_SCIENCE", 2);
    define("TRACK_MILITARY", 3);
    define("TRACK_TECHNOLOGY", 4);
}
```

#### Access

**Data fields in PHP:**
```php
$type = $this->token_types['card_tech_1_51']['type'];
```

**Data fields in JavaScript:**
First, send all variables from material file via getAllDatas:
```php
protected function getAllDatas() {
    $result = array ();
    $result ['token_types'] = $this->token_types;
    // ...
    return $result;
}
```

Then access in JavaScript:
```javascript
var type = this.gamedatas.token_types['card_tech_1_51'].type; // not translatable
var name = _(this.gamedatas.token_types['card_tech_1_51'].name); // to be shown to user (NOI18N)
```

**Send in notification from PHP:**
```php
$this->notifyAllUsers('gainCard',clienttranslate('player gains ${card_name}'), [
    'i18n'=>['card_name'],
    'card_id' => $card_id,
    'card_name' => $this->token_types[$card_id]['name']
]);
```

**PHP constants in JavaScript:**
If you want to access constants in JavaScript, send them via getAllDatas:
```php
$cc = get_defined_constants(true)['user'];
$result['constants']=$cc; // this will be all constants, you may have to filter some for security
```

Alternatively, include material.inc.php in a local PHP file and call this method to print constants in JS format, then include this file in JS. You may have to synchronize manually, but it's better for auto-complete:
```php
// this needs to be run locally after including material file (see example in testing below)
$cc = get_defined_constants(true)['user'];
foreach ($cc as $key => $value) {          
    print ("const $key = $value;\n");
}
```

#### Testing

If you screw up your material file (missing brackets, etc.), it's very hard to diagnose. Test it locally:
```php
<?php
class material_test {
    function __construct() {
        include '../material.inc.php';
        var_dump($this->token_types); // whatever your var
    }
}
// stub
function clienttranslate($x) { return $x; }

new material_test();
```

#### Adjusting Material

In rare cases, expansions change the materials of the original game. It's possible to adjust material based on selected game options:

```php
/**
 * This is called before every action, unlike constructor this method has initialized state of the table so it can
 * access db
 *
 * @Override
 */
protected function initTable() {
    // this fiddles with material file depending on the extension selected
    $this->adjustMaterial();
}

function adjustMaterial($force = false) {
    if (!$force && $this->token_types_adjusted)
        return;
    $this->token_types_adjusted = true;
    // ... fiddle with data in material file
}
```

To adjust material itself, specify key postfixes that match your game option, and the adjustment function rewrites your keys:
```php
'card_tech_1_51' => [
   'name' => clienttranslate("Improved Trade"),
   'name@e3' => clienttranslate("Much Improved Trade"),
   'cost' => 3,
   'cost@p2' => 2
```

In this example, if player selects game expansion 3, key name@e3 overrides key name, and if there are 2 players, cost@p2 overrides cost. For exact code, check adjustMaterial in Ultimate Railroads.

### Players Actions: yourgamename.action.php

**IMPORTANT NOTE:** This file is deprecated. You shouldn't need it if you use Autowired action.

#### Purpose of This File

With this file, you define all player entry points (possible game actions) for your game. The role of methods defined here is to filter arguments, format them, and then call corresponding PHP methods from your main game logic ("yourgame.game.php" file).

#### Example of Typical Action Method

From Reversi example:
```php
public function actPlayDisc()
{
    $this->setAjaxMode();     
    $x = $this->getArg( "x", AT_posint, true );
    $y = $this->getArg( "y", AT_posint, true );
    $result = $this->game->actPlayDisc( $x, $y );
    $this->ajaxResponse( );
}
```

#### Methods to Use in Action Methods

**function setAjaxMode()**
**function ajaxResponse()**

**function getArg($argName, $argType, $mandatory=false, $default=NULL, $argTypeDetails=array(), $bCanFail=false)**

You must not use "_GET", "_POST" or equivalent PHP variables - it's unsafe.

**Parameters:**
- `argName`: Name of the argument to retrieve
- `argType`: Type of the argument. Use one of:
  - 'AT_int' for an integer
  - 'AT_posint' for a positive integer
  - 'AT_float' for a float
  - 'AT_bool' for 1/0/true/false
  - 'AT_enum' for an enumeration (argTypeDetails lists possible values as an array)
  - 'AT_alphanum' for a string with 0-9a-zA-Z_ and space
  - 'AT_alphanum_dash' for a string with 0-9a-zA-Z_- and space
  - 'AT_numberlist' for a list of numbers separated with "," or ";" (example: 1,4;2,3;-1,2)
  - 'AT_base64' for a base64-encoded string (SECURITY WARNING*)
  - 'AT_json' for a JSON stringified string (SECURITY WARNING**)
- `mandatory`: Specify "true" if the argument is mandatory
- `default`: If mandatory=false, specify a default value if the argument is not present
- `argTypeDetails`: Used with 'AT_enum'. Validates that the value is in this list
- `bCanFail`: If true, specify that the argument might not be of the specified type (don't log as fatal error, return standard exception to player)

**SECURITY WARNING:** If using AT_base64 or AT_json, or other undocumented unchecked types, you MUST perform validation on unpacked data. Do not use any of it unchecked (don't pass to DB queries or return in notifications).

```php
public function actMyAction()
{
   $this->setAjaxMode();
   $args = $this->getArg('actionArgs', AT_json, true);
   $this->validateJSonAlphaNum($args, 'actionArgs');
   $this->game->actMyAction($args);
   $this->ajaxResponse();
}

public function validateJSonAlphaNum($value, $argName = 'unknown')
{
   if (is_array($value)) {
     foreach ($value as $key => $v) {
       $this->validateJSonAlphaNum($key, $argName);
       $this->validateJSonAlphaNum($v, $argName);
     }
     return true;
   }
   if (is_int($value)) {
     return true;
   }
   $bValid = preg_match("/^[_0-9a-zA-Z- ]*$/", $value) === 1;
   if (!$bValid) {
     throw new \BgaSystemException("Bad value for: $argName", true, true, FEX_bad_input_argument);
   }
   return true;
}
```

**AT_enum and argTypeDetails Example:**
```php
$myarg = $this->getArg( 'myarg', AT_enum, false, null, [ 'apple', 'orange', 'banana' ] ); // optional enum
```

**function isArg($argName)**
Returns "true" or "false" according to whether "argName" was specified as an argument of the AJAX request.

#### Useful Tip: Retrieve a List of Numbers

If JavaScript sends a list of integers separated by ";" (example: "1;2;3;4"), transform them into a PHP array:
```php
public function actPlayCards()
{
    $this->setAjaxMode();     

    $card_ids_raw = $this->getArg( "card_ids", AT_numberlist, true );
    
    // Removing last ';' if exists
    if( substr( $card_ids_raw, -1 ) == ';' )
        $card_ids_raw = substr( $card_ids_raw, 0, -1 );
    if( $card_ids_raw == '' )
        $card_ids = array();
    else
        $card_ids = explode( ';', $card_ids_raw );

    $this->game->actPlayCards( $card_ids );
    $this->ajaxResponse( );
}
```

#### Example Pass Array of IDs

If JavaScript sends a list of objects denoted by alphanumerical tokenId, use AT_alphanum type with space as array separator:
```php
// sending 'card_ids' => "card_1 card_23 card_12"
public function actPlayCards()   {
    $this->setAjaxMode();     

    $card_ids_raw = $this->getArg( "card_ids", AT_alphanum, true );
    $card_ids_raw = trim($card_ids_raw);

    if( $card_ids_raw == '' )
        $card_ids = array();
    else
        $card_ids = explode( ' ', $card_ids_raw );

    $this->game->actPlayCards( $card_ids );
    $this->ajaxResponse( );
}
```

### Game Layout: view and template

**IMPORTANT NOTE:** These files are deprecated. You shouldn't need them if you generate the template from the JS file. See the Reversi tutorial for an example of in-JS template.

#### Purpose of This File

These files work together to provide the HTML layout of your game.

#### Overview

In .tpl file, you can directly write raw HTML that will be displayed by the browser:
```html
<div id="myhand_wrap" class="whiteblock">
  <h3>{MY_HAND}</h3>
  <div id="myhand">
  </div>
</div>
```

Things in curly braces are template variables. You cannot put English text directly there.

You shouldn't try to set up the current game situation in the view - this is the role of your JavaScript code. Why? Because you'll have to write JavaScript code to put game elements in place anyway, and you don't want to write it twice.

**The view should handle:**
- The overall layout of your game interface (what is displayed where)
- The board and fixed elements on the board (places for cards, squares, etc.)
- The tokens which are always on the board (but JS code may move them around during setup)

**The view should NOT handle:**
- Game elements that come and go from the game area
- Game elements normally hidden from players (other players' cards, cards in the deck)

#### Template System

BGA uses the phplib template system, used in PHPbb forums.

#### Variables

In your template (.tpl) file, you can use variables. In your view (.view.php) file, fill these variables with values:
```php
// Display a translated version of "My hand" at the place of the variable in the template
$this->tpl['MY_HAND'] = self::_("My hand");

// Display some raw HTML material at the place of the variable
$this->tpl['MY_HAND'] = self::raw( "<div class='myhand_icon'></div>" );
```

**WARNING:** Do not use a variable called {id} as it will interfere with action buttons.
**WARNING:** Do not use a variable called {ID} as it could receive unexpected values.

#### Template Blocks

Using "blocks," you can repeat a piece of HTML from your template several times.

```html
(in reversi_reversi.tpl)

<div id="board">
    <!-- BEGIN square -->
        <div id="square_{X}_{Y}" class="square" style="left: {LEFT}px; top: {TOP}px;"></div>
    <!-- END square -->
    
    <div id="discs">
    </div>
</div>
```

```php
(in reversi.view.php)

$this->page->begin_block( "reversi_reversi", "square" );
        
$hor_scale = 64.8;
$ver_scale = 64.4;
for( $x=1; $x<=8; $x++ ) {
    for( $y=1; $y<=8; $y++ ) {
       $this->page->insert_block( "square", array(
         'X' => $x,
         'Y' => $y,
         'LEFT' => round( ($x-1)*$hor_scale+10 ),
         'TOP' => round( ($y-1)*$ver_scale+7 )
        ) );
    }        
}
```

**Explanations:**
1. Specify a block in your template file using "BEGIN" and "END" keywords as XML comments. In the example, we create a block named "square"
2. In your view, declare your block using "begin_block" method
3. Insert as many blocks as you want using "insert_block" method

**insert_block parameters:**
1. Name of the block to insert
2. Associative array to assign values to template variables of this block (X, Y, LEFT, TOP in the example)

#### Nested Blocks

You can use nested blocks. Example: add a mini-board for each player with 4 card places on each:

```html
ggg_ggg.tpl file:
<!-- BEGIN player -->
    <div class="miniboard" id="miniboard_{PLAYER_ID}">

        <div class="card_places">
            <!-- BEGIN card_place -->
            <div id="card_place_{PLAYER_ID}_{PLACE_ID}">
            </div>
            <!-- END card_place -->
        </div>

    </div>
<!-- END player -->
```

```php
ggg.view.php file:
$this->page->begin_block( "ggg_ggg", "player" );
$this->page->begin_block( "ggg_ggg", "card_place" );

$players = $this->loadPlayersBasicInfos();
foreach( $players as $player_id => $player_info ) {
    $this->page->insert_block( "player", array( 
        'PLAYER_ID' => $player_id
    ) );
    
    for( $i=1; $i<=4; $i++ ) {
        $this->page->insert_block( "card_place", array(
            'PLAYER_ID' => $player_id,
            'PLACE_ID' => $i
        ) );
    }
}
```

This creates a nested structure with player blocks containing card_place blocks.

---

## Summary

Phase 1 has covered the foundational aspects of BGA Studio development:

**Chapter 1: Introduction to BGA Studio**
- Understanding what BGA Studio is and its role in the ecosystem
- Assessing whether BGA development is right for you
- Required skills and expectations for volunteer developers
- Creating a development account and understanding licenses
- First steps with the Studio platform
- Contact and support resources

**Chapter 2: Development Environment Setup**
- Setting up Visual Studio Code with recommended extensions
- Configuring PHP and JavaScript intellisense
- Setting up automated file synchronization with SFTP
- Understanding the BGA Studio file structure
- Essential tools and tips for efficient development

**Chapter 3: Game Project Fundamentals**
- Understanding gameinfos.jsonc for game metadata
- Designing database schemas in dbmodel.sql
- Using material.inc.php for game material definitions
- Understanding the deprecated action.php file structure
- Working with view and template files for game layout

With these foundations in place, you're ready to move to Phase 2, which covers the state machine architecture - the core system that controls game flow and turn-based logic in BGA games.
