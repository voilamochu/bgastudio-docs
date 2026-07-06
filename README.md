# BGA Studio Developer Handbook

**Version 1.0** | Documentation for Board Game Arena game development

## Purpose

This handbook provides a comprehensive guide for developing board game adaptations on the Board Game Arena (BGA) Studio platform. It consolidates and organizes the official BGA documentation into a structured learning path covering all phases of game development.

## Target Audience

- **Beginner developers** starting their first BGA project
- **Experienced developers** migrating legacy projects to modern framework
- **AI coding assistants** generating BGA-compatible code

## How the Handbook Was Generated

This handbook was created through automated extraction and consolidation of official BGA Studio documentation from https://en.doc.boardgamearena.com. Source HTML files are available in the `source-html/` directory.

## Scope

### Covered Topics
- Project setup and development environment
- State machine architecture (State Classes)
- Server-side PHP game logic
- Client-side JavaScript interface
- UI components (Stock, BgaCards, Zone, Scrollmap)
- Internationalization and translations
- Bot implementation
- Testing strategies
- Publishing workflow

### Known Limitations
- Some implementation examples may require adaptation based on specific game needs
- The BGA framework evolves; always verify against latest official documentation
- Bot implementation is custom per-game (no framework support)
- Advanced TypeScript integration requires separate type definition downloads

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-07-06 | Initial release - consolidated official BGA documentation |

## Quick Start

1. Read Chapter 1 to understand BGA Studio fundamentals
2. Review Chapter 4 for state machine architecture
3. Study Chapter 7 for UI components and BgaCards usage
4. Follow the Pre-release checklist in Chapter 13 before publishing

## File Structure

```
bgastudio-docs/
├── Developer_Handbook_v1.md      # Consolidated handbook
├── README.md                     # This file
├── release_notes_v1.0.md         # Release notes
├── handbook_content/             # Individual phase markdown files
│   ├── phase-1-foundation-and-setup.md
│   ├── phase-2-state-machine-architecture.md
│   ├── ...
│   └── phase-8-publishing-reference-and-resources.md
├── source-html/                  # Downloaded source documentation
└── scripts/                     # Generation and download scripts
```

## Contributing

This is an unofficial documentation consolidation. For contributions to official BGA documentation, visit https://en.doc.boardgamearena.com/

## License

This handbook mirrors official BGA documentation and follows the same licensing terms. BGA Studio documentation is provided for use with the BGA platform.