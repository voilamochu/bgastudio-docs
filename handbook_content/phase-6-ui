# BGA Studio Developer Handbook - Phase 6: UI Enhancements and Interactivity

## Chapter 8: UI Enhancements and Interactivity

### Overview

This chapter covers advanced UI features and interactivity patterns that enhance the user experience and provide polish to your game interface.

### BGA Studio Cookbook

The BGA Studio Cookbook provides design and implementation recipes for common UI patterns and challenges.

#### Visual Effects, Layout and Animation

**DOM Manipulations**

**Create pieces dynamically (string concatenation):**
```javascript
div = `<div class='meeple_${color}'></div>`;
```

**Create all pieces statically:**
- Create ALL game pieces in HTML template (.tpl)
- All pieces should have unique, meaningful IDs (e.g., meeple_red_1)
- Do not use inline styling
- Player-specific pieces should use color identification (English name, hex value, or color number)
- Pieces should have separated classes for color, type, etc. for easy styling

**Example template:**
```html
<div id="home_red" class="home_red home">
    <div id="meeple_red_1" class="meeple red n1"></div>
    <div id="meeple_red_2" class="meeple red n2"></div>
</div>
```

**Example CSS:**
```css
.meeple {
    width: 32px;
    height: 39px;
    background-image: url(img/78_64_stand_meeples.png);
    background-size: 352px;
}

.meeple.red {
    background-position: 30% 0%;
}
```

**Important notes:**
- Straightforward mapping between server ID and JS ID (1:1)
- Place objects in different zones and use CSS for layout
- If you need temporary objects that look like originals, use dojo.clone
- For repetition or zone grids, use template generators with CSS instead of inline styles
- **Cannot use premade JS components (Stock, Zone) with this approach**
- Use alternative animation methods (default method leaves inline style attributes)

**Use player color in template:**
```php
function build_page($viewArgs) {
    $players = $this->game->loadPlayersBasicInfos();
    $cplayer = $this->getCurrentPlayerId();
    if (array_key_exists($cplayer, $players)) {
        $player_color = $players[$cplayer]['player_color'];
    } else {
        $player_color = 'ffffff'; // spectator
    }
    $this->tpl['PCOLOR'] = $player_color;
}
```

**Animation**

**Attach to new parent without destroying:**
```javascript
attachToNewParentNoDestroy: function (mobile_in, new_parent_in, relation, place_position) {
    const mobile = $(mobile_in);
    const new_parent = $(new_parent_in);
    var src = dojo.position(mobile);
    if (place_position)
        mobile.style.position = place_position;
    dojo.place(mobile, new_parent, relation);
    mobile.offsetTop; // force re-flow
    var tgt = dojo.position(mobile);
    var box = dojo.marginBox(mobile);
    var cbox = dojo.contentBox(mobile);
    var left = box.l + src.x - tgt.x;
    var top = box.t + src.y - tgt.y;
    mobile.style.position = "absolute";
    mobile.style.left = left + "px";
    mobile.style.top = top + "px";
    box.l += box.w - cbox.w;
    box.t += box.h - cbox.h;
    mobile.offsetTop; // force re-flow
    return box;
}
```

### BGA Studio Guidelines

These UX/UI guidelines ensure your game meets BGA quality standards. Validate UX before switching from ALPHA → BETA → RELEASE.

#### Layouts

