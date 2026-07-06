# BGA Studio Developer Handbook - Phase 2: State Machine Architecture

## Chapter 4: State Machine Architecture

### Understanding the BGA State Machine

The state machine is the heart of BGA game development. It controls the flow of the game, determines which players can act at any given time, and manages transitions between different game phases. Mastering the state machine is essential for creating functional, bug-free games.

**Important:** To understand the game state machine, it's recommended that you read the BGA presentation "Focus on BGA game state machine" first, available from the Studio main page.

### State Machine Overview

The BGA state machine is a finite state machine that:
- Defines all possible states your game can be in
- Specifies which players are active in each state
- Determines what actions are available in each state
- Controls transitions between states based on game events
- Manages private states for individual players during multiactive phases

The state machine ensures that:
- Only valid actions can be taken at any time
- The game progresses according to your rules
- Players see appropriate status messages
- The client interface knows what to display and enable

### Modern State Machine Implementation

BGA has evolved to provide two main approaches to implementing state machines:

1. **State Classes (Recommended)** - Object-oriented approach with separate files for each state
2. **States Builder (Legacy but still supported)** - Array-based approach using GameStateBuilder

**Note:** The old states.inc.php file is deprecated. You should use State Classes for new development.

### State Classes Approach (Recommended)

State classes allow you to create a PHP class for each game state, providing better code organization and maintainability.

#### Overview

State classes are stored in the `modules/php/States/` directory. Each state is represented by a separate PHP class that extends `Bga\GameFramework\States\GameState`.

#### Example State Class Structure

The State class in `modules/php/States/PlayerTurn.php` has this structure:

```php
<?php
declare(strict_types=1);

namespace Bga\Games\<MyGameName>\States;

use Bga\GameFramework\StateType;
use Bga\GameFramework\States\GameState;
use Bga\GameFramework\States\PossibleAction;
use Bga\Games\<MyGameName>\Game;

class PlayerTurn extends GameState
{
    function __construct(
        protected Game $game,
    ) {
        parent::__construct($game,
            id: 2,
            type: StateType::ACTIVE_PLAYER,

            // optional
            description: clienttranslate('${actplayer} must play a card or pass'),
            descriptionMyTurn: clienttranslate('${you} must play a card or pass'),
            transitions: [],
            updateGameProgression: false,
            initialPrivate: null,
        );
    }

    public function getArgs(): array
    {
        // the data sent to the front when entering the state
        return [];
    } 

    function onEnteringState(int $activePlayerId) {
        // the code to run when entering the state
    }   

    #[PossibleAction]
    public function actPlayCard(int $cardId, int $activePlayerId, array $args): string
    {
        // the code to run when the player triggers actPlayCard with bgaPerformAction
    }

    function zombie(int $playerId): string {
        // the code to run when the player is a Zombie
    }
}
```

The state must extend `Bga\GameFramework\States\GameState` and follow the same `__construct` function as the example.

#### State Class Constructor Parameters

Only `game`, `id`, and `type` are mandatory. Other parameters are optional. The parameter name defaults to the class name (including capitalization).

