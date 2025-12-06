# GitHub Issue Creation Feature - Implementation Summary

## Overview

Successfully implemented a comprehensive GitHub issue creation system that allows creating GitHub issues from natural language prompts. This feature integrates with the existing MCP TODO system and provides both CLI and Python API interfaces.

## Features Implemented

### ✅ Core Functionality

1. **Natural Language Parsing**
   - Parse plain English prompts into structured issue templates
   - Extract titles, descriptions, and metadata
   - Detect priority markers (`[high priority]`, `[urgent]`, etc.)
   - Support multi-line descriptions

2. **Auto-Initialization**
   - Automatically assigns issues to `sburdges-eng`
   - Adds appropriate labels (`todo`, `in-progress`, `high-priority`)
   - Creates default checklists for task tracking
   - Priority-based label assignment

3. **Batch Issue Creation**
   - Parse bullet lists (-, *, •)
   - Parse numbered lists (1., 2., etc.)
   - Parse paragraph-separated text
   - Create multiple issues in one command

4. **Related Issue Linking**
   - Extract keywords from issue descriptions
   - Search existing issues for related content
   - Automatically link top 3 related issues
   - Support manual linking via template

5. **Smart Labels**
   - `todo` - Default for new issues
   - `in-progress` - When started immediately
   - `high-priority` - For high/urgent priorities
   - Custom labels via CLI or API

## Files Created

### Core Module
- **`mcp_todo/github_issues.py`** (500+ lines)
  - `GitHubIssueTemplate` - Data structure for issues
  - `GitHubIssueCreator` - GitHub API client
  - `IssueParser` - Natural language parser
  - Helper functions for single/batch creation

### CLI Integration
- **`mcp_todo/cli.py`** (modified)
  - Added `create-issue` command
  - Added `create-issues` batch command
  - Integrated with existing MCP TODO CLI

### Documentation
- **`mcp_todo/GITHUB_ISSUES.md`** (350+ lines)
  - Complete usage guide
  - CLI examples
  - Python API examples
  - Troubleshooting guide
  - Configuration instructions

### Examples
- **`mcp_todo/example_github_issues.py`**
  - 6 comprehensive examples
  - Demonstrates all features
  - Runnable demonstration script

### Tests
- **`tests_music-brain/test_github_issues.py`**
  - Template creation tests
  - Parser tests
  - Priority detection tests
  - Batch parsing tests
  - Keyword extraction tests

## Usage Examples

### CLI

```bash
# Create single issue
python -m mcp_todo.cli create-issue \
  "Add user authentication [high priority]" \
  --repo owner/repo

# Create multiple issues from file
python -m mcp_todo.cli create-issues \
  --repo owner/repo \
  --file tasks.txt

# Start immediately (mark as in-progress)
python -m mcp_todo.cli create-issue \
  "Implement API endpoint" \
  --repo owner/repo \
  --start
```

### Python API

```python
from mcp_todo.github_issues import create_issue_from_prompt

# Simple usage
issue = create_issue_from_prompt(
    prompt="Add PostgreSQL support",
    owner="myorg",
    repo="myproject",
    token="ghp_xxxx"
)

print(f"Created issue #{issue['number']}")
```

## Configuration

### GitHub Token

Set via:
1. Environment variable: `GITHUB_TOKEN`
2. Config file: `~/.mcp_todo/github_config.json`
3. CLI parameter: `--token`

### Required Permissions

- `repo` - Full repository access
- Or `public_repo` - For public repositories only

## Architecture

### Components

```
GitHubIssueCreator
├── Authentication (token-based)
├── Issue Creation (POST /repos/{owner}/{repo}/issues)
├── Issue Search (GET /search/issues)
└── Related Issue Linking

IssueParser
├── Single Prompt Parsing
├── Multiple Prompt Parsing (bullets/numbered/paragraphs)
├── Priority Detection (regex-based)
└── Keyword Extraction

GitHubIssueTemplate
├── Issue Metadata (title, body, labels, etc.)
├── Checklist Management
├── Related Issue Tracking
└── Body Formatting
```

### Integration Points

1. **MCP TODO System** - Shares configuration directory
2. **GitHub API** - RESTful API via `requests` library
3. **CLI** - Extends existing `mcp_todo.cli` module

## Testing

### Manual Testing
```bash
# Test parsing
python -c "
from mcp_todo.github_issues import IssueParser
template = IssueParser.parse_single('Test issue [urgent]')
print(template.title, template.priority)
"

# Run examples
python mcp_todo/example_github_issues.py
```

### Unit Tests
```bash
pytest tests_music-brain/test_github_issues.py -v
```

## Dependencies

### Required
- `requests` - For GitHub API calls
  ```bash
  pip install requests
  ```

### Optional
- None

## Future Enhancements

Potential improvements for future iterations:

1. **MCP Server Integration**
   - Add MCP server tools for AI assistants
   - Allow Claude/Cursor to create issues directly

2. **Advanced Features**
   - Milestone assignment
   - Project board integration
   - Issue templates from repository
   - Label autocomplete

3. **Bidirectional Sync**
   - Convert GitHub issues to TODOs
   - Sync issue status back to TODOs
   - Watch for issue updates

4. **Enhanced Parsing**
   - Extract due dates from natural language
   - Parse markdown checklists from prompts
   - Support for issue templates

5. **Workflow Integration**
   - Auto-create PR when issue is started
   - Link commits to issues
   - Auto-close issues from PR merge

## License

MIT License - Consistent with parent project

## Summary

This implementation provides a complete, production-ready GitHub issue creation system that:

- ✅ Parses natural language into structured issues
- ✅ Automatically initializes issues with labels and assignees
- ✅ Supports batch creation from lists
- ✅ Links related issues automatically
- ✅ Integrates seamlessly with existing MCP TODO system
- ✅ Provides both CLI and Python API
- ✅ Includes comprehensive documentation and examples
- ✅ Is fully tested and validated

The feature is ready for immediate use and can be extended with additional capabilities as needed.
