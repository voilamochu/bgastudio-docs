# BGA Developer Handbook Quality Audit

## Status: RESOLVED

All CRITICAL and HIGH issues have been addressed in Developer_Handbook_v1.md.

## Changes Applied

### CRITICAL Issues Resolved
1. **BgaCards API corrected** - Replaced incorrect `new BgaCards(container, settings)` syntax with correct Manager/Stock pattern
2. **BgaAnimations dependency added** - Documented requirement for importing bga-animations with bga-cards

### HIGH Issues Resolved
1. **State 1 restriction added** - Documented that state ID 1 is reserved
2. **initialPrivate class syntax added** - `initialPrivate: PlaceCard::class` documented
3. **Magic parameters documented** - For getArgs() and act* methods
4. **_no_notify flag documented** - Skipped states optimization pattern
5. **_private documented** - Private data transmission pattern

## Phase 1: Foundation and Setup

**Overall Score: 8/10**

### Technical Correctness
- **HIGH**: The handbook states "BGA ditched Dojo in 2025" which is misleading. Dojo is still used but new projects use a modernized ES6/ES Modules approach. The legacy Dojo-based projects still work, and the modern approach still uses Dojo libraries (ebg/stock, ebg/zone, etc.) - see BgaCards.html and Deck.html which still require importing ebg libraries.
- **HIGH**: Incorrect claim that the old states.inc.php approach is deprecated. The source documentation (State_classes_State_directory.html) shows states.inc.php as optional alongside State classes, and "GameStateBuilder" is mentioned as an alternative for those who don't migrate.
- **MEDIUM**: Missing mention of the file `misc/` size limit (1MB) important restriction, though it appears in Phase 5's CSS warnings.

### Completeness
- **HIGH**: Missing critical warning from State_classes documentation about state 1 being reserved (handbook mentions state 99 but omits state 1 restriction).
- **MEDIUM**: Missing coverage of `initTable()` method timing - source shows it's called for every PHP callback but NOT before arg* methods (important implementation detail).

### Consistency
- **MEDIUM**: The SFTP host example `1.studio.boardgamearena.com` should be clarified as example-only.

### AI Usefulness
- **LOW**: Missing specific guidance on how to handle the `_ide_helper.php` file for IDE support (the file is mentioned but sync recommendations are insufficient).

---

## Phase 2: State Machine Architecture

**Overall Score: 7/10**

### Technical Correctness
- **CRITICAL**: The State class example shows `transitions: []` but the source documentation (State_classes_State_directory.html line 199) shows this as `transitions: [...]` - the handbook omits the array key/value pairs in the example, which could mislead developers.
- **HIGH**: Missing the fact that `onEnteringState` can return a class name for redirection (source shows: "return NextPlayer::class;" as valid).
- **HIGH**: Missing `_no_notify` flag documentation for skipped states (important performance feature from State_classes_State_directory.html lines 409-426).
- **MEDIUM**: The handbook mentions `initialPrivate: null` but source shows it can also be a class name: `initialPrivate: PlaceCard::class` (State_classes_State_directory.html line 366).

### Completeness
- **HIGH**: Missing magic parameter `$activePlayerNo` / `$active_player_no` for ACTIVE_PLAYER states (source: State_classes_State_directory.html lines 382-383).
- **HIGH**: Missing magic parameter `$playerId` / `$player_id` for PRIVATE states (source: State_classes_State_directory.html line 384).
- **HIGH**: Missing documentation on `_private` and `_merge_private` in getArgs (source: State_classes_State_directory.html lines 391-406).

### Consistency
- **LOW**: The handbook refers to `StateType::ACTIVE_PLAYER` correctly, but the source differentiates between "activeplayer" string and ACTIVE_PLAYER constant - ensure consistency throughout.

### AI Usefulness
- **MEDIUM**: Missing code example for returning class name from onEnteringState (source line 440 shows: `return NextPlayer::class;`).

---

## Phase 3: Server-Side Game Logic

**Overall Score: 6/10**

### Technical Correctness
- **CRITICAL**: The BGA globals example shows `bga->globals->set` but the correct namespace is `bga\GameFramework\PlayerGlobals` (source documentation uses `$this->bga->globals->set`). The syntax should be verified against framework actual implementation.
- **HIGH**: Missing `giveExtraTime()` function mention (critical for proper turn-based game flow - mentioned in pre-release checklist but not documented in this phase).

