# BGA Studio Developer Handbook

This directory contains the planning artifacts for the Board Game Arena (BGA) Studio Developer Handbook.

## Overview

The handbook is organized into 15 chapters designed to teach BGA Studio development from beginner to advanced levels, suitable for:
- New BGA Studio developers
- Experienced developers
- AI coding assistants
- Future migration projects

## Generated Files

| File | Description |
|------|-------------|
| `handbook_plan.json` | Complete chapter definitions with metadata including purpose, learning objectives, prerequisites, and page assignments |
| `handbook_toc.md` | Human-readable table of contents in Markdown format |
| `chapter_mapping.json` | Mapping of each documentation page to its assigned chapter(s) |
| `generation_order.json` | Optimal order for generating handbook chapters with dependency information |

## Chapter Structure

The handbook follows a logical progression:

1. **Introduction to BGA Studio** (Low complexity) - Get started with BGA development
2. **Development Environment Setup** (Medium) - Configure your local environment
3. **Game Project Fundamentals** (High) - Core project structure and configuration
4. **State Machine Architecture** (High) - Game flow control system
5. **Server-Side Game Logic (PHP)** (High) - Backend implementation
6. **Client-Side Game Interface (JavaScript)** (High) - Frontend implementation
7. **Game UI Components and Graphics** (High) - Visual elements and assets
8. **UI Enhancements and Interactivity** (High) - Polish and advanced UI
9. **Notifications and Logging** (Low) - Communication between client/server
10. **Internationalization and Localization** (Medium) - Multi-language support
11. **Advanced Features** (High) - Bots, undo, zombie mode
12. **Testing and Debugging** (High) - Quality assurance practices
13. **Game Lifecycle and Publishing** (Medium) - From dev to release
14. **Reference and Migration Guide** (Medium) - Framework migration and reference
15. **Appendix: Additional Resources** (Varies) - Supplementary materials

## Complexity Tiers

- **Foundational** (Chapters 1-4): Core concepts every developer must understand
- **Implementation** (Chapters 5-8): Backend and frontend implementation details
- **Advanced Features** (Chapters 9-12): Specialized features and quality assurance
- **Reference** (Chapters 13-15): Lifecycle, migration guide, and appendix

## Usage

Run the generator script:
```bash
python build_handbook_plan.py
```

The script reads from `knowledge/` directory and produces all planning artifacts deterministically.

## Validation

The generated files validate that:
- Every documentation page is assigned to at least one chapter
- No duplicate chapter assignments (except for supporting sections)
- No empty chapters
- Logical progression from beginner to advanced concepts