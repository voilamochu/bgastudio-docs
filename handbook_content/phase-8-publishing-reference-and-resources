# BGA Studio Developer Handbook - Phase 8: Publishing, Reference, and Resources

## Chapter 13: Game Development and Publishing

### Complete Walkthrough

The "Create a game in BGA Studio: Complete Walkthrough" provides step-by-step instructions for building your first game adaptation using the BGA Studio framework.

#### Prerequisites

Before starting:
- Read the overall presentations of BGA Studio
- Know the languages used: PHP, SQL, HTML, CSS, JavaScript/TypeScript
- Set up your development environment (First Steps with BGA Studio)
- Complete at least one tutorial before creating a new game

#### Selecting Your First Game

For your first real game (after completing a tutorial), select from:
- Available Licenses
- Public Domain

**Important:** Don't start a project until you're sure BGA has the license for the game, or it will never be published to BGA!

If the game you want isn't in either category:
- Successfully publish another game to gain BGA admin trust
- They may then help you obtain a license for your desired game
- Or request a license yourself (see BGA Game licenses page)

**Taking over existing projects:**
- Check if the project is abandoned (many projects are inactive)
- Post on Developers forum asking if anyone is actively working on it
- Message developers of abandoned projects
- Ask admins for graphics if they have them
- Get read-only access via project list to see if the project is worth using
- If no code or graphics, start from scratch
- If original admin doesn't answer, write a support ticket for access

#### Creating a Project

1. Create a project in BGA Studio for the game
2. If the game name is taken, check existing project status first
3. Modify client source (.ts or .js) to output "hello world"
4. Build and reload page to verify FTP sync works
5. **Important:** Set up FTP auto-sync - manual copying is not sustainable

#### Development Tools

Setup your development environment with:
- Editor or IDE (VSCode recommended for TypeScript)
- Browser with dev tools
- File sync tools
- BGA Web tools
- Image manipulation tools
- Version control tools
- Build tools (npm, TypeScript compiler, SCSS compiler, rollup/esbuild)

Review Studio#BGA_Studio_user_guide especially debugging and tools sections.

#### Version Control

For real games, commit code to version control immediately. You'll encounter situations where the game doesn't start, and version control is essential for reverting.

**Tips:**
- At minimum, back up files after each major step
- Create a GitHub project if desired
- **Never commit original publisher graphics files**
- **Never include files with SFTP passwords** (GitHub is crawled for passwords - this caused a hacking attempt in June 2020)
- Commit modifications periodically via Studio Control Panel

#### Obtaining Game Graphics

For games from Available Licenses:
- Use "Request Art Files" button on studio license page
- Request can take time (requires back-and-forth between admins and publishers)
- Proceed to project creation while waiting

For public domain card games:
- Borrow standard cards from BGA generic assets (Common_board_game_elements_image_resources)
- Standard pieces (meeples, cubes, dice) also available there

### Pre-Release Checklist

Before moving from Dev to Alpha, review this checklist.

#### License
- BGA must have a license for the game (required even for Alpha)
- Cannot move to production until license situation is cleared

#### Metadata and Game Assets
- Game_meta-information: gameinfos.jsonc has correct, up-to-date information
- Game box graphics is 3D version (if available) with correct publisher icon
- Space around box must be transparent, not white
- Added requested images in Game Metadata Manager
- No unnecessary images in img directory
- Multiple images (cards) compressed in "Sprite"
- Each image should not exceed 4MB
- Total size should not exceed 15MB (use image compression, re-encode as indexed palette vs RGB)
- Note legitimate reasons for exceeding 15MB (expansions) when requesting Alpha move
- Extra fonts must be freeware (include .txt with license info in fonts directory)
- Sounds placed in "sounds" directory

