# BGA Studio Developer Handbook - Phase 7: Advanced Features and Testing

## Chapter 9: Internationalization (i18n)

### Localization Overview

Localization for BGA games happens largely on the CLIENT. Games must be developed in English, and English strings are sent to the client.

**Important:** If you've worked on systems where translation happens at the server and localized strings are sent to the client, you must unlearn that approach. Just stick with English and send untranslated English strings. The magic happens at the client.

### How Strings Are Translated

When developing your game, all strings must be in English and coherent with the English version of the game. The BGA community translates these strings into various languages.

### Translation Programming Requirements

The golden rules for translation:

1. **Server-side strings:** Wrap any string that needs translation on the client in `clienttranslate()` function:
   ```php
   $my_response = clienttranslate('Hey translators, please translate this string');
   ```
   `clienttranslate()` doesn't actually do anything (just passes text through), but the translation engine searches your code for strings wrapped in this function to build the list of strings that need translation.

2. **Client-side strings:** Wrap text in `_()`:
   - If you pass a string constant like `_('This is my string')`, the parser automatically detects and adds it to the translation list AND displays the local translation
   - If you pass a variable like `_(args.my_message)`, ensure the variable is set to an English string defined in PHP with `clienttranslate()` or in JavaScript with `_()`

3. **Notification messages:** Strings used as messages for `notify->all` or `notify->player` automatically display translated versions on the client. Just ensure they're wrapped in `clienttranslate()` on the server.

4. **State descriptions:** Strings used as "description" or "descriptionmyturn" for states automatically translate on the client. Wrap in `clienttranslate()` on the server.

5. **Game options:** Strings in pre-game option screen automatically translate. Wrap in `totranslate()` on the server (not `clienttranslate()` - this file is processed separately for main site translation). If you need the same string in-game, declare it elsewhere with `clienttranslate()`.

6. **Statistics:** Strings in statistics screen work like game options. Wrap in `totranslate()` on the server.

7. **Parameters with translation:** If parameters in notify calls or state descriptions contain text needing translation, use the 'i18n' argument to specify which parameters should be translated.

### What Strings Should Be Marked

**YES:**
- Every text visible to players during normal gameplay (tooltips, texts on cards, error messages)

