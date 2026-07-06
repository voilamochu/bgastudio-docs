# BGA Studio Developer Handbook - Phase 5: UI Components and Graphics

## Chapter 7: Game UI Components and Graphics

### Overview

This chapter covers the visual components and graphics system used to build the game interface. BGA provides several pre-built components for common game elements, along with guidelines for managing game assets and creating responsive layouts.

### Important Note: Modern Card Component

**A new library for cards has been added to the framework: BgaCards. We recommend using it instead of Stock for card-based games.**

BgaCards provides a more modern, feature-rich alternative to the Stock component specifically designed for card games.

### Stock Component

Stock is a JavaScript component for displaying sets of elements of the same size arranged in single or multiple lines.

#### Stock Use Cases

- Display card hands (Hearts, Seasons, The Boss, Race for the Galaxy)
- Display items in player panels (Takenoko, Amyitis)
- Many other situations (e.g., black dice and cubes on cards in Troyes)

#### Stock Benefits

- Items arranged nicely and sorted by type
- Smooth animations when adding/removing items
- Built-in selection and unselection functions
- No need to manage HTML manually - component handles entire lifecycle

#### Simple Stock Example (Hearts)

**Import the library:**
```javascript
const [stock] = await importDojoLibs(['ebg/stock']);
```

**Initialize in setup method:**
```javascript
// Player hand
this.playerHand = new ebg.stock();
this.playerHand.create(this.bga.gameui, $('myhand'), this.cardwidth, this.cardheight);
```

**Define card types using CSS sprite:**
```javascript
// Specify 13 images per row in CSS sprite
this.playerHand.image_items_per_row = 13;

// Create card types
for(var color=1; color<=4; color++) {
    for(var value=2; value<=14; value++) {
        var card_type_id = this.getCardUniqueId(color, value);
        this.playerHand.addItemType(card_type_id, card_type_id, 
            this.bga.images.getImgUrl('cards.jpg'), card_type_id);
    }
}
```

**Add cards to stock:**
```javascript
this.playerHand.addToStock(this.getCardUniqueId(2 /* hearts */, 5));
```

**Add cards with IDs:**
```javascript
this.playerHand.addToStockWithId(this.getCardUniqueId(2, 5), my_card_id);
```

**Remove cards:**
```javascript
this.playerHand.removeFromStockById(my_card_id);
```

#### Stock Creation Parameters

**create(page, container_div, item_width, item_height)**
- `page`: Container page (usually `this.bga.gameui`)
- `container_div`: Container div element (not an ID - use $(id) if you have ID)
- `item_width`: Width of items in pixels
- `item_height`: Height of items in pixels

### Deck Component (Server-Side)

Deck is one of the most useful PHP components for managing cards in your game.

#### Deck Capabilities

- Place cards in a pile, shuffle cards, draw cards one by one or many at a time
- Auto-reshuffle discard pile into deck when deck is empty
- Move cards between different locations (hands, table, etc.)

#### Card Properties

Each card has 5 properties:

**id**
- Unique ID of each card

**type and type_arg**
- Define the type of card (what sort of card is this?)
- Used as you like to identify different cards in your game

**location and location_arg**
- Define where the card is currently located
- `location`: Short string
- `location_arg`: Integer

**Examples of type/type_arg usage:**
- Hearts: `type` = color (1-4), `type_arg` = value (1-10, J, Q, K)
- Seasons: `type` = card type (Amulet of Air, Fire, etc.), `type_arg` not used
- Takenoko: `type` = objective kind (irrigation/panda/plot), `type_arg` = specific objective ID

#### Special Locations

Deck manages these locations automatically:

**'deck'**
- Standard draw deck
- Cards face down in stack
- Drawn in sequential order
- `location_arg` specifies position in stack (highest = next to draw)

**'hand'**
- Cards in player's hand
- `location_arg` = player ID

**'discard'**
- Discard pile
- May be reshuffled into deck if needed (autoreshuffle)

#### Creating a Deck Component

**Database table:**
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

**Note:** Schema can be modified (increase field sizes, add more fields). Additional fields require manual queries.

**Declare in PHP constructor:**
```php
$this->cards = $this->deckFactory->createDeck('card');
```

**Multiple decks:**
```php
$this->firstKindCards = $this->deckFactory->createDeck("first_kind_card");
$this->secondKindCards = $this->deckFactory->createDeck("second_kind_card");
```

**Note:** Most games need only one Deck component managing all objects of the same kind. Each Deck needs its own table with fields `card_id`, `card_type`, etc.

#### Initializing Cards

Deck provides fast initialization with `createCards`:
```php
// Create cards for a standard 52-card deck
$cards = [];
for($color=1; $color<=4; $color++) {
    for($value=2; $value<=14; $value++) {
        $cards[] = ['type' => $color, 'type_arg' => $value];
    }
}
$this->cards->createCards($cards, 'deck');
```

#### Common Deck Operations

**Shuffle:**
```php
$this->cards->shuffle('deck');
```

**Draw cards:**
```php
$card = $this->cards->drawCard('deck');
```

**Draw multiple cards:**
```php
$cards = $this->cards->drawCards('deck', 5);
```

**Move card:**
```php
$this->cards->moveCard($card_id, 'hand', $player_id);
```

**Get cards in location:**
```php
$handCards = $this->cards->getCardsInLocation('hand', $player_id);
```

### Zone Component

Zone organizes items of the same type inside a predefined space.

#### Zone in Action

See "Can't Stop" or "Niagara" on BGA to see Zone in action. In Niagara, it displays canoes over circles going down the river (custom mode).

#### Using Zone

**Import library:**
```javascript
const [zone] = await importDojoLibs(['ebg/zone']);
```