#### Server Side
- Use `giveExtraTime()` function when giving turn to a player
- Game progression implemented (`getGameProgression()` in PHP)
- Zombie turn implemented (`zombieTurn()` in PHP) - see Zombie mode documentation
- Defined and implemented meaningful statistics (total points, points from sources A/B/C...)
- Meaningful notification messages (don't overkill - too many logs slow loading)
- Tiebreaking implemented (using aux score field) and updated in metadata
- Database: no programmatic transaction management or schema-changing queries during normal operations
- Database: schema sufficient to complete game and allow for possible expansions (changing schema after release is challenging)

#### Client Side
- Use `ajaxcall`/`bgaPerformAction` only on player actions, never programmatically (creates race conditions, breaks replays/tutorials)
- Exception: no-op moves with timeouts when user has only one choice (timeout must cancel itself if state transition happens automatically, e.g., during replay)

#### User Interface
- Review BGA UI design Guidelines (BGA_Studio_Guidelines)
- Check English messages for proper punctuation, capitalization, present tense in notifications (not past), gender neutrality (see Translations)
- Elements not occupying all horizontal space should be centered
- If elements become blurry/pixelated on browser zoom, consider higher resolution images with background-size
- Non-self-explanatory graphic elements should have tooltips
- Strings ready for translation (see Translations)
- Generate dummy translations from "Manage game" page to verify translation readiness
- Use a prefix (e.g., trigram) for all CSS classes to avoid namespace conflicts (vla_selected vs selected)
- For design advice and 3rd party testing, post on developers forum

### Post-Release Phase

Congratulations - your game is now on BGA! You're still allowed to modify it, but pay attention to the points below.

#### Bug Reporting

Bugs are reported on the BGA bugs page.

#### Documentation for Bug Reports

You can provide a wiki page for bug reporters using the "Edit bug clarifications Wiki page" button.

#### Submitting Changes

Steps to make changes visible on BGA (from game Control Panel):

**Build a new release version:**
1. Enter release notes (fixed bug xxx, added feature yyy)
2. Press "Commit & build a new version now"
3. Don't dismiss build dialog - ensure no errors (errors = build failed)

**Deploy to production:**
1. Find newly built version (should be latest, check release notes)
2. Press "Deploy to production" button
3. Don't dismiss deploy dialog - ensure no errors (errors = deploy failed)

**Verification:**
- Version should update in "Online version" of control panel
- Version should update in Credits page of running game
- Post update announcement on Group page (using release notes)

**Tips for popular games:**
- Disable/lock table creation for new deploy
- Force players to refresh after new deploy

#### What Can Be Modified After Release?

Everything can be modified, but some items require special attention.

**Changes that break games in progress:**
Some changes will break games in progress at the moment of release/hotfix. Always ask: "Is it safe to make this change in a game in progress?" If no, you must inform BGA.

Breaking changes include:
- Changes in database schema (dbmodel.sql)
- New global variable or game option accessed during game (safe if only used during setup)
- Change ID of existing game states (adding new states is fine)
- Changing flow of game states (e.g., 1→2→3→4 to 1→3→2→4 causes players at state 2 to skip state 3)

**Guidelines for breaking changes:**
- Avoid introducing changes that break games in progress
- If unavoidable, group all updates in one version to avoid multiple blocks
- Tell BGA explicitly that the update can break games in progress so they can block the game briefly

**Note:** In the future, you'll be able to block/unblock games directly from Control Panel.

**Updating game options:**
- If adding options, let BGA know which value should be used for arena mode
- If removing/changing option ID, it breaks arena configuration - inform BGA to synchronize
- **Do not change option IDs** once in production (breaks ongoing games and arena statistics)

**Statistics:**
- Don't change statistic IDs (loses historical data)
- Don't re-use IDs of deleted statistics
- If game is public, read Post-release_phase#Changes_that_breaks_the_games_in_progress before changes

### Game Lifecycle

The BGA game lifecycle includes:
- Development (Dev)
- Alpha testing
- Beta testing
- Release
- Post-release maintenance

Each stage has specific requirements and considerations. Review the BGA_game_Lifecycle documentation for details.

---

## Chapter 14: Migration and Compatibility

### BGA Studio Migration Guide

The BGA_Studio_Migration_Guide covers migrating games to newer framework versions, including:
- PHP 7.4 to PHP 8.4 migration
- State class migration from states.inc.php
- Notification system updates
- Deprecated function replacements
- Modern API usage

### Compatibility

The Compatibility documentation covers:
- Browser compatibility requirements
- Mobile device support
- Framework version compatibility
- Backward compatibility considerations

---

## Chapter 15: Reference and Resources

### BGA Code Sharing

The BGA_Code_Sharing page provides community resources and shared code that can help with game development.

### Available Development Tools

**Chrome Extension:**
A Chrome extension is available to assist with BGA development.

**Common Board Game Elements:**
Image resources for common game elements (cards, meeples, cubes, dice) are available at Common_board_game_elements_image_resources.

### Community Resources

**Discord:**
Join the community-based Discord dev server: https://discord.gg/YxEUacY

**Developers Forum:**
Post questions on the BGA Developers forum. If stuck or have questions about documentation, post here.

**Wiki Editing:**
If you find typos in the wiki, fix them (login to BGA to edit).

### Additional Documentation

**Anti-Stock:**
Alternative pattern to Stock for card management.

**BGA Game Licenses:**
Information about game licensing and how to obtain licenses.

**Contact BGA Studio:**
How to contact BGA Studio for support.

**Game Metadata Manager:**
Managing game metadata and assets.

**Game Replay:**
Implementing game replay functionality.

**Game Sounds:**
Adding sound effects to your game.

**I Wish I Knew This When I Started:**
Tips from experienced developers.

**Studio FAQ:**
Frequently asked questions about BGA Studio.

**Studio File Reference:**
Reference for all Studio files and their purposes.

**Studio Logs:**
Understanding and using Studio logs for debugging.

**Tools and Tips:**
Additional tools and tips for BGA Studio development.

**Translations:**
Detailed translation system documentation.

**Troubleshooting:**
Solutions to common problems.

**Tutorials:**
- Tutorial_hearts
- Tutorial_reversi
- Tutorials_checklist

**Using AI for BGA Game Development:**
Guidelines and considerations for using AI tools in game development.

**Using Vue:**
Information about using Vue.js in BGA games.

**Your Game Mobile Version:**
Ensuring your game works on mobile devices.

---

## Summary

Phase 8 has covered publishing, reference materials, and additional resources:

**Key Topics:**
- Complete game development walkthrough
- Pre-release checklist for Alpha stage
- Post-release phase and maintenance
- Submitting changes and deployment process
- Game lifecycle stages
- Migration guide for framework updates
- Compatibility requirements
- Community resources and support
- Additional reference documentation

**Handbook Complete**

Congratulations! You have completed the BGA Studio Developer Handbook covering all phases of BGA game development:
- Phase 1: Foundation and Setup
- Phase 2: State Machine Architecture
- Phase 3: Server-Side Game Logic
- Phase 4: Client-Side Game Interface
- Phase 5: UI Components and Graphics
- Phase 6: UI Enhancements and Interactivity
- Phase 7: Advanced Features and Testing
- Phase 8: Publishing, Reference, and Resources

This handbook provides a comprehensive guide for developing games on Board Game Arena, from initial setup through publication and maintenance.
