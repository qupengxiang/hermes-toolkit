# src/core/skills.py
"""
Skills management for Hermes Toolkit.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class SkillEntry:
    """Represents a single Skill."""

    def __init__(self, name: str, category: str = 'default', **kwargs):
        self.name = name
        self.category = category
        self.title = kwargs.get('title', name)
        self.description = kwargs.get('description', '')
        self.tags = kwargs.get('tags', [])
        self.author = kwargs.get('author', '')
        self.version = kwargs.get('version', '1.0.0')
        self.content = kwargs.get('content', '')
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'author': self.author,
            'version': self.version,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_file(cls, file_path: Path) -> Optional['SkillEntry']:
        """Load a skill from a markdown file with YAML frontmatter."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter
            frontmatter = {}
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2].strip()
                    except yaml.YAMLError:
                        body = content

            name = file_path.stem
            category = file_path.parent.name if file_path.parent.name != 'skills' else 'default'

            return cls(
                name=name,
                category=frontmatter.get('category', category),
                title=frontmatter.get('title', name),
                description=frontmatter.get('description', ''),
                tags=frontmatter.get('tags', []),
                author=frontmatter.get('author', ''),
                version=frontmatter.get('version', '1.0.0'),
                content=body,
                created_at=frontmatter.get('created_at', ''),
                updated_at=frontmatter.get('updated_at', datetime.now().isoformat()),
            )
        except IOError:
            return None

    def to_markdown(self) -> str:
        """Convert skill to markdown with YAML frontmatter."""
        frontmatter = {
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'tags': self.tags,
            'author': self.author,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat(),
        }

        fm_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        return f"---\n{fm_yaml}---\n\n{self.content}"


class SkillsManager:
    """
    Manages Skills for Hermes Toolkit.
    """

    SKILL_TEMPLATE = """---
title: "{title}"
category: "{category}"
description: "{description}"
tags: [{tags}]
author: "{author}"
version: "1.0.0"
created_at: "{created_at}"
updated_at: "{updated_at}"
---

# {title}

{content}
"""

    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir:
            self._skills_dir = Path(skills_dir)
        else:
            self._skills_dir = Path.home() / '.hermes' / 'skills'

        self._skills_dir.mkdir(parents=True, exist_ok=True)

    def list_skills(self, category: Optional[str] = None) -> List[SkillEntry]:
        """
        List all skills, optionally filtered by category.

        Returns:
            List of SkillEntry objects
        """
        skills = []

        if category:
            categories = [self._skills_dir / category]
        else:
            categories = [self._skills_dir]
            # Get all subdirectories as categories
            for item in self._skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    categories.append(item)

        for cat_dir in categories:
            if not cat_dir.exists():
                continue

            for md_file in cat_dir.rglob('*.md'):
                # Skip README files
                if md_file.name.lower() in ('readme.md', 'readme'):
                    continue

                skill = SkillEntry.from_file(md_file)
                if skill:
                    skills.append(skill)

        # Sort by category and name
        skills.sort(key=lambda s: (s.category, s.name))
        return skills

    def get_categories(self) -> List[str]:
        """Get all skill categories."""
        categories = set()
        for item in self._skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories.add(item.name)

        return sorted(list(categories))

    def get_skill(self, name: str, category: str) -> Optional[SkillEntry]:
        """Get a specific skill by name and category."""
        skill_file = self._skills_dir / category / f'{name}.md'
        if skill_file.exists():
            return SkillEntry.from_file(skill_file)
        return None

    def create_skill(
        self,
        name: str,
        title: str,
        category: str,
        content: str,
        description: str = '',
        tags: Optional[List[str]] = None,
        author: str = '',
    ) -> bool:
        """Create a new skill."""
        try:
            # Create category directory if needed
            cat_dir = self._skills_dir / category
            cat_dir.mkdir(parents=True, exist_ok=True)

            # Create skill file
            skill = SkillEntry(
                name=name,
                category=category,
                title=title,
                description=description,
                tags=tags or [],
                author=author,
                content=content,
                created_at=datetime.now().isoformat(),
            )

            skill_file = cat_dir / f'{name}.md'
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(skill.to_markdown())

            return True
        except IOError as e:
            print(f"Error creating skill: {e}")
            return False

    def update_skill(self, skill: SkillEntry) -> bool:
        """Update an existing skill."""
        try:
            skill_file = self._skills_dir / skill.category / f'{skill.name}.md'
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(skill.to_markdown())
            return True
        except IOError:
            return False

    def delete_skill(self, name: str, category: str) -> bool:
        """Delete a skill."""
        try:
            skill_file = self._skills_dir / category / f'{name}.md'
            if skill_file.exists():
                skill_file.unlink()
                return True
            return False
        except IOError:
            return False

    def search_skills(self, query: str) -> List[SkillEntry]:
        """
        Search skills by name, title, description, or content.

        Args:
            query: Search query string

        Returns:
            List of matching SkillEntry objects
        """
        query_lower = query.lower()
        results = []

        for skill in self.list_skills():
            # Search in name, title, description, content, tags
            searchable = ' '.join([
                skill.name,
                skill.title,
                skill.description,
                skill.content,
                ' '.join(skill.tags),
            ]).lower()

            if query_lower in searchable:
                results.append(skill)

        return results

    def import_skill(self, file_path: str) -> bool:
        """Import a skill from an external markdown file."""
        try:
            source = Path(file_path)
            if not source.exists():
                return False

            skill = SkillEntry.from_file(source)
            if not skill:
                return False

            # Create category if needed
            cat_dir = self._skills_dir / skill.category
            cat_dir.mkdir(parents=True, exist_ok=True)

            # Copy file
            dest = cat_dir / f'{skill.name}.md'
            with open(source, 'r', encoding='utf-8') as src:
                with open(dest, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

            return True
        except IOError:
            return False

    def export_skill(self, name: str, category: str, dest_dir: str) -> bool:
        """Export a skill to an external directory."""
        try:
            skill_file = self._skills_dir / category / f'{name}.md'
            if not skill_file.exists():
                return False

            dest = Path(dest_dir) / f'{name}.md'
            with open(skill_file, 'r', encoding='utf-8') as src:
                with open(dest, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

            return True
        except IOError:
            return False

    def get_new_skill_template(self, category: str = 'general') -> Dict[str, Any]:
        """Get a template for creating a new skill."""
        return {
            'name': 'new-skill',
            'title': 'New Skill',
            'category': category,
            'description': '',
            'tags': [],
            'author': '',
            'content': '# New Skill\n\nDescribe your skill here...',
        }

    @property
    def skills_dir(self) -> Path:
        return self._skills_dir