**id (Mandatory)**
- Must be a positive integer
- Must be unique between all your states (don't use the same ID twice)
- Number 99 is reserved for the last game state (end of game) - don't modify it
- **Important:** When a game is in production and you change the ID of a state, all active games (including turn-based) will behave unpredictably

**type (Mandatory)**
Determines who can act in this state:
- `StateType::ACTIVE_PLAYER`: One player is active and must play
- `StateType::MULTIPLE_ACTIVE_PLAYER`: Multiple players can be active and must play
- `StateType::PRIVATE`: During multiactive states, players can independently move to different private parallel states
- `StateType::GAME`: No player is active. This is a transitional state to do something automatic specified by game rules

**name**
- The name of the game state is used to identify the state in your game logic
- Default: class name (as is)
- **Warning:** Don't put spaces and weird characters in the name (stick to identifiers). This could cause unexpected problems

**Accessing state name in PHP:**
```php
// Get current game state
$state = $this->gamestate->getCurrentMainState();
if( $state['name'] == 'myGameState' )
{
    // ...
}
```

**Accessing state name in JavaScript:**
```javascript
onEnteringState: function( stateName, args )
{
    console.log( 'Entering state: '+stateName );
    
    switch( stateName )
    {
        case 'myGameState':
            // Do some stuff at the beginning at this game state
            break;
    }
}
```

**description**
- The string displayed in the main action bar (top of screen) when the state is active to ALL players except the active player
- Must use `clienttranslate` for translation
- Can use `${actplayer}` to refer to the active player

```php
clienttranslate('${actplayer} must play a card or pass')
```

**Custom fields in description:**
```php
// In state class:
description: clienttranslate('${actplayer} must choose ${nbr} identical energies'),

// In getArgs method:
function getArgs(): array
{
    return [
        'nbr' => 2  // ${nbr} in description will be replaced by "2"
    ];    
}
```

**Note:** You can omit this for game states.

**Note:** You can use `${otherplayer}` to refer to some other player if you want this shown in player's color, but you must provide `otherplayer_id` as argument (along with `otherplayer`) to specify this player's ID, or the game won't load.

**descriptionMyTurn**
- Mandatory when state type is ACTIVE_PLAYER or MULTIPLE_ACTIVE_PLAYER
- The string displayed to the active player specifically
- Can use `${you}` instead of player name

```php
description: clienttranslate('${actplayer} can take some actions'),
descriptionMyTurn: clienttranslate('${you} can take some actions')
```

**Note:** You can use `${you}` in descriptionMyTurn so the description will display "You" instead of the player's name.

```php
descriptionMyTurn: clienttranslate('${you} can follow action of ${otherplayer}')
```

This requires state arguments for `otherplayer` and `otherplayer_id`.

**transitions**
- Defines which transitions are possible from this state
- Transitions are triggered by action methods returning transition names
- Format: `['transitionName' => targetStateId]`

```php
transitions: [
    'playCard' => 3, 
    'pass' => 3,
]
```

**updateGameProgression**
- Optional boolean (default: false)
- If true, the game progression bar updates when entering this state
- Use for states that represent significant game progress

**initialPrivate**
- Optional (default: null)
- Used during multiactive states to specify an initial private state
- See the section on private states for more details

#### State Class Methods

**getArgs(): array**
- Returns data sent to the frontend when entering the state
- This data is available in the `args` parameter of `onEnteringState` in JavaScript
- Use this to send state-specific information to the client

```php
public function getArgs(): array
{
    return [
        'possibleCards' => $this->game->getPossibleCards(),
        'mustPlay' => true,
    ];
}
```

**onEnteringState(int $activePlayerId)**
- Called when the state is entered
- Use this to perform initialization logic specific to this state
- `$activePlayerId` is the ID of the active player (if applicable)

```php
function onEnteringState(int $activePlayerId) {
    // Perform state-specific initialization
    $this->game->notifyAllUsers('newState', clienttranslate('Entering new state'), []);
}
```

**Possible Actions**
- Methods marked with `#[PossibleAction]` attribute can be called from the frontend using `bgaPerformAction`
- These methods implement the actual game logic for player actions
- Must return a string indicating the transition to take

```php
#[PossibleAction]
public function actPlayCard(int $cardId, int $activePlayerId, array $args): string
{
    // Validate and execute the action
    $this->game->validateCardPlay($cardId, $activePlayerId);
    $this->game->playCard($cardId, $activePlayerId);
    
    // Return the transition name
    return 'playCard';
}
```

**zombie(int $playerId): string**
- Called when a player is in zombie mode (disconnected)
- Implement automatic play logic for disconnected players
- Must return a string indicating the transition to take

```php
function zombie(int $playerId): string {
    // Automatic action for zombie player
    $cardId = $this->game->getRandomCard($playerId);
    $this->game->playCard($cardId, $playerId);
    
    return 'playCard';
}
```

### State Types in Detail

#### ACTIVE_PLAYER State

Only one player is active and must take action. This is the most common state type for turn-based games.

**Characteristics:**
- Exactly one player can perform actions
- Other players see a description of what the active player is doing
- The active player sees descriptionMyTurn
- Use for standard turn-based gameplay

**Example:**
```php
type: StateType::ACTIVE_PLAYER,
description: clienttranslate('${actplayer} is taking their turn'),
descriptionMyTurn: clienttranslate('${you} are taking your turn'),
```

#### MULTIPLE_ACTIVE_PLAYER State

Multiple players can be active simultaneously. Use this for:
- Simultaneous action selection
- Bidding phases
- Real-time elements in turn-based games
- Any phase where multiple players act independently

**Characteristics:**
- Multiple players can perform actions at the same time
- Each active player sees descriptionMyTurn
- Non-active players see the regular description
- The state doesn't automatically advance until all players have acted (or a timeout)

**Example:**
```php
type: StateType::MULTIPLE_ACTIVE_PLAYER,
description: clienttranslate('Players are choosing their actions'),
descriptionMyTurn: clienttranslate('${you} must choose your action'),
```

#### PRIVATE State

Used during multiactive states when players need to move to different private parallel states. This allows for complex multi-phase interactions where players might be in different states simultaneously.

**Use cases:**
- Secret selection phases
- Individual decision-making within a multiactive phase
- Complex turn structures with sub-states

**Characteristics:**
- Each player can be in a different private state
- Players can transition independently
- Requires careful state management

**Example:**
```php
type: StateType::PRIVATE,
initialPrivate: 'initialPrivateState',
```

#### GAME State

No player is active. This is a transitional state for automatic game logic.

**Use cases:**
- Dealing cards
- Calculating scores
- Checking win conditions
- Automatic cleanup between turns
- AI/bot actions

**Characteristics:**
- No player input is expected
- The state performs automatic logic
- Usually transitions quickly to another state
- No description needed (can be empty string)

**Example:**
```php
type: StateType::GAME,
description: '',  // Empty since this is transitional
```

### State Transitions

State transitions control how the game moves from one state to another. Transitions are triggered by:

1. **Action methods** returning transition names
2. **Automatic game logic** in GAME states
3. **Timeout conditions** in multiactive states

#### Defining Transitions

In state classes, transitions are defined in the constructor:

```php
transitions: [
    'playCard' => 3,     // If action returns 'playCard', go to state 3
    'pass' => 4,         // If action returns 'pass', go to state 4
    'timeout' => 5,      // If timeout occurs, go to state 5
]
```

#### Triggering Transitions

**From action methods:**
```php
#[PossibleAction]
public function actPlayCard(int $cardId, int $activePlayerId, array $args): string
{
    // ... game logic ...
    
    // Return the transition name
    return 'playCard';  // This triggers transition to state 3
}
```

**From game logic (in GAME states):**
```php
function onEnteringState(int $activePlayerId) {
    // Perform automatic logic
    $this->game->dealCards();
    
    // Transition to next state
    $this->game->gamestate->nextState('dealComplete');
}
```

#### Transition Methods

The framework provides several methods for state transitions:

**nextState(string $transitionName)**
- Transition to the next state based on the transition name
- Used within action methods or game logic

**setState(int $stateId)**
- Force transition to a specific state ID
- Use sparingly - can break the state machine flow if used incorrectly

**checkGameEnd()**
- Check if the game should end
- Automatically transitions to state 99 if game end conditions are met

### State Arguments and Data Flow

State arguments allow you to pass data between the server and client when entering states.

#### Server to Client (getArgs)

Use the `getArgs()` method to send data to the client:

```php
public function getArgs(): array
{
    return [
        'selectedCards' => $this->game->getSelectedCards(),
        'score' => $this->game->getCurrentScore(),
        'message' => clienttranslate('Choose a card to play'),
    ];
}
```

This data is available in JavaScript:

```javascript
onEnteringState: function( stateName, args )
{
    console.log( args.selectedCards );
    console.log( args.score );
}
```

#### Client to Server (Action Arguments)

Action methods receive arguments from the client:

```php
#[PossibleAction]
public function actPlayCard(int $cardId, int $activePlayerId, array $args): string
{
    // $args contains additional data from the client
    $extraData = $args['extraData'] ?? null;
    
    // ... game logic ...
}
```

#### Custom Description Variables

You can use custom variables in descriptions by including them in getArgs:

```php
description: clienttranslate('${actplayer} must choose ${nbr} cards'),

public function getArgs(): array
{
    return [
        'nbr' => $this->game->getCardsToChoose(),
    ];
}
```

### Client-Side State Handling

The JavaScript side needs to handle state changes appropriately.

#### onEnteringState

Called when entering a new state:

```javascript
onEnteringState: function( stateName, args )
{
    console.log( 'Entering state: '+stateName );
    
    switch( stateName )
    {
        case 'playerTurn':
            // Update UI for player turn
            this.updatePlayerTurnUI( args );
            break;
            
        case 'multiplayerPhase':
            // Update UI for multiplayer phase
            this.updateMultiplayerUI( args );
            break;
    }
}
```

#### onLeavingState

Called when leaving a state:

```javascript
onLeavingState: function( stateName )
{
    console.log( 'Leaving state: '+stateName );
    
    switch( stateName )
    {
        case 'playerTurn':
            // Clean up player turn UI
            this.cleanupPlayerTurnUI();
            break;
    }
}
```

#### Updating Action Buttons

Update action buttons based on the current state:

```javascript
updateActionButtons: function( stateName, args )
{
    if( this.isCurrentPlayerActive() )
    {
        switch( stateName )
        {
            case 'playerTurn':
                this.addActionButton( 'playCard_button', _('Play card'), () => this.onPlayCard() );
                this.addActionButton( 'pass_button', _('Pass'), () => this.onPass() );
                break;
        }
    }
}
```

### Zombie Mode and State Handling

Zombie mode handles disconnected players. Each state should implement zombie behavior.

#### Implementing Zombie Methods

```php
function zombie(int $playerId): string {
    // Check if this player is the active player
    if ($this->game->getActivePlayerId() == $playerId) {
        // Perform automatic action
        $this->game->autoPlayForZombie($playerId);
        return 'playCard';
    }
    
    // If not active, just stay in current state
    return '';
}
```

#### Zombie Strategy

Common zombie strategies:
- **Random action**: Choose a random valid action
- **Pass/Skip**: Always pass or skip the turn
- **Conservative**: Choose the safest action
- **Aggressive**: Choose the most aggressive action
- **Timeout-based**: Wait for timeout then take default action

### State Machine Debugging

Debugging state machine issues can be challenging. Here are some tips:

#### Check Current State

```php
// In PHP
$state = $this->gamestate->getCurrentMainState();
error_log("Current state: " . $state['name'] . " (ID: " . $state['id'] . ")");
```

```javascript
// In JavaScript
console.log("Current state: " + this.gamedatas.gamestate.name);
```

#### Check Active Player

```php
// In PHP
$activePlayerId = $this->game->getActivePlayerId();
error_log("Active player: " . $activePlayerId);
```

```javascript
// In JavaScript
console.log("Active player: " + this.player_id);
console.log("Is current player active: " + this.isCurrentPlayerActive());
```

#### Log State Transitions

```php
function onEnteringState(int $activePlayerId) {
    error_log("Entering state " . $this->getId() . " for player " . $activePlayerId);
}
```

#### Use Studio Debugging Tools

The Studio provides debugging tools at the bottom of the game area:
- **Input/Output debugging section**: Shows AJAX calls and notifications
- **Game database access**: View current game state in database
- **BGA logs**: Check PHP logs for state-related errors

### Migration from Old State Machine

If you're migrating from the old states.inc.php approach:

#### State Management Functions

Several state-related functions have been deprecated:

- Replace `$this->gamestate->state()` with `$this->getCurrentMainState()` or `$this->getCurrentState(int $playerId)`
- Replace `$this->getState()` with `$this->getCurrentMainStateId()` or `$this->getCurrentStateId(int $playerId)`
- Replace `$this->getPrivateState($playerId)` with `$this->getCurrentState($playerId)`
- Replace `$this->gamestate->states` access with `$this->getCurrentMainState()` or `$this->getCurrentState(int $playerId)`
- Replace `$this->isMutiactiveState()` (misspelled) with `$this->isMultiactiveState()`

#### Migration Steps

1. Create a State class for each state (except 1 and 99 if still in states.inc.php)
2. Move the state definition into the class
3. Adapt the "st", "arg", "actXXX", and "zombie" functions into the class
4. When all classes are migrated, remove the states.inc.php file

### Best Practices

#### State Design

- **Keep states focused**: Each state should have a single, clear purpose
- **Minimize state count**: Don't create more states than necessary
- **Use descriptive names**: State names should clearly indicate their purpose
- **Plan transitions**: Map out your state machine before implementing

#### Error Handling

- **Validate actions**: Always validate player actions before executing
- **Handle edge cases**: Consider what happens with unusual game states
- **Provide feedback**: Notify players of state changes and action results

#### Performance

- **Minimize database queries**: Cache data when possible
- **Optimize getArgs**: Only send necessary data to the client
- **Use transitions efficiently**: Avoid unnecessary state changes

#### Testing

- **Test all transitions**: Verify every possible state transition
- **Test zombie mode**: Ensure zombie players don't break the game
- **Test edge cases**: What happens with minimum/maximum players?
- **Test timeouts**: Verify timeout behavior in multiactive states

### Common State Machine Patterns

#### Simple Turn-Based Game

```
State 2 (playerTurn) -> State 3 (nextPlayerTurn) -> ... -> State 99 (gameEnd)
```

#### Multiplayer Phase

```
State 2 (multiplayerChoice) -> State 3 (resolveChoices) -> State 2 (next round)
```

#### Auction/Bidding

```
State 2 (bidding) -> State 3 (resolveBid) -> State 2 (next bidder) or State 4 (auctionEnd)
```

#### Simultaneous Action Selection

```
State 2 (chooseActions) -> State 3 (resolveActions) -> State 4 (nextRound)
```

### Troubleshooting Common Issues

#### Game Stuck in a State

- Check if transitions are properly defined
- Verify action methods are returning correct transition names
- Ensure zombie mode is implemented for all states
- Check for infinite loops in state transitions

#### Players Can't Act

- Verify the state type is correct (ACTIVE_PLAYER vs GAME)
- Check if the player is actually the active player
- Ensure action buttons are properly enabled in JavaScript
- Verify possible actions are marked with #[PossibleAction]

#### State Not Updating

- Check if nextState is being called correctly
- Verify transition names match exactly
- Ensure the state ID is valid
- Check for PHP errors in onEnteringState

#### Multiactive State Issues

- Verify all players can act independently
- Check timeout settings
- Ensure private states are correctly configured
- Test with different player counts

---

## Summary

Phase 2 has covered the state machine architecture, the core system that controls game flow in BGA games:

**Key Concepts:**
- State machine fundamentals and purpose
- State classes approach (recommended)
- State types: ACTIVE_PLAYER, MULTIPLE_ACTIVE_PLAYER, PRIVATE, GAME
- State transitions and triggering mechanisms
- State arguments and data flow between server and client
- Client-side state handling
- Zombie mode implementation
- State machine debugging and best practices

**Next Steps:**
With the state machine architecture understood, you're ready for Phase 3, which covers server-side game logic (PHP) - implementing the actual game rules and mechanics that operate within the state machine framework you've just learned.
