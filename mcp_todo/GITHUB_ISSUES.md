# GitHub Issue Creation

Create GitHub issues from natural language prompts with automatic initialization (labels, assignees, checklists, and related issue linking).

## Features

- ✅ **Natural Language Parsing** - Create issues from plain English
- ✅ **Auto-Initialization** - Automatically assigns to `sburdges-eng`, adds labels, creates checklists
- ✅ **Priority Detection** - Detects `[high priority]`, `[urgent]` markers
- ✅ **Related Issue Linking** - Searches for and links related issues by keyword
- ✅ **Batch Creation** - Create multiple issues from bullet lists
- ✅ **Smart Labels** - Adds `todo`, `in-progress`, `high-priority` based on context

## Quick Start

### Setup

1. **Install requirements:**
   ```bash
   pip install requests
   ```

2. **Set GitHub token:**
   ```bash
   export GITHUB_TOKEN="your_github_personal_access_token"
   ```

   Or create `~/.mcp_todo/github_config.json`:
   ```json
   {
     "token": "your_github_personal_access_token"
   }
   ```

### Create a Single Issue

```bash
# Basic issue
python -m mcp_todo.cli create-issue \
  "Add user authentication" \
  --repo owner/repo

# High priority issue
python -m mcp_todo.cli create-issue \
  "Fix critical security bug [high priority]" \
  --repo owner/repo

# Start immediately (mark as in-progress)
python -m mcp_todo.cli create-issue \
  "Implement API endpoint" \
  --repo owner/repo \
  --start

# Add custom labels
python -m mcp_todo.cli create-issue \
  "Add SQLite support" \
  --repo owner/repo \
  --labels "database,enhancement"
```

### Create Multiple Issues

From a text file with bullet points:

**issues.txt:**
```
- Add logging support
- Implement error handling [high priority]
- Write unit tests
- Update documentation
```

```bash
python -m mcp_todo.cli create-issues \
  --repo owner/repo \
  --file issues.txt
```

Or from stdin:
```bash
python -m mcp_todo.cli create-issues --repo owner/repo
# Type or paste your issues, then press Ctrl+D
- Task 1
- Task 2
```

## Python API

### Create Single Issue

```python
from mcp_todo.github_issues import create_issue_from_prompt

# Simple usage
issue = create_issue_from_prompt(
    prompt="Add PostgreSQL support",
    owner="myorg",
    repo="myproject",
    token="ghp_xxxx"  # or set GITHUB_TOKEN
)

print(f"Created issue #{issue['number']}: {issue['title']}")
print(f"URL: {issue['html_url']}")
```

### Create Issue with Options

```python
from mcp_todo.github_issues import create_issue_from_prompt

issue = create_issue_from_prompt(
    prompt="Implement user dashboard [high priority]",
    owner="myorg",
    repo="myproject",
    start=True,  # Mark as in-progress
    find_related=True,  # Link related issues
    custom_labels=["frontend", "UI"],
)
```

### Batch Creation

```python
from mcp_todo.github_issues import create_issues_batch

prompts = [
    "Add logging",
    "Fix bug in login",
    "Update README [high priority]",
]

issues = create_issues_batch(
    prompts=prompts,
    owner="myorg",
    repo="myproject",
    start_all=False,  # Don't mark all as in-progress
)

for issue in issues:
    if "error" not in issue:
        print(f"✓ Created #{issue['number']}")
```

### Advanced: Custom Templates

```python
from mcp_todo.github_issues import GitHubIssueCreator, GitHubIssueTemplate

# Create custom template
template = GitHubIssueTemplate(
    title="Implement caching layer",
    body="Add Redis caching for better performance",
    priority="high",
    labels=["performance", "backend"],
    checklist=[
        "Design cache strategy",
        "Implement Redis client",
        "Add cache invalidation",
        "Write tests",
        "Benchmark performance",
    ],
    relates_to=[10, 15],  # Link to issues #10 and #15
    depends_on=[20],  # Depends on issue #20
)

# Create issue
creator = GitHubIssueCreator("myorg", "myproject", token="ghp_xxxx")
issue = creator.create_issue(template)
```

### Parse Natural Language

```python
from mcp_todo.github_issues import IssueParser

# Parse single prompt
template = IssueParser.parse_single(
    "Add support for WebSockets [urgent]",
    start=True
)

print(template.title)  # "Add support for WebSockets"
print(template.priority)  # "urgent"
print(template.labels)  # ["in-progress", "high-priority"]

# Parse multiple from text
text = """
- Add user authentication
- Implement API rate limiting
- Write integration tests
"""

templates = IssueParser.parse_multiple(text)
print(f"Found {len(templates)} issues")  # 3
```