**NO:**
- Error messages that shouldn't happen (unexpected errors)
- Player names (don't put player_name or PHP keys sent via notification that are player names)
- Proper names of characters or places (consult publisher)
- Numbers (e.g., `_("42")`)
- Internal keywords

### English String Rules

For coherent interface, follow these rules about final periods:

**General rule:**
- If a sentence is displayed isolated in the interface → no final period
- If a sentence is followed or could be followed by another text → use final period

**Examples:**
- Button labels: "Play card" (no period)
- Tooltips: "This card gives you 2 points" (no period)
- Status messages: "Player X played a card." (period - could be followed by more text)
- Error messages: "Invalid move" (no period - isolated)

### Translation with Parameters

When using parameters in notifications or state descriptions, use the 'i18n' array to specify which parameters need translation:

```php
$this->bga->notify->all('cardPlayed', clienttranslate('${player_name} played ${card_name}'), [
    'i18n' => ['card_name'],
    'player_name' => $this->getPlayerNameById($playerId),
    'card_id' => $cardId,
    'card_name' => $this->getCardName($cardId),
]);
```

---

## Chapter 10: Bots and Artificial Intelligence

### Overview

There is no framework support for AI/Bots currently, so it's all custom implementation.

### Games with Bot Support

The following games have modes that support bots: Conspiracy, Glow, Crew, Crew Deepsea, Tapestry.

### Bot Implementation Techniques

#### Testing Bot

A testing bot is a JavaScript bot that presses buttons on behalf of a player. It's handy for testing on Studio.

**Recommended approach:** Add a Studio-only button (with debug bar) "Run bot/Stop bot". When running, it can react to state changes and press buttons. Example: Battleship (only appears on Studio as testing-only).

#### JavaScript AI

Currently not feasible - JS code requires a real player connected to the game with a browser, so it cannot run as an AI engine.

#### Server Bot as Registered Game Player

This would be ideal, but currently only Can't Stop uses this technique, and no other game can use it.

#### Server Bot as Game State Action (Recommended)

This is the only feasible way in production. In addition to whatever game states are doing, it can handle fake players and simulate their moves.

### Bot Implementation Details

#### Bot Player ID

Reserve non-existing player IDs for bots (e.g., 1-6). If the bot needs color and order, see below.

#### Bot Color, Order, and Resources

Create a table similar to the player table to track bot color, name, score, score_aux, and other data:

```sql
CREATE TABLE IF NOT EXISTS `playerextra` (
  `player_id` int(10) unsigned NOT NULL,
  `player_name` varchar(32) NOT NULL,
  `player_avatar` varchar(10) NOT NULL,
  `player_color` varchar(6) NOT NULL,
  `player_no` int(10) NOT NULL,
  `player_score` int(10) NOT NULL DEFAULT '0',
  `player_score_aux` int(10) NOT NULL DEFAULT '0',
  `player_ai` tinyint(1) NOT NULL DEFAULT '0' COMMENT '1 = player is an AI',
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

#### Bot Actions

- All actions that can be done by Bot must have `$player_id` as argument and not use active player
- Separate code of AJAX actions from functional code, so functions can run from AJAX action or game state action
- If using `getPlayerNameById` to send player_name in notification, wrap it (same for player color)

```php
public function getPlayerName(int $player_id) {
    if ($player_id == PLAYER_AUTOMA)
        return _('Automa');
    return $this->getPlayerNameById($player_id);
}
```

Create a function like `loadPlayersBasicInfosWithBots` that returns similar data to `loadPlayersBasicInfos` but with bot IDs. Cache the result if using frequently:

```php
function loadPlayersBasicInfosWithBots() {
    $player_basic = $this->loadPlayersBasicInfos();
    if (!$this->isAutoma())
        return $player_basic;           
    if (!isset($this->player_bots)) {
        $this->player_bots = $this->getCollectionFromDb("SELECT * FROM playerextra");
    }
    return $this->player_bots + $player_basic;
}
```

#### Bot Player Panel

If you want the bot on the player panel, use `this.bga.playerPanels.addAutomataPlayerPanel`.

#### Bot Player Notifications

When sending notification with `${player_name}`, also send 'player_id' with your fake ID. Additionally, `getAllDatas()` should contain a record matching the fake player ID in the players field:

```php
protected function getAllDatas() {
    $result = [];
    // ...
    $result['players'][$player_id]['id'] = $player['id'];
    $result['players'][$player_id]['score'] = $player['score'];
    $result['players'][$player_id]['color'] = $player['color'];
    $result['players'][$player_id]['name'] = $player['name'];
    // ...
    return $result;
}
```

---

## Chapter 11: Advanced BGA Components

### BgaAnimations

The BgaAnimations component provides a modern animation system for BGA games, offering smoother and more flexible animations than the legacy Dojo-based system.

### BgaAutofit

BgaAutofit automatically adjusts game elements to fit different screen sizes and orientations, ensuring your game looks good on all devices.

### BgaCards

BgaCards is the modern replacement for Stock specifically designed for card games. It provides:
- Better performance
- More features
- Easier API
- Better TypeScript support

### BgaDice

BgaDice is a component for displaying and animating dice in your game.

### BgaScoreSheet

BgaScoreSheet provides a score sheet component for games with complex scoring systems.

### ExpandableSection

ExpandableSection allows you to create collapsible/expandable UI sections for organizing complex interfaces.

### Counter

Counter is a component for displaying dynamic numeric values with smooth animations.

### BGA Undo Policy

BGA has specific policies and guidelines for implementing undo functionality in games. Review the BGA_Undo_policy documentation for details on:
- When undo is required
- How to implement undo correctly
- Undo limitations and edge cases

### Zombie Mode

Zombie mode handles disconnected players automatically. The Zombie_Mode documentation covers:
- How zombie mode works
- Implementing zombie behavior in states
- Best practices for zombie handling

---

## Chapter 12: Testing and Debugging

### Manual Testing on BGA

For manual testing, the most important things to know are:
- How to start/stop game in one click
- How to switch between players in one click
- How to save/restore the game state
- How to construct the game state automatically

All of these are described in Tools_and_tips_of_BGA_Studio.

### Manual Testing Locally

For HTML/CSS development, file sync is almost instant, so you don't save much by testing locally. However, if internet is a challenge, see Tools_and_tips_of_BGA_Studio#Speed_up_CSS_development_and_layout for tips.

### Automated Testing

#### JavaScript Testing

For TypeScript projects, you can set up automated testing with:
- Dev dependencies on mocha, jsdom, and sinon
- Build tools for TypeScript
- Typescript code in src/
- Test code in src/tests/
- Tests have their own src/tests/tsconfig.json
- File src/tests/setup.ts contains framework and global stubs

The configuration is verbose. Check project "dojoless" or bga-dojoless on GitHub for examples.

#### PHP Testing with PHPUnit

**Install PHPUnit:**
```bash
cd /home/<yourusername>/php-composer
composer require --dev phpunit/phpunit ^13
```

Add `.phpunit.cache` to sftp.json ignore list (and .gitignore if using git). You can push unit tests to FTP - future maintainers can use them to ensure nothing breaks on updates.

**Setup shell function:**
```bash
phpunit() {
 /home/<yourusername>/php-composer/vendor/bin/phpunit \
   -c "$PWD/phpunit.xml.dist" \
   --bootstrap "$PWD/tests/bootstrap.php" \
   "$@"
}
```

**Run tests:**
```bash
phpunit
phpunit tests/BoardManagerTest.php
phpunit --filter testGivesExtraTime
```

**Setup minimal files:**

**phpunit.xml.dist:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="tests/bootstrap.php"
         colors="true"
         cacheDirectory=".phpunit.cache">
  <testsuites>
    <testsuite name="Reversi">
      <directory>tests</directory>
    </testsuite>
  </testsuites>
</phpunit>
```

**tests/bootstrap.php:**
```php
<?php
declare(strict_types=1);

require_once __DIR__ . '/stubs/BgaFrameworkStubs.php';

$autoload = __DIR__ . '/../vendor/autoload.php';
if (file_exists($autoload)) {
    require_once $autoload;
}

spl_autoload_register(static function (string $class): void {
    $prefix = 'Bga\\Games\\Reversi\\';

    if (!str_starts_with($class, $prefix)) {
        return;
    }

    $relativeClass = substr($class, strlen($prefix));
    $path = __DIR__ . '/../modules/php/' . str_replace('\\', '/', $relativeClass) . '.php';

    if (file_exists($path)) {
        require_once $path;
    }
});
```

**Create framework stubs in tests/stubs/BgaFrameworkStubs.php** - stub framework classes and methods.

**Example test:**
```php
<?php
declare(strict_types=1);

namespace Tests;

use Bga\Games\Reversi\BoardManager;
use Bga\Games\Reversi\Game;
use PHPUnit\Framework\TestCase;

final class BoardManagerTest extends TestCase
{
    public function testGetPossibleMovesOnInitialBoardForBlackPlayer(): void
    {
        $board = $this->createEmptyBoard(8);
        $board[4][4] = 2;
        $board[5][5] = 2;
        $board[4][5] = 1;
        $board[5][4] = 1;

        $game = $this->createGame(8);
        $boardManager = $this->createBoardManager($game, $board);

        $moves = $boardManager->getPossibleMoves(1);

        self::assertSame(
            [
                3 => [4 => true],
                4 => [3 => true],
                5 => [6 => true],
                6 => [5 => true],
            ],
            $moves,
        );
    }

    // ... more tests
}
```

### Practical Debugging

The Practical_debugging documentation covers:
- Common debugging techniques
- Using Studio debugging tools
- Analyzing logs
- Troubleshooting common issues

### Troubleshooting

The Troubleshooting documentation provides solutions to common problems developers encounter.

### Studio Logs

Studio logs help you diagnose issues by providing detailed information about:
- PHP errors
- Database queries
- State transitions
- Notification issues

---

## Summary

Phase 7 has covered advanced features and testing:

**Key Topics:**
- Internationalization (i18n) and translation system
- Bot and AI implementation techniques
- Advanced BGA components (BgaAnimations, BgaCards, etc.)
- Undo policy and zombie mode
- Manual and automated testing strategies
- PHP testing with PHPUnit
- Debugging and troubleshooting

**Next Steps:**
With advanced features and testing covered, you're ready for Phase 8, the final phase covering publishing, reference materials, and additional resources.
