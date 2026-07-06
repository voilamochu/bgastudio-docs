# BGA Studio Developer Handbook - Phase 3: Server-Side Game Logic

## Chapter 5: Server-Side Game Logic (PHP)

### Understanding the Game Logic File

The main game logic file (`modules/php/Game.php`) is where you implement the core rules of your game. This is the most important file in your project - it's where you initialize the game, persist data, implement the rules, and notify the client interface of changes.

**Important:** Your PHP class instance won't remain in memory between two callbacks. Every time the client sends a request, a new class will be created, the constructor will be called, and eventually your callback function will execute. This means you cannot rely on instance variables persisting between requests - all persistent data must be stored in the database.

### File Structure

The Game.php file has a specific structure that you should follow. The template provided includes comments describing each section.

#### Core Methods

**__construct**
- The game constructor where you define global variables and initialize class members
- Called every time a new instance of your game class is created
- Use this to set up game configuration and constants

**setupNewGame(array $players)**
- Initial setup of the game
- Takes an array of players, indexed by player_id
- Each player includes: player_name, player_canal, player_avatar, and flags for admin/ai/premium/order/language/beginner
- Initialize the game state, deal cards, set up the board, etc.
- This is where the game begins

**getAllDatas(int $currentPlayerId)**
- Retrieve all game data during a complete reload of the game
- Return value must be an associative array
- The value of 'players' is reserved for returning players data from the players table
- If you set 'players', it must follow specific rules:

```php
$result['players'] = $this->getCollectionFromDb("SELECT `player_id` `id`, `player_score` `score`, `player_no` `no`, `player_color` `color` FROM `player`");
// Returned value must include ['players'][$player_id]['score'] for scores to populate when F5 is pressed
```

**Magic parameters:** getAllDatas accepts magic parameters:
- `int $currentPlayerId` - fetch information from the current player's perspective
- `int $currentPlayerNo` - fetch information from the current player number's perspective
- Should not have any other parameters

**getGameProgression()**
- Compute the game progression indicator
- Returns a number indicating percent of progression (0-100)
- Used to calculate ELO changes when a player quits
- Used as a conceding requirement (in non-tournament 2-player games, a player may concede if progression is at least 50%)

**Utility Functions**
- Your custom utility functions
- Helper methods for game logic
- Common operations used throughout your game

**Player Actions**
- Entry points for player actions
- Methods that handle specific player moves and decisions
- These are called from the client side

**Game State Arguments**
- Methods to return additional data for specific game states
- Called when entering a state to provide context to the client

**Game State Actions**
- Logic to run when entering a new game state
- Initialization for specific states
- Automatic game logic

**initTable()**
- Not part of the template but can be implemented
- Called for every PHP callback by the framework
- Use in rare cases where you need to read database and manipulate data before ANY PHP entry functions are called (getAllDatas, action*, st*, etc.)
- NOT called before arg* methods

**zombieTurn(int $player_id)**
- What to do when it's a zombie player's turn
- Implement automatic play for disconnected players
- Return the transition to take after zombie action

**upgradeTableDb()**
- Function to migrate database if you change it after release on production
- Handle schema changes for existing games
- Critical for maintaining compatibility with live games

**getGameName()**
- Returns the game name
- Set when you create the project
- If copying files from another project, keep this function intact
- Must return the right game name or many things will break

### Accessing Player Information

**Important:** Be mindful of the difference between the "active" player and the "current" player:
- **Active player:** The player whose turn it is (not necessarily the player who sent the request)
- **Current player:** The player who sent the request and will see the results (not necessarily the player whose turn it is)

#### Player Information Methods

**getPlayerCount() or getPlayersNumber()**
- Returns the number of players playing at the table
- **Note:** Doesn't work at the beginning of setupNewGame (use count($players) instead)
- Works after initialization of player table