## Issue Template Format

Created issues include:

### Default Structure

```markdown
[Issue Description]

## Checklist
- [ ] Define task requirements
- [ ] Implement initial solution
- [ ] Write/update tests
- [ ] Review and refine
- [ ] Submit PR

## Related Issues
- Relates to #123
- Depends on #456
```

### Default Labels

- **todo** - Not started (default)
- **in-progress** - Active work (when using `--start`)
- **high-priority** - High or urgent priority detected

### Default Assignee

- **sburdges-eng** - Automatically assigned

## Priority Detection

The parser automatically detects priority markers:

| Marker | Priority |
|--------|----------|
| `[high priority]` or `high priority` | `high` |
| `[urgent]` or `urgent` | `urgent` |
| `[low priority]` | `low` |
| (none) | `medium` |

High and urgent priorities automatically add `high-priority` label.

## Related Issue Linking

When creating an issue, the system:

1. Extracts keywords from the issue description
2. Searches existing issues for those keywords
3. Automatically links top 3 related issues in the body

Disable with `--no-related` flag.

## Examples

### Example 1: Bug Fix

```bash
python -m mcp_todo.cli create-issue \
  "Users can't log in with special characters in password [urgent]" \
  --repo mycompany/webapp \
  --labels "bug,auth"
```

Creates:
- Title: "Users can't log in with special characters in password"
- Priority: urgent
- Labels: `bug`, `auth`, `high-priority`, `in-progress`
- Assigned to: `sburdges-eng`

### Example 2: Feature Request

```bash
python -m mcp_todo.cli create-issue \
  "Add dark mode to dashboard" \
  --repo mycompany/webapp \
  --labels "enhancement,UI" \
  --start
```

Creates:
- Title: "Add dark mode to dashboard"
- Priority: medium
- Labels: `enhancement`, `UI`, `in-progress`
- Status: In Progress

### Example 3: Batch Issues from File

**sprint-tasks.txt:**
```
- Implement user profile editing
- Add email verification [high priority]
- Create admin dashboard
- Fix memory leak in background worker [urgent]
- Write API documentation
```

```bash
python -m mcp_todo.cli create-issues \
  --repo mycompany/webapp \
  --file sprint-tasks.txt \
  --yes
```

Creates 5 issues with appropriate priorities and labels.

## Configuration

### GitHub Token

Token needs these permissions:
- **repo** - Full repository access
- **public_repo** - Public repository access (for public repos)

Create token at: https://github.com/settings/tokens

### Config File Format

`~/.mcp_todo/github_config.json`:
```json
{
  "token": "ghp_yourtoken",
  "default_repo": "owner/repo",
  "default_labels": ["automated"],
  "default_assignees": ["sburdges-eng", "teammate"]
}
```

## Integration with MCP TODO

You can create issues from existing TODO items:

```python
from mcp_todo.storage import TodoStorage
from mcp_todo.github_issues import GitHubIssueCreator, GitHubIssueTemplate

storage = TodoStorage()
todos = storage.list_all(status="pending", priority="high")

creator = GitHubIssueCreator("owner", "repo", token="ghp_xxxx")

for todo in todos:
    template = GitHubIssueTemplate(
        title=todo.title,
        body=todo.description or "",
        priority=todo.priority.value,
        labels=todo.tags,
    )
    
    issue = creator.create_issue(template)
    print(f"Created issue #{issue['number']} for TODO {todo.id}")
```

## Troubleshooting

### "requests library required"

Install the requests library:
```bash
pip install requests
```

### "GitHub token required"

Set your token:
```bash
export GITHUB_TOKEN="your_token"
```

Or add to `~/.mcp_todo/github_config.json`

### "Repository must be in format 'owner/repo'"

Ensure you use the correct format:
```bash
--repo myusername/myproject
```

Not:
```bash
--repo myproject  # Wrong
--repo github.com/myusername/myproject  # Wrong
```

### API Rate Limiting

GitHub API has rate limits:
- **5000 requests/hour** (authenticated)
- **60 requests/hour** (unauthenticated)

For batch creation of many issues, consider adding delays:

```python
import time
from mcp_todo.github_issues import create_issue_from_prompt

for prompt in large_list:
    issue = create_issue_from_prompt(prompt, ...)
    time.sleep(1)  # Wait 1 second between issues
```

## License

MIT License - See LICENSE file for details.