**Layout arrangement**
- Game should fit square ratio and show everything active player needs
- Use vertical scroll for secondary info (other players' progress, secondary boards)
- Center play area on all devices
- Leave "no action" margin around board (deselect, scroll on mobile)
- Use HTML anchors to jump between distant sections
- Use spacers/transparent whiteblocks to group pieces clearly
- Keep score, turn order, and objectives accessible (button/tab/panel), not always visible
- Tuck rare abilities into tooltips

**Don't:**
- Hide game components behind popups (you should see everything you'd see on a real table)
- Place "always accessible" info permanently on player panels
- Add in-game logos or branding not part of the actual game
- Scatter related info (e.g., resources) across three corners

**Layout mantra:** Central = shared actions. Top/Bottom = global info. Panels = private resources.

#### Action Bar

The Action Bar always shows current state: turn in progress, who we're waiting for, or what the player can do.

**Do:**
- Center main awaited actions (Play card, End turn, Confirm move)
- Place secondary/greyed-out actions next to them
- Put cancel/undo/remove on the right, visually separated from forward actions
- Use Action Bar for: actions targeting another player, Pass/End turn/time-related actions, auction phases, small resource exchanges without dedicated board space
- Keep it to max 4 buttons + context so it doesn't overflow on mobile

**Don't:**
- Replace board-component actions with Action Bar buttons (players should act on the board like in real life)
- Stick custom buttons next to BGA's built-in buttons (replay controls, etc.)
- Let cancel actions visually compete with main actions
- Show "Round in progress" text inside the bar (display on table or as flavor text of current action)

**Example:** Wingspan shows current round as flavor text under the action bar.

#### Player Panels

Player panels let anyone glance at: who's playing, color, score, turn order, and resources gained.

**Do:**
- Keep panels compact (4-player game on mobile must not occupy more than ¼ of screen)
- Offer HTML anchor shortcuts to jump to a player's main components

**Don't:**
- Put settings, titles, round numbers, or other redundant info in panels
- Put always-accessible info (score, objectives) only on player panels

#### Popups

**Do:**
- Reserve automatic popups for tutorials only
- Make any required popup skippable on click/touch/timer
- Use game wiki for rules, hints, scoring tips, helpers

**Don't:**
- Use popups for anything mandatory
- Show popups every turn (unless skippable)
- Force players to read text before playing (except tutorials)

#### Colors and Contrast

**Do:**
- Use player colors consistently (not just for pieces but also for UI elements)
- Ensure text is readable on all backgrounds
- Consider colorblind accessibility (use patterns, symbols, or colorblind-safe palettes)
- Use meaningful color associations (red = danger, green = success, etc.)

**Don't**
- Rely on color alone to convey critical information
- Use low-contrast combinations
- Use red/green together without additional distinction

#### Typography

**Do:**
- Use BGA's default fonts for consistency
- Keep text readable at minimum sizes
- Use text hierarchy (headings, body, captions)
- Consider line length for readability

**Don't:**
- Use decorative fonts that are hard to read
- Make text too small or too large
- Use all caps for body text

#### Tooltips

**Do:**
- Use tooltips for rare or complex information
- Keep tooltips concise and helpful
- Ensure tooltips don't cover game elements
- Make tooltips disappear on mouse out or touch elsewhere

**Don't:**
- Put critical information only in tooltips
- Make tooltips so long they're hard to read
- Show tooltips for obvious elements

### Game Options and Preferences

#### Understanding Options vs Preferences

**Game Options:**
- Something usually in the rule book defined as "variant" (except player count, which is automatic)
- Examples: Whether to include The River in Carcassonne, expansions, special rules
- Selected by table creator
- Affects all players equally

**User Preferences:**
- Personal choices of each player only visible to that specific player
- Examples: Layout, whether to prompt for action, auto-opt in some actions
- Individual player settings

#### Game Options Format

**gameoptions.json structure:**
```json
{
    "100": { "name": "Game Setup", ... },
    "101": { "name": "Draft", ... }
}
```

Each key corresponds to option ID (must be string type in JSON).

**Access options in PHP:**
```php
$value = $this->tableOptions->get(100);
```

**Access options metadata:**
```php
$game_options = $this->getTableOptions();
```

**Note:** Options display in JSON order, not sorted by ID or name.

#### Option Definition Properties

**name** (mandatory)
- Name visible to table creator
- Automatically marked for translation

**values** (mandatory)
- Map of possible values
- Key is numeric value (as string in JSON)
- Value is object describing the value

**Value properties:**
- **name** (mandatory): String representation visible to table creator, auto-translated
- **description**: String description when name isn't self-explanatory, displayed under option in table
- **tmdisplay**: String representation in table description in lobby (useful for On/Off variants, pre-game communication)
- **nobeginner**: Set to true if not recommended for beginners
- **firstgameonly**: Set to true if recommended only for first game (discovery option)
- **beta**: Set to true if option is in beta development stage (warning for players)
- **alpha**: Set to true if option is in alpha development stage (warning, training mode only except developer)
- **premium**: Option only usable by premium members

**default** (optional)
- Default value if not present (first value listed is default)

**displaycondition** (array of conditions)
- Checks conditions before displaying option for selection
- All (or any) conditions must be true depending on displayconditionoperand

**displayconditionoperand**
- 'and' (default) or 'or'
- Changes behavior to display if one condition is true instead of all

**startcondition** (map from value to conditions array)
- Checks conditions on option VALUES before starting game
- All conditions must be true or players get red error message when attempting to begin

### PlayerCounter and TableCounter

These components display dynamic counters for player and table values.

#### PlayerCounter

**Purpose:** Display dynamic values associated with players (score, resources, etc.)

**Implementation:**
```javascript
this.playerCounter = new ebg.playercounter();
this.playerCounter.create('player_panel');
this.playerCounter.setValue(playerId, value);
```

#### TableCounter

**Purpose:** Display dynamic table-wide values (turn number, round, etc.)

**Implementation:**
```javascript
this.tableCounter = new ebg.counter();
this.tableCounter.create('table_info');
this.tableCounter.setValue(value);
```

### Best Practices for UI Enhancements

#### Performance

- **Minimize reflows** - Batch DOM updates when possible
- **Use CSS animations** - Prefer CSS over JavaScript animations
- **Debounce events** - Prevent rapid-fire updates
- **Lazy load complex UI** - Initialize only when needed

#### User Experience

- **Provide clear feedback** - Visual cues for all actions
- **Use consistent patterns** - Similar actions should behave similarly
- **Handle edge cases** - What happens with extreme values?
- **Test with different players** - Consider various player counts and settings

#### Accessibility

- **Keyboard navigation** - Support keyboard shortcuts where possible
- **Screen reader support** - Use ARIA labels where appropriate
- **Colorblind accessibility** - Don't rely on color alone
- **Touch targets** - Make buttons large enough for mobile (minimum 44x44px)

#### Code Organization

- **Separate concerns** - Keep logic, presentation, and behavior separate
- **Use meaningful names** - Class and function names should be descriptive
- **Comment complex logic** - Explain non-obvious implementations
- **Follow conventions** - Stick to BGA and framework patterns

---

## Summary

Phase 6 has covered UI enhancements and interactivity:

**Key Topics:**
- BGA Studio Cookbook recipes for common UI patterns
- BGA Studio Guidelines for UX/UI best practices
- Game options and preferences configuration
- PlayerCounter and TableCounter components
- Animation and visual effects
- Layout principles and responsive design

**Next Steps:**
With UI enhancements covered, you're ready for Phase 7, which covers advanced features and testing - implementing complex game mechanics and ensuring quality through testing.
