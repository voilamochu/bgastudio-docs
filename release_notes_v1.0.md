# Release Notes v1.0

## BGA Studio Developer Handbook - Version 1.0

**Release Date:** July 6, 2026

## Overview

Version 1.0 represents the initial consolidated release of the BGA Studio Developer Handbook. This release combines official Board Game Arena documentation into a structured, version-controlled format suitable for both human developers and AI coding assistants.

## Changes Included

### CRITICAL Fixes (from audit)

- **BgaCards API correction** - Completely rewrote BgaCards usage documentation to reflect the correct Manager/Stock pattern with BgaAnimations dependency requirement
- **BgaCards import methods** - Added both `importEsmLib` and legacy `importDojoLibs` patterns

### HIGH Priority Changes

- **State 1 restriction** - Added warning that state ID 1 is reserved for first game state
- **initialPrivate class syntax** - Added `initialPrivate: PlaceCard::class` alternative syntax
- **Magic parameters documentation** - Added comprehensive documentation for `getArgs()` and `act*` methods
- **Private data (_private)** - Added `_private` and `_merge_private` documentation
- **_no_notify flag** - Added skipped states optimization documentation

### MEDIUM Priority Changes

- **Dojo clarification** - Clarified that the modern framework still uses Dojo libraries internally
- **giveExtraTime()** - Referenced in pre-release checklist
- **upgradeTableDb()** - Documented for post-release migrations
- **initTable()** - Documented timing caveats (called for all PHP callbacks except arg* methods)

### Editorial Improvements

- Standardized heading hierarchy across all chapters
- Consistent terminology (ACTIVE_PLAYER, State Classes, etc.)
- Added clickable Table of Contents
- Added appendices (Glossary, Source Documentation, Abbreviations, Further Reading)
- Added version header and metadata

## Known Issues (Not Fixed)

The following issues from the audit were deferred for future versions:

- Missing `bgaFormatText` function documentation
- Notification decorator documentation
- PHPUnit stubs file structure detail
- `bgaPlayDojoAnimation` utility documentation
- Some cross-references to external documentation

## Technical Validation

- All code examples verified against source HTML documentation
- BgaCards API validated against official implementation
- State machine patterns confirmed against State classes documentation

## Next Steps

- Monitor official BGA documentation for framework updates
- Add TypeScript integration examples
- Expand bot implementation patterns
- Include more game-specific examples

## Credits

Documentation extracted from official BGA Studio documentation (https://en.doc.boardgamearena.com/) using automated tools.