**getActivePlayerId(): string**
- Gets the "active_player" regardless of current state type
- **Note:** Does NOT mean this player is active right now (state type could be "game" or "multiplayer")
- **Note:** Avoid using in "multiplayer" states because it doesn't mean anything
- **Generally:** You shouldn't use this method. It's available as a magic param in getArgs/onEnteringState/act functions and shouldn't be needed elsewhere

**getActivePlayerName()**
- Gets the "active_player" name
- **Note:** Avoid using in "multiplayer" states

**getPlayerNameById($player_id)**
- Gets the player name by ID

**getPlayerNameByNo($playerNo)**
- Gets the player name by player number

**getPlayerColorById($player_id)**
- Gets the player color by ID

**getPlayerNoById($player_id)**
- Gets 'player_no' (number) by ID

**getPlayerIdByNo(int $playerNo): int**
- Gets the player ID by player number

**loadPlayersBasicInfos()**
- Gets an associative array with generic data about players (not game-specific)
- Key is the player ID
- Returned table is cached - safe to call multiple times without performance concerns
- Each value contains:
  - `player_name` - the name of the player
  - `player_color` - color code (e.g., ff0000) as string
  - `player_no` - position at start of game in natural table order (1, 2, 3...)

```php
$players = $this->loadPlayersBasicInfos();
foreach ($players as $player_id => $info) {
    $player_color = $info['player_color'];
    // ...
}
```

**Note:** If you want an array of player IDs only:
```php
$player_ids = array_keys($this->loadPlayersBasicInfos());
```

**getCurrentPlayerId(bool $bReturnNullIfNotLogged = false): string**
- Gets the "current_player" (the one who sent the request)
- **Be careful:** This is not necessarily the active player
- **Generally:** You shouldn't use this method. It's available as a magic param in act functions and getAllDatas
- **Very important:** In setupNewGame and zombieTurn, NEVER use getCurrentPlayerId() or getCurrentPlayerName(), or it will fail with "Not logged" error (these actions are triggered from the main site and propagated to the game server from a server, not from a browser)

**getCurrentPlayerName(bool $bReturnEmptyIfNotLogged = false): string**
- Gets the "current_player" name
- Throws exception if current player is not at the table (i.e., spectator)
- **Be careful** using this method (see above)
- Can be replaced by `$this->getPlayerNameById($currentPlayerId)`

**getCurrentPlayerColor()**
- Gets the "current_player" color
- Throws exception if current player is not at the table
- **Be careful** using this method (see above)
- Can be replaced by `$this->getPlayerColorById($currentPlayerId)`

**isCurrentPlayerZombie()**
- Checks the "current_player" zombie status
- Returns true if player is zombie (left or was kicked out)
- Throws exception if current player is not at the table
- **Be careful** using this method (see above)
- Should never be needed - zombie players should behave like real players, and zombie-specific logic should be in the zombie method only

**isSpectator()**
- Checks the "current_player" spectator status
- Returns true if the user is a spectator (not part of the game)
- For spectators, display all public information and no private information
- Like a friend sitting at the same table watching the game

For player score and tiebreaker, see the section "Manage player scores and Tie breaker" later in this chapter.

### Accessing the Database

The main game logic should be the only point from which you access the game database. You access your database using SQL queries with the methods below.

**Important:** BGA uses database transactions. This means:
- Your database changes WON'T BE APPLIED until your request ends normally (web request, not database request)
- This is very useful - if your game logic detects something wrong (e.g., a disallowed move), throw an exception and all changes will be removed
- You need not (and cannot) use your own transactions for multiple related database operations

All methods below are part of the game class (and view class) and can be accessed using `$this->`.

#### Database Query Methods