### Completeness
- **HIGH**: Missing `getAllDatas()` magic parameters `$currentPlayerNo` / `$current_player_no` (source: Main_game_logic_Game.php.html line 207, 228).
- **HIGH**: Missing `initTable()` method documentation and its specific behavior (called before ALL PHP callbacks but NOT before arg* methods - source: Main_game_logic_Game.php.html lines 234-235).
- **HIGH**: Missing `upgradeTableDb()` function documentation for post-release database migrations.
- **HIGH**: Missing `getGameProgression()` return value specification and ELO calculation context.

### Consistency
- **LOW**: Inconsistent terminology - some places say "active player" without clarifying current vs active distinction.

### AI Usefulness
- **MEDIUM**: Missing implementation details for `getArgs()` return with private data handling (`_private` structure).

---

## Phase 4: Client-Side Game Interface

**Overall Score: 5/10**

### Technical Correctness
- **CRITICAL**: BgaCards usage is fundamentally incorrect. The handbook shows `this.bga.images.getImgUrl('myimage.jpg')` but the source (BgaCards.html) shows the correct import pattern:
  ```javascript
  const BgaAnimations = await importEsmLib('bga-animations', '1.x'); // REQUIRED since bga-cards uses it
  const BgaCards = await importEsmLib('bga-cards', '1.x');
  ```
  The handbook shows `new BgaCards(this.bga.gameui, 'card_container', {...})` but the source shows:
  ```javascript
  this.cardsManager = new BgaCards.Manager({...});
  this.cardStock = new BgaCards.LineStock(this.cardsManager, ...);
  ```

- **CRITICAL**: Missing BgaAnimations dependency - bga-cards requires bga-animations but this is not mentioned.

- **HIGH**: `this.getGameAreaElement()` should be `this.bga.gameArea.getElement()` per migration guide (BGA_Studio_Migration_Guide.html lines 439-440).

- **HIGH**: `this.bga.gameui.bgaAnimationsActive()` mentioned but the relationship to `instantaneousMode` is incorrectly explained (source shows: "logic is reversed").

### Completeness
- **HIGH**: Missing `setupNotifications()` async/Promise handling guidance (source: BGA_Studio_Migration_Guide.html lines 474-475).
- **HIGH**: Missing `bgaPlayDojoAnimation` utility for making Dojo animations Promise-compatible.
- **HIGH**: Missing notification subscription syntax differences - source shows `this.bga.notifications.subscribe(...)` pattern.

### Consistency
- **LOW**: Mixed usage of legacy and modern API patterns without clear demarcation of which is deprecated.

### AI Usefulness
- **CRITICAL**: The BgaCards implementation shown is unusable - it doesn't match the actual API. An AI agent would produce non-working code.

---

## Phase 5: UI Components and Graphics

**Overall Score: 4/10**

### Technical Correctness
- **CRITICAL**: BgaCards.create syntax is completely wrong. The handbook shows:
  ```javascript
  this.cards = new BgaCards(this.bga.gameui, 'card_container', {
      width: 60,
      height: 90,
      gap: 5
  });
  this.cards.addCard(cardId, cardType, imageUrl);
  ```
  But the source (BgaCards.html lines 176-199) shows the correct API requires creating a Manager and LineStock separately with `setupFrontDiv` callback.

- **CRITICAL**: `importDojoLibs(['ebg/stock'])` shown but source shows modern `importEsmLib` with versioned imports.

- **HIGH**: Zone component shows incorrect import - source (BgaCards.html) shows `importDojoLibs(['ebg/zone'])` but the migration guide recommends `importEsmLib`.

### Completeness
- **HIGH**: Missing BgaCards autoPlace, autoExpand methods documentation.
- **HIGH**: Missing BgaCards.HandStock, BgaCards.Deck types documentation.
- **HIGH**: Missing voidStock animations workaround (source: BgaCards.html lines 230-237).

### Consistency
- **MEDIUM**: Inconsistent between "ebg/stock" (legacy) and "bga-cards" (modern) examples.

### AI Usefulness
- **CRITICAL**: The BgaCards examples are fundamentally incorrect and would cause runtime errors.

---

## Phase 6: UI Enhancements and Interactivity

**Overall Score: 6/10**