**Declare Zone object:**
```javascript
constructor() {
    this.myZone = new ebg.zone();
}
```

**Add div in template:**
```html
<div id="my_zone"></div>
```

**Set CSS:**
```css
#my_zone {
    width: 100px;
}
```

**Create Zone in setup:**
```javascript
zone.create(this.bga.gameui, 'my_zone', <item_width>, <item_height>);
zone.setPattern(<mode>);
```

**Parameters:**
- `item_width`: Width of objects to organize
- `item_height`: Height of objects to organize
- `mode`: 'grid', 'diagonal', or 'custom'

**Patterns:**
- `grid`: Items in lines from top-left to bottom-right, wrapping when no space
- `diagonal`: Items on diagonal from top-left to bottom-right, overlapping
- `custom`: Organized based on coordinates you provide

**Note:** Zone width is static - beware of overflow on small screens. For responsive design, consider Stock instead.

#### Zone Operations

**Place item in zone:**
```javascript
zone.placeInZone(<object_id>, <weight>);
```

**Remove item:**
```javascript
zone.removeFromZone(<object_id>, <destroy?>, <to>);
```

**Other operations:**
- `zone.removeAll()` - Remove and destroy all items
- `zone.getItemNumber()` - Get number of items
- `zone.getAllItems()` - Get array of item IDs

### Scrollmap Component

Scrollmap is used for game boards that are larger than the visible area, allowing players to scroll around the board.

#### Scrollmap Use Cases

- Large game boards that don't fit on screen
- Maps with multiple regions
- Games with zoomed-in views

#### Implementation

**Import library:**
```javascript
const [scrollmap] = await importDojoLibs(['ebg/scrollmap']);
```

**Create Scrollmap:**
```javascript
this.scrollmap = new ebg.scrollmap();
this.scrollmap.create(this.bga.gameui, 'board_area', width, height);
```

**Use container div:**
```html
<div id="board_area"></div>
```

### Game Art and Images

#### Image Directory Structure

Game images are stored in the `img/` directory. Common image types:
- Card sprites
- Board backgrounds
- Token images
- Player avatars
- UI elements

#### Image Guidelines

- Use optimized images for web performance
- Prefer CSS sprites for multiple small images
- Use appropriate formats (PNG for transparency, JPG for photos)
- Consider responsive image loading

#### Image Access

**In JavaScript:**
```javascript
this.bga.images.getImgUrl('myimage.jpg');
```

**In CSS:**
```css
background-image: url(img/myimage.jpg);
```

### Game Interface Stylesheet

#### CSS File Structure

The game stylesheet (`yourgamename.css`) contains all custom styles for your game.

#### Common CSS Patterns

**Game area:**
```css
#game_area {
    background-image: url(img/board.jpg);
    background-repeat: no-repeat;
    background-position: center;
}
```

**Player panels:**
```css
.player_panel {
    border: 2px solid #000;
    border-radius: 5px;
}
```

**Card styles:**
```css
.card {
    width: 60px;
    height: 90px;
    border-radius: 5px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
}
```

### Mobile Version Support

#### Mobile Considerations

- Games must work on mobile devices
- Touch interfaces require larger touch targets
- Screen real estate is limited
- Performance is more critical

#### Mobile Best Practices

- Use larger buttons (minimum 44x44 pixels)
- Simplify complex UI for mobile
- Test on actual mobile devices
- Consider landscape vs portrait orientations

#### Mobile-Specific CSS

```css
@media (max-width: 768px) {
    /* Mobile-specific styles */
    .card {
        width: 50px;
        height: 75px;
    }
}
```

### BgaCards Component (Recommended for Card Games)

#### Why Use BgaCards

BgaCards is the modern replacement for Stock specifically designed for card games, offering:
- Better performance
- More features
- Easier API
- Better TypeScript support

#### Basic BgaCards Usage

**Import:**
```javascript
const [BgaCards] = await importDojoLibs(['bga-cards']);
```

**Create:**
```javascript
this.cards = new BgaCards(this.bga.gameui, 'card_container', {
    width: 60,
    height: 90,
    gap: 5
});
```

**Add card:**
```javascript
this.cards.addCard(cardId, cardType, imageUrl);
```

**Remove card:**
```javascript
this.cards.removeCard(cardId);
```

### Best Practices for UI Components

#### Performance

- **Minimize DOM operations** - Use component methods instead of direct DOM manipulation
- **Use CSS sprites** - Reduce HTTP requests for multiple small images
- **Optimize images** - Compress and optimize file sizes
- **Lazy load** - Load images only when needed

#### User Experience

- **Provide visual feedback** - Show hover states, selection indicators
- **Use animations sparingly** - Enhance but don't distract
- **Ensure accessibility** - Consider colorblind players
- **Test on different devices** - Desktop, tablet, mobile

#### Code Organization

- **Group related styles** - Organize CSS logically
- **Use consistent naming** - Follow naming conventions
- **Comment complex sections** - Explain non-obvious CSS
- **Separate concerns** - Keep structure, presentation, behavior separate

---

## Summary

Phase 5 has covered UI components and graphics for BGA games:

**Key Components:**
- Stock component for displaying item collections
- Deck component for server-side card management
- Zone component for organizing items in predefined spaces
- Scrollmap for large game boards
- BgaCards as modern alternative to Stock for card games

**Graphics and Assets:**
- Image directory structure and management
- CSS styling for game interface
- Mobile version support and responsive design
- Image optimization and performance considerations

**Next Steps:**
With UI components and graphics covered, you're ready for Phase 6, which covers UI enhancements and interactivity - adding polish and advanced features to your game interface.