**DbQuery(string $sql)**
- Generic method to access the database
- Can execute any type of SELECT/UPDATE/DELETE/REPLACE/INSERT query
- Returns result of the query
- For SELECT queries, use the specialized methods below (they're much better)
- **Do not use** for TRUNCATE, DROP, and other table-altering operations (see disclaimer about implicit commits)
- If you really need TRUNCATE, use DELETE FROM xxx instead

**getUniqueValueFromDB(string $sql)**
- Returns a unique value from DB or null if no value is found
- $sql must be a SELECT query
- Raises exception if more than 1 row is returned

**getCollectionFromDB(string $sql, bool $bSingleValue = false): array**
- Returns an associative array of rows for a SQL SELECT query
- Key of resulting array is the first field specified in SELECT query
- Value is an associative array with all fields specified in SELECT and associated values
- First column must be a primary or alternate key (semantically - doesn't actually have to be declared as such in SQL)
- Resulting collection can be empty (won't be null)
- If $bSingleValue = true and SQL requests 2 fields A and B, returns associative array "A=>B", otherwise A=>[A,B]
- **Note:** The name is misleading - it returns an associative array (map), not a collection
- Cannot use to get list of values with duplicates (hence primary key requirement on first column)
- If you need a simple array, use getObjectListFromDB()

**getObjectListFromDB(string $sql, bool $bSingleValue = false): array**
- Returns an array of objects/associative arrays for a SQL SELECT query
- Use this when you don't have a unique key or don't need key-based access
- If $bSingleValue = true and SQL requests 2 fields A and B, returns array of B values only

Example:
```php
$result = $this->getObjectListFromDB("SELECT `player_name` `name` FROM `player`", true);
// Result: ['myuser0', 'myuser1']
```

**getDoubleKeyCollectionFromDB(string $sql, bool $bSingleValue = false): array**
- Returns an associative array of associative arrays from a SQL SELECT query
- First array level corresponds to first column in SQL
- Second array level corresponds to second column in SQL
- If $bSingleValue = true, keep only third column in result

**DbGetLastId()**
- Returns the PRIMARY key of the last inserted row (like PHP's mysql_insert_id function)

**DbAffectedRow(): int**
- Returns the number of rows affected by the last operation

**escapeStringForDB(string $string): string**
- **Must** use this function on every string type data in your database that contains unsafe data (unsafe = can be modified by a player)
- Ensures no SQL injection through the string, as long as the SQL statement uses single quotes around the string
- **This is important!**

**Note:** If you use standard types in AJAX actions like AT_alphanum, data is sanitized before arrival. This function is only needed if you manage to get an unchecked string (like when users enter text as a response). This function does not escape % and _ by default (wildcards in SQL LIKE statements) - determine if this is desirable behavior.

### Using BGA Globals

Sometimes you want a single global value for your game without creating a specific DB table for it.

The keys are strings, so you might want to store them in constants to avoid mistakes (key must be at most 50 characters long).

Having a string key and JSON serialization allows easy debugging by looking at the bga_globals table content.

#### BGA Globals Methods

**bga->globals->set(string $name, $mixed $obj): void**
```php
const FIRST_PLAYER_ID = "firstPlayerId";
$this->bga->globals->set(FIRST_PLAYER_ID, array_keys($players)[0]);
```

**bga->globals->get(string $name, $mixed $defaultValue = null, ?string $class = null): mixed**
```php
$currentFirstPlayerId = $this->bga->globals->get(FIRST_PLAYER_ID);
$selectedCardsIds = $this->bga->globals->get(SELECTED_CARDS_IDS, []);
```

You can specify the expected class type if you save a class and don't want it returned as stdClass:
```php
$undo = new Undo($playerId, $moves);
$this->bga->globals->set(UNDO, $undo);

$undo = $this->bga->globals->get(UNDO); // returns stdClass
$undo = $this->bga->globals->get(UNDO, class: Undo::class); // returns Undo class
```

**Note:** Your class should be a plain object with no mandatory constructor params:
```php
class Undo {
    public function __construct(
        public ?int $playerId = null,
        public ?array $moves = null,
    ) {}
}
```

**bga->globals->getAll(...$names): array**
```php
$variables = $this->bga->globals->getAll();
$diceVariables = $this->bga->globals->getAll(DIE1, DIE2);
```

Use with PHP's extract() function to quickly assign multiple variables:
```php
extract($this->bga->globals->getAll('endTime', 'hour', 'vipWelcome'));
// $endTime, $hour, and $vipWelcome (may) now exist

if (!empty($endTime)) {
    // ...
}
```

**bga->globals->delete(...$names): void**
```php
$this->bga->globals->delete(SELECTED_CARDS_IDS);
$this->bga->globals->delete(SELECTED_CARDS_IDS, UNDO, AFTER_DISCARD_RETURN_STATE);
```

**bga->globals->has(string $name): bool**
- Indicates if a global variable is stored in database
```php
$cardSelectionIsStarted = $this->bga->globals->has(SELECTED_CARDS_IDS);
```

**bga->globals->inc(string $name, int $inc): int**
```php
$this->bga->globals->inc(PLAYED_ACTIONS_IN_CURRENT_TURN, 1);
$totalSpent = $this->bga->globals->inc(SPENT_COINS_IN_CURRENT_TURN, $cardCost);
```

### Using Legacy Globals (Numbers Only)

Before `$this->globals`, you could only store numeric values as globals. These "GameStateValues" are stored in the "global" table in the database.

**initGameStateLabels(array $labelsMap): void**
- Define up to 80 globals with IDs from 10 to 89 (inclusive, gaps allowed)
- For game options, IDs need to be between 100 and 199
- Must not use globals outside the defined ranges (used by other framework components)

```php
function __construct() {
    parent::__construct();
    $this->initGameStateLabels([ 
        "my_first_global_variable" => 10,
        "my_second_global_variable" => 11,
        "my_game_variant" => 100
    ]);
}
```

**Note:** The methods below WILL throw an exception if label is not defined using the call above.

**setGameStateInitialValue(string $label, int $value): void**
- Initialize global value
- Not required if you're okay with default value of 0
- Should be called from setupNewGame function

**getGameStateValue(string $label, int $default = 0): int**
- Retrieve the value of a global
- Returns $default if global hasn't been initialized
```php
$value = $this->getGameStateValue('my_first_global_variable');
```

**setGameStateValue(string $label, int $value): void**
```php
$this->setGameStateValue('my_first_global_variable', 42);
```

**incGameStateValue(string $label, int $increment): int**
- Increment a global value and return the new value
```php
$newValue = $this->incGameStateValue('my_first_global_variable', 1);
```

### Notifications

Notifications are a crucial part of the BGA framework. Everything players see, including all changes on the frontend (including setup), is done via notifications.

**Important:** To understand notifications, read "The BGA Framework at a glance" presentation first.

#### Framework Notifications

The framework automatically sends notifications for:
- State transitions
- Player activation changes
- Score updates
- Game end

#### Custom Notifications

You send custom notifications for game-specific events:
- Card plays
- Token movements
- Game phase changes
- Custom game events

#### Notification Queue

Notifications are queued - sent at the very end of the action when it ends normally. This means:
- If you throw an exception for any reason (e.g., move not allowed), no notifications will be sent
- This provides transactional consistency - either all changes happen, or none do

#### When to Send Notifications

Send notifications from:
- Action handlers (act* in State classes or Game.php) - **MUST** send at least one notification (includes state transition)
- Game state transitions (onEnteringState in State classes)
- Game initialization (setupNewGame)
- Zombie turn handling

#### Types of Notifications

**Public Notifications**
- Sent to all players
- Used for game state changes that everyone should see
- Examples: "Player X played a card", "Turn passed to Player Y"

**Private Notifications**
- Sent to specific players only
- Used for information that should be hidden from other players
- Examples: "You drew these cards", "Your hand is now..."

**Note:** The bundle of notifications sent at the end of an action is considered a single "move" and the table's move counter increases. If you ONLY send private notifications during action handling, they won't have an associated move_id (to avoid this, add a simple public notification with empty message).

#### Notification Methods

**bga->notify->all(string $notification_type, string | NotificationMessage $message, array $notification_args)**

Parameters:
- `notification_type`: A string defining the type of your notification
- `message`: The message to display (must use clienttranslate for translatable messages)
- `notification_args`: Associative array of arguments for the notification

```php
$this->bga->notify->all('cardPlayed', clienttranslate('${player_name} played ${card_name}'), [
    'player_id' => $playerId,
    'player_name' => $this->getPlayerNameById($playerId),
    'card_id' => $cardId,
    'card_name' => $this->getCardName($cardId),
]);
```

**bga->notify->player(int $player_id, string $notification_type, string | NotificationMessage $message, array $notification_args)**
- Sends notification to a specific player only
- Use for private information

```php
$this->bga->notify->player($playerId, 'cardsDrawn', clienttranslate('You drew ${count} cards'), [
    'count' => count($cards),
    'card_ids' => $cardIds,
]);
```

**bga->notify->players(array $player_ids, string $notification_type, string | NotificationMessage $message, array $notification_args)**
- Sends notification to multiple specific players
- Use for semi-private information (e.g., team members)

#### Notification Message Format

**Simple Message:**
```php
clienttranslate('${player_name} played a card')
```

**With Arguments:**
```php
$this->bga->notify->all('cardPlayed', clienttranslate('${player_name} played ${card_name}'), [
    'i18n' => ['card_name'],  // Mark card_name as translatable
    'player_name' => $this->getPlayerNameById($playerId),
    'card_name' => $this->getCardName($cardId),
]);
```

**Preserve HTML:**
```php
$this->bga->notify->all('message', self::_('Some <b>bold</b> text'), [
    'preserve' => ['_message'],  // Preserve HTML formatting
]);
```

#### Handling Notifications on Client Side

Notifications are handled on the JavaScript side by subscribing to notifications (only do this for custom notifications!). See Game_interface_logic:_yourgamename.js#Notifications for details.

### PHP Migration Notes

If you're migrating from older PHP versions, note these changes:

**October 2025:** Migration from PHP 7.4 to PHP 8.4 with new syntax and functions.

**Replace all `self::` with `$this->`**
- The new project template removes this bad practice (may be unsupported in future PHP versions)

**Add `declare(strict_types=1);` to all .php files**
- Fix compiler warnings (IDE will detect before upload)

### Autowire Game Actions

Modern BGA uses autowiring for game actions, eliminating the need for the deprecated action.php file.

**Benefits:**
- Simpler action handling
- Automatic argument validation
- Better IDE support
- Reduced boilerplate

**How it works:**
- Actions are defined directly in State classes or Game.php
- Mark with `#[PossibleAction]` attribute
- Framework automatically routes calls to the correct method

**Example:**
```php
#[PossibleAction]
public function actPlayCard(int $cardId, int $activePlayerId, array $args): string
{
    // Validate and execute
    $this->validateCardPlay($cardId, $activePlayerId);
    $this->playCard($cardId, $activePlayerId);
    
    return 'playCard';  // Transition name
}
```

### Game Statistics

Game statistics are displayed at the end of the game and track various metrics.

#### File Structure

There are 2 types of statistics:
- **Table statistics:** Not associated with specific players (one value per game)
- **Player statistics:** Associated with each player (one value per player)

Statistics types:
- "int" for integer
- "float" for floating point values
- "bool" for boolean

**Important:** If you want to skip some statistics according to game variants, don't init them or call set/inc on them. They'll display as "-" (instead of 0 if you init but don't update).

**Warning:** If your game is already public on BGA, read this before any changes: https://en.doc.boardgamearena.com/Post-release_phase#Changes_that_breaks_the_games_in_progress

#### Statistics Rules

- Statistic index is the reference used in set/inc/init PHP methods
- Must contain alphanumerical characters and no space (e.g., 'turn_played')
- Statistics IDs must be >= 10
- Two table statistics can't share the same ID
- Two player statistics can't share the same ID
- A table statistic can have the same ID as a player statistic (not recommended unless same conceptually)
- Statistics ID is the reference used by BGA website - if you change the ID, you lose all historical data
- **Do NOT re-use an ID of a deleted statistic**
- Statistic name is the English description shown to players
- Order in array determines display order (NOT by ID) - helpful for stats added later that need to appear higher
- Statistic names and labels are automatically added to translation system (no need for totranslate() calls)
- Previously was stats.inc.php - can continue using for old projects
- (Number of table statistics) + (Number of player statistics × Maximum players) should not exceed ~930 or game will crash

#### Example stats.json

```json
{
   "table": {
     "turns_number": {
       "id": 10,
       "name": "Number of turns",
       "type": "int"
     }
   },
   "player": {
     "turns_number": {
       "id": 10,
       "name": "Number of turns",
       "type": "int"
     },
     "player_teststat1": {
       "id": 11,
       "name": "player test stat 1",
       "type": "int"
     },
     "player_teststat2": {
       "id": 12,
       "name": "player test stat 2",
       "type": "float"
     }
   }
}
```

#### Generate PHP Initialization

In Chrome DevTool console (F12):
```javascript
stats = <Ctrl+V of stats.json content>
['table', 'player'].map(type => `$this->${type}Stats->init([${Object.keys(stats[type]).map(key => `'${key}'`).join(',')}], 0);`).join('\n')
```

Copy the result and paste in your PHP setupNewGame function (assumes you want to init all stats to 0).

#### Labeled Stats

Sometimes you want to display a label instead of a number (e.g., winning faction as table statistic, faction chosen by each player in games like Terra Mystica).

```json
{
  "table": {
    "winning_race": {
      "id": 11,
      "name": "Winning race",
      "type": "int"
    }
  },
  "value_labels": {
    "11": [
      "None (or tied)",
      "Auren",
      "Witches",
      "Fakirs",
      "Nomads",
      "Chaos Magicians",
      "Giants",
      "Swarmlings",
      "Mermaids",
      "Dwarves",
      "Engineers",
      "Halflings",
      "Cultists",
      "Alchemists",
      "Darklings"
    ]
  }
}
```

#### Limited Access Stats

For internal game statistics visible only to developers, publishers, or admins:

```json
{
  "player_teststat2": {
    "id": 12,
    "name": "player test stat 2",
    "type": "float",
    "display": "limited"
  }
}
```

#### Translations

Any name or value_labels text in JSON files are automatically added to the translation system, even without totranslate() calls.

### Best Practices for Server-Side Logic

#### Error Handling

- **Use exceptions** for error conditions - they automatically roll back database changes
- **Validate all inputs** before processing
- **Provide clear error messages** to help debugging
- **Log important events** for troubleshooting

#### Performance

- **Minimize database queries** - cache when possible
- **Use indexed columns** in WHERE clauses
- **Avoid N+1 query problems** - use joins or getCollectionFromDB
- **Keep transactions short** - don't do unnecessary work in them

#### Security

- **Always escape user input** with escapeStringForDB
- **Validate player actions** against game rules
- **Never trust client data** - always validate on server
- **Use framework validation** (AT_* types) when possible

#### Code Organization

- **Keep methods focused** - each method should do one thing
- **Use utility methods** for common operations
- **Comment complex logic** for future maintenance
- **Follow naming conventions** consistently

#### Testing

- **Test edge cases** - minimum/maximum players, unusual game states
- **Test error conditions** - invalid moves, disallowed actions
- **Test database transactions** - ensure rollback works
- **Test with different game options** - variants affect logic

---

## Summary

Phase 3 has covered server-side game logic, the core of BGA game implementation:

**Key Concepts:**
- Game.php file structure and core methods
- Player information access and the active/current player distinction
- Database access methods and transaction handling
- BGA globals for game-wide state management
- Notification system for client communication
- Game statistics tracking and display
- PHP migration notes and autowire actions
- Best practices for secure, performant server-side code

**Next Steps:**
With server-side game logic mastered, you're ready for Phase 4, which covers client-side game interface (JavaScript) - building the interactive frontend that communicates with your server-side logic.
