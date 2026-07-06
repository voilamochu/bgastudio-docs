This is an automatically generated documentation consolidation from https://en.doc.boardgamearena.com/. The complete handbook is available as Developer_Handbook_v1.md.

## Chapter 6: Client-Side Game Interface (JavaScript)

### Understanding the Game Interface File

The main game interface file (`modules/js/Game.js`) is where you build the interactive frontend for your game. This file defines:

- Which actions on the page will generate calls to the server
- What happens when you get notifications for changes from the server and how to show them in the browser
- Setup and management of the user interface

**Important:** This file is now named `Game.js` and located in the `modules/js` directory. If you see it named `yourgamename.js` in the root directory, it's the legacy usage. The legacy version uses define/declare to instantiate a JS object, while the new way exports a class using ES Modules. The new class doesn't extend gameui, so if you need to access things from gameui that don't exist in the sub-components, you must use `this.gameui.xx`.

### Framework Sub-Components

The BGA framework is now split into multiple sub-components to group related functions:

- **statusBar** - Game status and progress display
- **sounds** - Sound effects management
- **gameArea** - Main game board area
- **playerPanels** - Player information panels
- **images** - Image loading and caching
- **userPreferences** - User preference handling
- **players** - Player information and state
- **actions** - Action execution and management
- **notifications** - Notification handling
- **dialogs** - Dialog and popup management

All are available in the `bga` object sent to the constructor (or `this.bga` for the legacy way).

```javascript
constructor(bga) {
    this.bga = bga;
}
```

In the legacy `<mygamename>.js`, `this.bga` is already set.

### File Structure

The Game.js file follows a specific structure:

**constructor**
- Define global variables for your whole interface
- Initialize framework components
- Register state classes

**setup(gamedatas)**
- Called when the page is refreshed
- Sets up the game interface
- Called when:
  - The game starts
  - A player opens a game in the browser later
  - A player refreshes the game page (F5)
  - A player does a server-side Undo

**onEnteringState(stateName: string, args: object | null): void**
- Called when entering a new game state
- Customize the view for each game state
- Optional - not needed if you use JS State classes
- **Warning:** For MULTIPLE_ACTIVE_PLAYER states, active players are NOT active yet. Use onUpdateActionButtons for operations that depend on active/inactive status. For initialization that doesn't depend on active player, replace `this.bga.players.isCurrentPlayerActive()` with `!this.bga.players.isCurrentPlayerSpectator()`.

**onLeavingState(stateName: string): void**
- Called when leaving a game state
- Clean up state-specific UI elements
- Optional - not needed if you use JS State classes

**onUpdateActionButtons(stateName: string, args: object | null): void**
- Called on state changes to add action buttons to the status bar
- In MULTIPLE_ACTIVE_PLAYER states, called when another player becomes inactive
- Optional - not needed if you use JS State classes

**Utility Methods**
- Your custom utility methods
- Helper functions for UI operations

**Player Actions**
- Handlers for player actions on the interface (e.g., click on an item)
- Event handlers for user interactions

**setupNotifications()**
- Associates notifications with notification handlers
- For each game notification, trigger a JavaScript method to handle it and update the interface

**Notification Handlers**
- Methods that handle specific notifications
- Update the game interface based on server notifications

The `gamedatas` argument contains all data retrieved by your `getAllDatas` PHP method plus some additional framework data.

### JS State Classes