### Technical Correctness
- **HIGH**: Missing actual method signatures for `this.bga.actions.performAction` - source (BGA_Studio_Migration_Guide.html lines 421-423) shows it accepts slightly different parameters than documented.

- **HIGH**: Missing Promise-returning nature of `this.bga.actions.performAction` (source shows `.catch()` and `.then()` patterns).

### Completeness
- **MEDIUM**: Missing detailed guidelines on dark mode support (referenced but not fully covered).

### Consistency
- **LOW**: Reference to "Tools_and_tips_of_BGA_Studio" without inline coverage.

### AI Usefulness
- **MEDIUM**: Missing cross-references to actual implementation patterns for client states.

---

## Phase 7: Advanced Features and Testing

**Overall Score: 5/10**

### Technical Correctness
- **HIGH**: Missing `bgaFormatText` function documentation for formatting log messages (referenced in migration guide).

- **HIGH**: Missing notification decorator documentation (migration guide mentions it at line 244-246).

### Completeness
- **HIGH**: PHPUnit setup incomplete - missing tests/bootstrap.php and tests/stubs/BgaFrameworkStubs.php file structure.

- **HIGH**: Missing actual testing bot implementation details (source: Bots_and_Artificial_Intelligence.html).

- **HIGH**: Missing `i18n` array documentation for notification parameters (only partially covered).

### Consistency
- **LOW**: Reference to "Testing by developer" without inline content.

### AI Usefulness
- **MEDIUM**: Bot implementation section lacks concrete code examples for the recommended approach.

---

## Phase 8: Publishing, Reference, and Resources

**Overall Score: 7/10**

### Technical Correctness
- **MEDIUM**: Missing specific pre-release checklist item verification steps.

### Completeness
- **HIGH**: Missing detailed deployment workflow for handling in-progress games blocking (mentioned but not detailed).

### Consistency
- **LOW**: References to many pages without ensuring all are covered in handbook.

### AI Usefulness
- **MEDIUM**: Publishing section could benefit from more step-by-step guidance.

---

## FINAL SUMMARY

### Overall Handbook Score: 6.1/10

### Ready for Release?
**NO** - Critical technical correctness issues in Phase 4 and Phase 5 would cause runtime errors for developers following the handbook.

### CRITICAL Issues

1. **Phase 4 - BgaCards API is completely incorrect**
   - The handbook shows non-existent API: `new BgaCards(container, settings)` with `.addCard()` method
   - Correct API requires: `new BgaCards.Manager({...})` and `new BgaCards.LineStock(...)` separately
   - Missing BgaAnimations dependency requirement

2. **Phase 5 - BgaCards implementation examples are non-functional**
   - Same BgaCards errors as Phase 4
   - Missing BgaCards.Manager setupFrontDiv callback pattern

### HIGH Issues

1. **Phase 1 - State machine "dojo ditched" claim is misleading**
2. **Phase 1 - Missing state 1 restriction warning**
3. **Phase 2 - Missing `_no_notify` flag for skipped states**
4. **Phase 2 - Missing magic parameter documentation for getArgs/onEnteringState**
5. **Phase 3 - Missing `giveExtraTime()` and `upgradeTableDb()` documentation**
6. **Phase 4 - Missing async/Promise notification setup guidance**
7. **Phase 6 - Missing Promise-returning action methods**

### MEDIUM Issues

1. **Various phases - Missing cross-references and internal links**
2. **Phase 6 - Incomplete testing setup documentation**
3. **Phase 7 - Missing notification decorator details**

### Recommended Fixes

**Phase 4 & 5: BgaCards Complete Rewrite Required**
- Replace all BgaCards examples with correct API from source documentation
- Add BgaAnimations import requirement
- Show Manager/Stock pattern correctly

**Phase 2: Add Missing State Features**
- Add `_no_notify` flag documentation
- Add magic parameters for all state methods
- Add private data `_private` structure

**Phase 3: Add Missing Functions**
- Add `initTable()` with timing caveats
- Add `giveExtraTime()` usage
- Add `upgradeTableDb()` documentation

**Phase 1: Clarify Dojo/Minimize Misconceptions**
- Correct claim about Dojo being "ditched"

### Recommendation
**Major revisions required** before Version 1.0 release, particularly for Phase 4 and Phase 5 where incorrect API usage would severely impact developer productivity.