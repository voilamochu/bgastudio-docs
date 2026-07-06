#!/usr/bin/env python3
"""
Build the BGA Studio Developer Handbook blueprint.

This script generates planning artifacts deterministically from the knowledge index:
- handbook_plan.json: Complete chapter definitions with metadata
- handbook_toc.md: Human-readable table of contents
- chapter_mapping.json: Mapping of documentation pages to chapters
- generation_order.json: Optimal order for generating handbook chapters

Run with: python build_handbook_plan.py
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

# Paths
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
OUTPUT_DIR = Path(__file__).parent


def load_json(filename: str) -> Any:
    """Load a JSON file from the knowledge directory."""
    with open(KNOWLEDGE_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_page_word_count(path: str, master_index: List[Dict]) -> int:
    """Get word count for a page from master index."""
    for item in master_index:
        if item['source_file'] == path:
            return item.get('word_count', 0)
    return 0


def get_page_headings(path: str, master_index: List[Dict]) -> List[Dict]:
    """Get headings for a page from master index."""
    for item in master_index:
        if item['source_file'] == path:
            return item.get('headings', [])
    return []


# Define the handbook chapters based on analysis of the documentation
HANDBOOK_CHAPTERS = [
    {
        "number": 1,
        "title": "Introduction to BGA Studio",
        "purpose": "Introduce Board Game Arena Studio, its purpose, and how to get started as a developer.",
        "learning_objectives": [
            "Understand what BGA Studio is and its role in the ecosystem",
            "Learn the requirements and prerequisites for BGA development",
            "Set up a development account and understand the licensing model",
            "Navigate the documentation and community resources"
        ],
        "prerequisite_chapters": [],
        "pages": [
            {"path": "Studio.html", "primary": True},
            {"path": "How_to_join_BGA_developer_team.html", "primary": True},
            {"path": "First_steps_with_BGA_Studio.html", "primary": True},
            {"path": "BGA_Game_licenses.html", "primary": True},
            {"path": "Contact_BGA_Studio.html", "primary": False}
        ]
    },
    {
        "number": 2,
        "title": "Development Environment Setup",
        "purpose": "Configure the local development environment for efficient BGA game development.",
        "learning_objectives": [
            "Install and configure VSCode for BGA development",
            "Set up file synchronization with the BGA Studio server",
            "Understand the project structure and file organization",
            "Configure code formatting and intellisense"
        ],
        "prerequisite_chapters": [1],
        "pages": [
            {"path": "Setting_up_BGA_Development_environment_using_VSCode.html", "primary": True},
            {"path": "Studio_file_reference.html", "primary": True},
            {"path": "Tools_and_tips_of_BGA_Studio.html", "primary": False}
        ]
    },
    {
        "number": 3,
        "title": "Game Project Fundamentals",
        "purpose": "Understand the core structure of a BGA game project and essential configuration files.",
        "learning_objectives": [
            "Create a new game project using the template",
            "Configure game metadata and player settings",
            "Understand the file structure and their purposes",
            "Set up version control for your project"
        ],
        "prerequisite_chapters": [2],
        "pages": [
            {"path": "Game_meta-information_gameinfos.jsonc.html", "primary": True},
            {"path": "Game_database_model_dbmodel.sql.html", "primary": True},
            {"path": "Game_material_description_material.inc.php.html", "primary": True},
            {"path": "Players_actions_yourgamename.action.php.html", "primary": True},
            {"path": "Game_layout_view_and_template_yourgamename.view.php_and_yourgamename_yourgamename.tpl.html", "primary": True}
        ]
    },
    {
        "number": 4,
        "title": "State Machine Architecture",
        "purpose": "Master the BGA state machine system for controlling game flow and turn-based logic.",
        "learning_objectives": [
            "Design and implement game states",
            "Control player activation and turn order",
            "Handle state transitions and transitions",
            "Understand client vs server states and private states"
        ],
        "prerequisite_chapters": [3],
        "pages": [
            {"path": "Your_game_state_machine_states.inc.php.html", "primary": True},
            {"path": "State_classes_State_directory.html", "primary": True},
            {"path": "BGA_Studio_Migration_Guide.html", "primary": False, "sections": ["States", "State Management Functions"]}
        ]
    },
    {
        "number": 5,
        "title": "Server-Side Game Logic (PHP)",
        "purpose": "Implement core game logic on the server side using PHP and the BGA framework.",
        "learning_objectives": [
            "Access and manipulate the database",
            "Handle player actions and game events",
            "Send notifications to clients",
            "Manage randomness and game statistics"
        ],
        "prerequisite_chapters": [4],
        "pages": [
            {"path": "Main_game_logic_Game.php.html", "primary": True},
            {"path": "BGA_Studio_Migration_Guide.html", "primary": False, "sections": ["PHP migration", "Autowire game actions", "Notifications", "State Management Functions", "Deprecated translation functions"]},
            {"path": "Game_statistics_stats.json.html", "primary": True}
        ]
    },
    {
        "number": 6,
        "title": "Client-Side Game Interface (JavaScript)",
        "purpose": "Build the interactive client-side game interface using JavaScript/TypeScript.",
        "learning_objectives": [
            "Set up the Game.js structure and framework components",
            "Handle player input and connect to server actions",
            "Process notifications and update the UI",
            "Work with the DOM and create interface elements"
        ],
        "prerequisite_chapters": [4, 5],
        "pages": [
            {"path": "Game_interface_logic_Game.js.html", "primary": True},
            {"path": "BGA_Studio_Migration_Guide.html", "primary": False, "sections": ["Main class", "Notification setup", "Status bar manipulation", "Dojo usage"]},
            {"path": "Using_Typescript_and_Scss.html", "primary": True}
        ]
    },
    {
        "number": 7,
        "title": "Game UI Components and Graphics",
        "purpose": "Create and manage visual components, layout, and game assets.",
        "learning_objectives": [
            "Use BGA UI components (Stock, Deck, Zone, Scrollmap)",
            "Manage game images and graphics assets",
            "Create responsive layouts for different screen sizes",
            "Handle animations and visual feedback"
        ],
        "prerequisite_chapters": [6],
        "pages": [
            {"path": "Stock.html", "primary": True},
            {"path": "Deck.html", "primary": True},
            {"path": "Zone.html", "primary": True},
            {"path": "Scrollmap.html", "primary": True},
            {"path": "Game_art_img_directory.html", "primary": True},
            {"path": "Game_interface_stylesheet_yourgamename.css.html", "primary": True},
            {"path": "Your_game_mobile_version.html", "primary": True}
        ]
    },
    {
        "number": 8,
        "title": "UI Enhancements and Interactivity",
        "purpose": "Enhance the user interface with advanced features and polish.",
        "learning_objectives": [
            "Implement tooltips, dialogs, and banners",
            "Add sound effects and image buttons",
            "Handle user preferences and customization",
            "Follow UI/UX best practices and guidelines"
        ],
        "prerequisite_chapters": [7],
        "pages": [
            {"path": "BGA_Studio_Cookbook.html", "primary": True, "sections": ["Visual Effects, Layout and Animation", "Game Model and Database design", "Images and Icons", "Dynamic tooltips"]},
            {"path": "BGA_Studio_Guidelines.html", "primary": True},
            {"path": "Options_and_preferences_gameoptions.json,_gamepreferences.json.html", "primary": True},
            {"path": "PlayerCounter_and_TableCounter.html", "primary": True}
        ]
    },
    {
        "number": 9,
        "title": "Notifications and Logging",
        "purpose": "Implement game notifications and understand the logging system.",
        "learning_objectives": [
            "Send properly formatted notifications to clients",
            "Handle notification args and decorators",
            "Format log messages for translation",
            "Understand BGA logging and error reporting"
        ],
        "prerequisite_chapters": [5, 6],
        "pages": [
            {"path": "BGA_Studio_Migration_Guide.html", "primary": False, "sections": ["Notification Decorators", "Notification args consistency"]}
        ]
    },
    {
        "number": 10,
        "title": "Internationalization and Localization",
        "purpose": "Implement multi-language support for your game.",
        "learning_objectives": [
            "Mark strings for translation in PHP and JavaScript",
            "Use clienttranslate and proper i18n formatting",
            "Handle gender-specific pronouns in translations",
            "Preview and test translations"
        ],
        "prerequisite_chapters": [5],
        "pages": [
            {"path": "Translations.html", "primary": True}
        ]
    },
    {
        "number": 11,
        "title": "Advanced Features",
        "purpose": "Implement advanced BGA features including bots, undo, and zombie mode.",
        "learning_objectives": [
            "Create AI bots for your game",
            "Implement undo functionality",
            "Handle disconnected players with zombie mode",
            "Use BGA helper libraries and utilities"
        ],
        "prerequisite_chapters": [4, 5, 6],
        "pages": [
            {"path": "Bots_and_Artificial_Intelligence.html", "primary": True},
            {"path": "BGA_Undo_policy.html", "primary": True},
            {"path": "Zombie_Mode.html", "primary": True},
            {"path": "BGA_Studio_Migration_Guide.html", "primary": False, "sections": ["Updated Zombie Mode documentation and recommendations"]},
            {"path": "BgaAnimations.html", "primary": True},
            {"path": "BgaAutofit.html", "primary": True},
            {"path": "BgaCards.html", "primary": True},
            {"path": "BgaDice.html", "primary": True},
            {"path": "BgaScoreSheet.html", "primary": True},
            {"path": "ExpandableSection.html", "primary": True},
            {"path": "Counter.html", "primary": True}
        ]
    },
    {
        "number": 12,
        "title": "Testing and Debugging",
        "purpose": "Establish testing practices and debug issues effectively.",
        "learning_objectives": [
            "Write unit tests for PHP and JavaScript",
            "Debug common runtime errors",
            "Use BGA Studio debugging tools",
            "Test with bots and playtesting"
        ],
        "prerequisite_chapters": [5, 6, 11],
        "pages": [
            {"path": "Testing_by_developer.html", "primary": True},
            {"path": "Practical_debugging.html", "primary": True},
            {"path": "Troubleshooting.html", "primary": True},
            {"path": "Studio_logs.html", "primary": True}
        ]
    },
    {
        "number": 13,
        "title": "Game Lifecycle and Publishing",
        "purpose": "Navigate the game development lifecycle from dev to release.",
        "learning_objectives": [
            "Understand the alpha/beta release process",
            "Handle post-release updates and database migrations",
            "Document changes and communicate with the community",
            "Avoid version mismatches and production issues"
        ],
        "prerequisite_chapters": [1, 12],
        "pages": [
            {"path": "Create_a_game_in_BGA_Studio_Complete_Walkthrough.html", "primary": True},
            {"path": "Post-release_phase.html", "primary": True},
            {"path": "Pre-release_checklist.html", "primary": True},
            {"path": "Tutorials_checklist.html", "primary": True}
        ]
    },
    {
        "number": 14,
        "title": "Reference and Migration Guide",
        "purpose": "Reference for migrating existing games and understanding framework changes.",
        "learning_objectives": [
            "Migrate from legacy BGA patterns to modern API",
            "Understand deprecated features and replacements",
            "Use the new this.bga.* API structure",
            "Update existing projects to current standards"
        ],
        "prerequisite_chapters": [1, 2, 5, 6],
        "pages": [
            {"path": "BGA_Studio_Migration_Guide.html", "primary": True}
        ]
    },
    {
        "number": 15,
        "title": "Appendix: Additional Resources and Tutorials",
        "purpose": "Supplementary materials including tutorials, community resources, and reference documentation.",
        "learning_objectives": [
            "Understand additional tools like ChromeExtension",
            "Reference game asset formats and requirements",
            "Find answers to common questions in the FAQ",
            "Learn from complete tutorial implementations"
        ],
        "prerequisite_chapters": [],
        "pages": [
            {"path": "Anti-Stock.html", "primary": False, "reason": "Stock alternative pattern"},
            {"path": "BGA_Code_Sharing.html", "primary": False, "reason": "Community resources"},
            {"path": "BGA_game_Lifecycle.html", "primary": False, "reason": "Lifecycle overview"},
            {"path": "ChromeExtension.html", "primary": False, "reason": "Development tool"},
            {"path": "Common_board_game_elements_image_resources.html", "primary": False, "reason": "Asset reference"},
            {"path": "Compatibility.html", "primary": False, "reason": "Technical requirements"},
            {"path": "Draggable.html", "primary": False, "reason": "Deprecated component reference"},
            {"path": "Game_fonts_fonts_directory.html", "primary": False, "reason": "Font asset handling"},
            {"path": "Game_metadata_manager.html", "primary": False, "reason": "Game metadata API"},
            {"path": "Game_replay.html", "primary": False, "reason": "Replay feature"},
            {"path": "Game_sounds_sounds_directory.html", "primary": False, "reason": "Sound assets"},
            {"path": "I_wish_I_knew_this_when_I_started.html", "primary": False, "reason": "Developer tips"},
            {"path": "Studio_FAQ.html", "primary": False, "reason": "FAQ reference"},
            {"path": "Tutorial_hearts.html", "primary": False, "reason": "Tutorial reference"},
            {"path": "Tutorial_reversi.html", "primary": False, "reason": "Tutorial reference"},
            {"path": "Using_AI_for_BGA_game_development.html", "primary": False, "reason": "AI development tools"},
            {"path": "Using_Vue.html", "primary": False, "reason": "Vue framework integration"}
        ]
    }
]


def calculate_chapter_metrics(chapter: Dict, master_index: List[Dict]) -> Dict:
    """Calculate reading time and complexity for a chapter."""
    total_words = 0
    code_blocks = 0
    
    for page in chapter.get('pages', []):
        page_info = next((item for item in master_index if item['source_file'] == page['path']), None)
        if page_info:
            total_words += page_info.get('word_count', 0)
            # Adjust for sections if specified
            if page.get('sections'):
                # Estimate based on full page for now
                code_blocks += page_info.get('code_block_count', 0) // 2
            else:
                code_blocks += page_info.get('code_block_count', 0)
    
    # Reading time: ~200 words per minute for technical content
    reading_time = max(5, total_words // 200)
    
    # Complexity: based on code blocks and word count
    if code_blocks > 30 or total_words > 5000:
        complexity = "High"
    elif code_blocks > 10 or total_words > 2000:
        complexity = "Medium"
    else:
        complexity = "Low"
    
    return {
        "reading_time_minutes": reading_time,
        "estimated_complexity": complexity
    }


def extract_glossary_terms(chapter: Dict, glossary: List[Dict]) -> List[str]:
    """Extract glossary terms relevant to this chapter."""
    terms = []
    for page in chapter.get('pages', []):
        path = page['path']
        for entry in glossary:
            for page_ref in entry.get('pages', []):
                if page_ref['path'] == path:
                    term = entry['term']
                    if term not in terms:
                        terms.append(term)
    return sorted(terms)[:20]  # Limit to 20 terms per chapter


def generate_handbook_plan(master_index: List[Dict], glossary: List[Dict]) -> Dict:
    """Generate the complete handbook plan with all metadata."""
    plan = []
    
    for chapter in HANDBOOK_CHAPTERS:
        metrics = calculate_chapter_metrics(chapter, master_index)
        terms = extract_glossary_terms(chapter, glossary)
        
        # Calculate total word count
        total_words = sum(
            next((item.get('word_count', 0) for item in master_index if item['source_file'] == p['path']), 0)
            for p in chapter.get('pages', [])
        )
        
        chapter_entry = {
            "number": chapter['number'],
            "title": chapter['title'],
            "purpose": chapter['purpose'],
            "learning_objectives": chapter['learning_objectives'],
            "prerequisite_chapters": chapter['prerequisite_chapters'],
            "glossary_terms_introduced": terms,
            "estimated_reading_time_minutes": metrics['reading_time_minutes'],
            "estimated_implementation_complexity": metrics['estimated_complexity'],
            "total_word_count": total_words,
            "pages": chapter['pages']
        }
        plan.append(chapter_entry)
    
    return plan


def generate_toc(plan: List[Dict]) -> str:
    """Generate markdown table of contents."""
    lines = ["# BGA Studio Developer Handbook\n", ""]
    lines.append("## Table of Contents\n")
    lines.append("")
    
    for chapter in plan:
        lines.append(f"{chapter['number']}. [{chapter['title']}](#chapter-{chapter['number']})")
        lines.append("")
    
    lines.append("\n---\n")
    lines.append("\n*Total chapters: {}*\n".format(len(plan)))
    
    return "\n".join(lines)


def generate_chapter_mapping(master_index: List[Dict]) -> Dict:
    """Generate mapping of documentation pages to chapters."""
    # Build set of all covered pages
    covered_pages = set()
    for chapter in HANDBOOK_CHAPTERS:
        for page in chapter.get('pages', []):
            path = page['path']
            if path not in covered_pages:
                covered_pages.add(path)
    
    mapping = {
        "page_to_chapters": {},
        "orphan_pages": [],
        "validation": {
            "total_pages_in_index": len(master_index),
            "covered_pages": len(covered_pages),
            "missing_pages": []
        }
    }
    
    # Map each page to its chapters
    for chapter in HANDBOOK_CHAPTERS:
        for page in chapter.get('pages', []):
            path = page['path']
            assignment = {"chapter": chapter['number'], "primary": page.get('primary', False)}
            if page.get('sections'):
                assignment['sections'] = page['sections']
            if page.get('reason'):
                assignment['reason'] = page['reason']
            
            if path not in mapping['page_to_chapters']:
                mapping['page_to_chapters'][path] = []
            mapping['page_to_chapters'][path].append(assignment)
    
    # Find orphan pages
    for item in master_index:
        path = item['source_file']
        if path not in covered_pages:
            mapping['orphan_pages'].append({
                "path": path,
                "title": item['title'],
                "word_count": item.get('word_count', 0)
            })
    
    # Check for missing pages in mapping
    for item in master_index:
        if item['source_file'] not in mapping['page_to_chapters']:
            mapping['validation']['missing_pages'].append(item['source_file'])
    
    return mapping


def generate_generation_order(plan: List[Dict]) -> Dict:
    """Generate optimal order for chapter generation."""
    # Chapters are already in order, but we can add dependency tracking
    order = {
        "generation_order": [c['number'] for c in plan],
        "dependency_graph": {},
        "complexity_tier": {
            "foundational": [],
            "implementation": [],
            "advanced_features": [],
            "reference": []
        }
    }
    
    for chapter in plan:
        num = chapter['number']
        prereqs = chapter['prerequisite_chapters']
        
        order['dependency_graph'][str(num)] = {
            "requires": prereqs,
            "complexity": chapter['estimated_implementation_complexity'],
            "reading_time": chapter['estimated_reading_time_minutes']
        }
        
        tier = "foundational" if num <= 4 else ("implementation" if num <= 8 else ("advanced_features" if num <= 12 else "reference"))
        order['complexity_tier'][tier].append(num)
    
    return order


def main():
    """Main entry point."""
    # Load knowledge files
    master_index = load_json('master_index.json')
    glossary = load_json('glossary.json')
    
    # Generate outputs
    plan = generate_handbook_plan(master_index, glossary)
    toc = generate_toc(plan)
    mapping = generate_chapter_mapping(master_index)
    gen_order = generate_generation_order(plan)
    
    # Write outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_DIR / 'handbook_plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2)
    
    with open(OUTPUT_DIR / 'handbook_toc.md', 'w', encoding='utf-8') as f:
        f.write(toc)
    
    with open(OUTPUT_DIR / 'chapter_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    
    with open(OUTPUT_DIR / 'generation_order.json', 'w', encoding='utf-8') as f:
        json.dump(gen_order, f, indent=2)
    
    # Print summary
    print(f"Generated handbook blueprint:")
    print(f"  - {len(plan)} chapters")
    print(f"  - {len(mapping['orphan_pages'])} orphan pages")
    if mapping['orphan_pages']:
        print("  Orphan pages:")
        for orphan in mapping['orphan_pages']:
            print(f"    - {orphan['title']}")


if __name__ == '__main__':
    main()