To split the code of the Game class, you can create dedicated classes for each state you handle on the front side (some states like NextPlayer don't need to be handled on the JS side).

#### Registering State Classes

This method links a state class to a state name. Use it in the Game constructor:

```javascript
// Declare the State classes
this.bga.states.register('PlayerTurn', new PlayerTurn(this, this.bga));
```

When a state class is declared, the framework automatically calls its `onEnteringState`, `onLeavingState`, and `onPlayerActivationChange` functions.

#### State Class Structure

```javascript
class PlayerTurn {
    constructor(game, bga) {
        this.game = game;
        this.bga = bga;
    }

    /**
     * Called each time we enter the game state.
     * Use this to perform UI changes at this moment.
     */
    onEnteringState(args, isCurrentPlayerActive) {
        // Update UI for this state
    }

    /**
     * Called each time we leave the game state.
     * Use this to perform UI changes at this moment.
     */
    onLeavingState(args, isCurrentPlayerActive) {
        // Clean up UI for this state
    }

    /**
     * Called each time the current player becomes active or inactive
     * in a MULTIPLE_ACTIVE_PLAYER state.
     * For non-MULTIPLE_ACTIVE_PLAYER states, delete this function.
     */
    onPlayerActivationChange(args, isCurrentPlayerActive) {
        // Update UI based on player activation
    }

    // Custom functions specific to this state
}
```

#### State Helper Methods

**this.bga.states.getCurrentMainStateName(): string**
- Get the current main state name

**this.bga.states.getCurrentPlayerStateName(): string**
- Get the current player's state name

**this.bga.states.logger: Function**
- Logger function for debugging

**this.bga.states.getStateClass(stateName: string): Object**
- Get the state class for a given state name

**this.bga.states.getCurrentMainStateClass(): Object**
- Get the current main state class

**this.bga.states.getCurrentPlayerStateClass(): Object**
- Get the current player's state class

**this.bga.states.getStateClasses(): Object[]**
- Get all state classes

### Client States

Client states simulate state transitions without actually going to the server. This is useful when you need to ask the user multiple questions before sending data to the server.

**this.bga.states.setClientState(stateName: string, args: Object): void**
```javascript
this.bga.states.setClientState("client_playerPicksLocation", {
    descriptionmyturn: _("${you} must select location"),
});
```

With arguments:
```javascript
this.bga.states.setClientState("client_playerPicksLocation", {
    descriptionmyturn: _("${you} must select location for card {$card_number}"),
    args: { card_number: 5 },
});
```

For more information, see BGA_Studio_Cookbook#Multi_Step_Interactions.

**this.bga.states.restoreServerGameState(): void**
- Restore the actual server game state

**this.bga.states.isOnClientState(): boolean**
- Check if currently in a client state

### Accessing Player Information

#### Player Information Methods

**this.bga.players.getCurrentPlayerId(): number**
- ID of the player looking at the game
- May not be part of the game (spectator)

**this.bga.players.isCurrentPlayerSpectator(): boolean**
- True if the user is a spectator (not a player)

**Read-only state detection:**
```javascript
// Returns true for spectators, instant replay (during game), archive mode (after game end)
isReadOnly: function () {
    return this.bga.players.isCurrentPlayerSpectator() || 
           typeof g_replayFrom != 'undefined' || 
           g_archive_mode;
}
```

**this.bga.players.isCurrentPlayerActive(): boolean**
- True if the player on whose browser the code is running is currently active (their turn)
- **Note:** See remarks about usage in onEnteringState method

```javascript
if (this.bga.players.isCurrentPlayerActive()) {
    // Enable action buttons
}
```

**this.bga.players.getActivePlayerId(): number | null**
- ID of the active player, or null if not in an ACTIVE_PLAYER type state

```javascript
if (args.player_id == this.bga.players.getActivePlayerId()) {
    // This is the active player
}
```

**this.bga.players.getActivePlayerNo(): number | null**
- Number of the active player, or null if not in an ACTIVE_PLAYER type state

**this.bga.players.getFormattedPlayerName(playerId, params?): string**
- HTML code to display player name in bold with color
- Optional params: `{ replaceByYou: true }` displays colored "You" instead of player name

**Note:** In hotseat mode, the framework doesn't keep gamedatas of hotseat players and shares the same set as the main player.

**this.bga.players.getPlayerById(playerId): object**
- Player data stored in gamedatas.players
- Can be undefined if player isn't at the table (spectator)

**this.bga.players.getActivePlayer(): object**
- Same as getPlayer for the active player

**this.bga.players.getPlayerAvatarUrl(playerId, size): string**
- Player avatar URL
- Size can be 32, 50, 92, or 184 (default)
- Set playerId to 0 for default avatar

**this.bga.players.getPlayerIdByNo(): number**
- Player ID by player number

### Accessing and Manipulating the DOM

#### Main Game Area

**this.bga.gamearea.getGameAreaElement(): HTMLElement**
- Get the main game area element

**this.bga.gamearea.getGameAreaBackgroundColor(): string**
- Get the background color of the game area

**this.bga.gamearea.setGameAreaBackgroundColor(color: string): void**
- Set the background color of the game area

#### HTML Insertion

**this.bga.gamearea.insertAdjacentHTML(position: string, html: string): void**
- Insert HTML into the game area
- Position can be 'beforebegin', 'afterbegin', 'beforeend', 'afterend'

```javascript
this.bga.gamearea.insertAdjacentHTML('beforeend', '<div id="my-board"></div>');
```

### Actions and Player Input

#### Performing Actions

**this.bga.actions.performAction(action: string, args?: object, options: object): Promise<void>**

This method sends a player's input to the game server.

**Important restrictions:**
- Should NOT be triggered programmatically
- Especially not in loops, callbacks, notifications, or onEnteringState/onUpdateActionButtons/onLeavingState
- This prevents race conditions and breaks replay game and tutorial features
- Should only be used in reaction to user actions in the interface

**Parameters:**
- `action`: Name of the action, as written in "possibleactions" of the current state
- `args`: Object containing call parameters (can be undefined/omitted if no parameters)
  - Forbidden arg names: `$args`, `$activePlayerId`, `$active_player_id`, `$currentPlayerId`, `$current_player_id` (to avoid conflict with magic params)
- `options`: Options to tweak the call
  - Default: `{ lock: true, checkAction: true }`
  - `lock`: (true by default) Locks UI before any other action can execute, preventing multiple button clicks. Set to false to handle locking yourself.
  - `checkAction`: (true by default) Check that action is in possible actions list and user is active. Set to false only for rare out-of-turn actions.

**Important:** This is asynchronous - you should not do anything after this line except returning. Use promise handlers (catch/then) for post-call logic.

#### Action Examples

**Simple action:**
```javascript
this.bga.actions.performAction('pass');
```

**Standard call with action args:**
```javascript
this.bga.actions.performAction('actPlayCard', { id: this.selectedCardId });
```

**Call without checking action (player inactive in multiactive state):**
```javascript
this.bga.actions.performAction('actChangeMind', {}, { 
    checkAction: false, 
    checkPossibleActions: true 
});
```

**Call without lock (special action not directly related to game flow):**
```javascript
this.bga.actions.performAction('actSetAutoBid', { alwaysBidUntil: 500 }, { 
    lock: false, 
    checkAction: false 
});
```

**Call with array of IDs (for #[IntArrayParam]):**
```javascript
this.bga.actions.performAction('actPlayCards', { ids: this.selectedCardIds });
```

**Call with JSON object (for #[JsonParam], note the stringify):**
```javascript
this.bga.actions.performAction('actPlanComplexStuff', { 
    answer: JSON.stringify(this.theJsonObject) 
});
```

**Call with reaction to exception:**
```javascript
this.bga.actions.performAction('actPlayCard', { id: this.selectedCardId })
    .catch(() => { 
        this.selectedCardId = undefined; 
    });
```

**Call with reaction to success:**
```javascript
this.bga.actions.performAction('actPlayCard', { id: this.selectedCardId })
    .then(() => { 
        console.log('Action succeeded'); 
    });
```

### Event Handling

#### Connecting Events

**this.bga.gameui.connect(element: ElementOrId, event: string, method: eventHandler): void**
- Connect an event handler to an element
- Automatically handles event binding and cleanup

```javascript
onPet: function(event) {
    var id = event.currentTarget.id;
    console.log('onPet ' + id);
    dojo.stopEvent(event);
    if (this.gamedatas.gamestate.name == 'playerTurnPet') {
        this.bga.actions.performAction('actPlayPet', { card: id });
    } else {
        this.bga.dialogs.showMoveUnauthorized();
    }
}
```

**Important:** If you don't store the handler, you must destroy the object to disconnect it.

### Notifications

#### Setting Up Notifications

**setupNotifications()**
- Associate notifications with notification handlers
- For each game notification, trigger a JavaScript method to handle it and update the interface

```javascript
setupNotifications() {
    this.bga.notifications.subscribe('cardPlayed', (args) => this.onCardPlayed(args));
    this.bga.notifications.subscribe('playerScored', (args) => this.onPlayerScored(args));
}
```

#### Notification Handlers

Each notification should have a corresponding handler:

```javascript
onCardPlayed(args) {
    // Update UI to show card was played
    this.moveCardToPlayedArea(args.card_id, args.player_id);
}

onPlayerScored(args) {
    // Update player score display
    this.updatePlayerScore(args.player_id, args.score);
}
```

### TypeScript and SCSS (Optional Advanced Topics)

For developers who want modern tooling, BGA supports TypeScript and SCSS with automatic compilation.

#### TypeScript Setup

**Install dev stack:**
- Install node/npm
- Configure auto-build in your IDE (recommended)

**Benefits:**
- Type safety and better IDE support
- Catch errors at compile time
- Better code organization
- Improved auto-complete

**Configuration files:**

**package.json** (in root folder, not src):
```json
{
   "name": "yourgamename",
   "version": "1.0.0",
   "description": "",
   "main": "modules/js/Game.js",
   "scripts": {
     "build:ts": "rollup -c",
     "build:scss": "sass --no-source-map src/scss/Game.scss yourgamename.css",
     "watch:ts": "rollup -c -w",
     "watch:scss": "sass --watch src/scss/Game.scss yourgamename.css",
     "watch": "npm run watch:ts & npm run watch:scss",
     "build": "npm run build:ts && npm run build:scss"
   },
   "author": "yourname",
   "license": "MIT",
   "devDependencies": {
    "@rollup/plugin-typescript": "^12.3.0",
    "rollup": "^4.53.3",
    "sass": "^1.71.0",
    "tslib": "^2.8.1",
    "typescript": "^6.0.3"
   }
}
```

**Note:** If not using SCSS, remove corresponding scripts and dependencies.

**IMPORTANT:** Exclude node_modules/ from auto-sync to remote folder. Keep uploading the src folder so maintainers can use TypeScript.

**rollup.config.mjs:**
```javascript
import typescript from '@rollup/plugin-typescript';

export default {
    input: 'src/ts/Game.ts',
    output: {
      file: 'modules/js/Game.js',
      format: 'es',
      sourcemap: false,
      inlineDynamicImports: true,
    },
    plugins: [
      typescript({
        tsconfig: './tsconfig.json',
        outDir: 'modules/js',
      }),
    ],
    treeshake: false,
};
```

**tsconfig.json:**
```json
{
    "compilerOptions": {
      "target": "ES2020",
      "module": "ES2022",
      "moduleResolution": "bundler",
      "strict": false,
      "lib": ["dom", "esnext"],
      "sourceMap": false,
      "rootDir": "."
    },
    "include": [
      "*.d.ts",
      "src/ts/**/*.d.ts",
      "src/ts/**/*.ts"
    ]
}
```

**Note:** rootDir must be "." (not "src") so TypeScript sees *.d.ts files in project root (like bga-framework.d.ts). outDir must be set in rollup plugin (not tsconfig.json) because rollup plugin requires outDir inside same directory as rollup output file.

#### TypeScript File Structure

**TypeScript example:**
```typescript
interface YourGameNamePlayer extends Player {
    cards: Card[]; // information added to each result['players']
}

interface YourGameNameGamedatas extends Gamedatas<YourGameNamePlayer> {
    // Variables set up in getAllDatas
    discardedCards: { [row: number]: Card[] };
    remainingCardsInDecks: { [row: number]: number };
    tableCards: { [row: number]: Card[] };
}
```

**Note:** Generic typing is optional. types.d.ts cannot be called Game.d.ts (has different types, not related to Game class).

**Game class:**
```typescript
export class Game {
    public bga: Bga<YourGameNamePlayer, YourGameNameGamedatas>;
    private gamedatas: YourGameNameGamedatas;

    constructor(bga: Bga<YourGameNamePlayer, YourGameNameGamedatas>) {
        this.bga = bga;
    }

    public setup(gamedatas: YourGameNameGamedatas) {
        this.gamedatas = gamedatas;
        this.setupNotifications();
    }

    public setupNotifications() {}
}
```

**Important:** Sync bga-framework.d.ts from FTP folder regularly to get the latest version.

#### SCSS Setup

**SCSS file:** Write classic SCSS (compiled by Dart scss) in `src/scss/yourgamename.scss`

```scss
@use 'variables' as v;

@use "./Animations";
@use "./Board";

#ebd-body {
    background-image: url(img/woodbg.jpg);
    background-repeat: repeat;
}

@each $key, $val in v.$colors-list {
    .fgcolor#{$key} {
        color: #{$val};
    }
}
```

**SCSS can be split into multiple files:**
```scss
$colors-list: (
  _6cd0f6: #6cd0f6, // blue
  _ef58a2: #ef58a2, // pink
  _ffcc02: #ffcc02, // yellow
  _a0d28c: #a0d28c // green
);
```

### Best Practices for Client-Side Code

#### Performance

- **Minimize DOM manipulation** - Batch updates when possible
- **Use event delegation** - Attach fewer event listeners
- **Cache DOM elements** - Store references to frequently accessed elements
- **Optimize animations** - Use CSS transitions where possible

#### Code Organization

- **Use state classes** - Split code by game state
- **Keep methods focused** - Each method should do one thing
- **Use utility methods** - Extract common operations
- **Follow naming conventions** - Be consistent

#### Error Handling

- **Handle action failures** - Use catch() on performAction
- **Validate user input** - Check before sending to server
- **Provide feedback** - Show loading states and error messages
- **Log important events** - Use console.log for debugging

#### User Experience

- **Disable invalid actions** - Gray out buttons that can't be used
- **Show clear feedback** - Visual cues for valid/invalid actions
- **Handle network delays** - Show loading indicators
- **Support replay** - Ensure UI works in replay mode

#### Testing

- **Test with different player counts** - Verify UI scales correctly
- **Test in different states** - Ensure state-specific UI works
- **Test with spectators** - Verify read-only mode works
- **Test undo functionality** - Ensure UI updates correctly on undo

---

## Summary

Phase 4 has covered client-side game interface development, the frontend of BGA games:

**Key Concepts:**
- Game.js file structure and purpose
- Framework sub-components for organized functionality
- State-based UI management with JS State classes
- Client states for multi-step interactions
- Player information access and management
- DOM manipulation and game area management
- Action execution with bgaPerformAction
- Event handling and user input processing
- Notification system for server-client communication
- Optional TypeScript and SCSS for modern development

**Next Steps:**
With both server-side logic and client-side interface understood, you're ready for Phase 5, which covers UI components and graphics - the visual building blocks that make your game look and feel great.
