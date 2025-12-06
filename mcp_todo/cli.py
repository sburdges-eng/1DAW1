#!/usr/bin/env python3
"""
MCP TODO CLI

Command-line interface for managing TODOs directly.
Useful for testing and manual management.

Usage:
    python -m mcp_todo.cli list
    python -m mcp_todo.cli add "My task" --priority high
    python -m mcp_todo.cli complete abc123
    python -m mcp_todo.cli create-issue "Add feature X" --repo owner/repo
"""

import argparse
import json
import sys
import os
from typing import Optional

from .storage import TodoStorage
from .models import TodoStatus, TodoPriority


def cmd_add(args, storage: TodoStorage):
    """Add a new TODO."""
    tags = args.tags.split(",") if args.tags else []

    todo = storage.add(
        title=args.title,
        description=args.description or "",
        priority=args.priority,
        tags=tags,
        project=args.project,
        due_date=args.due,
        context=args.context or "",
        ai_source="cli",
    )

    print(f"Created: {todo}")
    print(f"  ID: {todo.id}")


def cmd_list(args, storage: TodoStorage):
    """List TODOs."""
    tags = args.tags.split(",") if args.tags else None

    todos = storage.list_all(
        project=args.project,
        status=args.status,
        priority=args.priority,
        tags=tags,
        include_completed=not args.hide_completed,
    )

    if not todos:
        print("No TODOs found.")
        return

    # Group by status if not filtering
    if not args.status:
        by_status = {}
        for todo in todos:
            status = todo.status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(todo)

        status_order = ["in_progress", "pending", "blocked", "completed", "cancelled"]
        for status in status_order:
            if status in by_status:
                print(f"\n{status.upper().replace('_', ' ')}:")
                for todo in by_status[status]:
                    print(f"  {todo}")
    else:
        for todo in todos:
            print(todo)

    print(f"\nTotal: {len(todos)} items")


def cmd_get(args, storage: TodoStorage):
    """Get TODO details."""
    todo = storage.get(args.id, project=args.project)

    if not todo:
        print(f"TODO not found: {args.id}")
        sys.exit(1)

    print(f"ID: {todo.id}")
    print(f"Title: {todo.title}")
    print(f"Status: {todo.status.value}")
    print(f"Priority: {todo.priority.value}")
    print(f"Project: {todo.project or 'default'}")
    print(f"Created: {todo.created_at}")
    print(f"Updated: {todo.updated_at}")

    if todo.description:
        print(f"Description: {todo.description}")
    if todo.tags:
        print(f"Tags: {', '.join(todo.tags)}")
    if todo.due_date:
        print(f"Due: {todo.due_date}")
    if todo.completed_at:
        print(f"Completed: {todo.completed_at}")
    if todo.notes:
        print("Notes:")
        for note in todo.notes:
            print(f"  - {note}")


def cmd_complete(args, storage: TodoStorage):
    """Mark TODO as complete."""
    todo = storage.complete(args.id, project=args.project, ai_source="cli")

    if todo:
        print(f"Completed: {todo}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_start(args, storage: TodoStorage):
    """Mark TODO as in progress."""
    todo = storage.start(args.id, project=args.project, ai_source="cli")

    if todo:
        print(f"Started: {todo}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_delete(args, storage: TodoStorage):
    """Delete a TODO."""
    success = storage.delete(args.id, project=args.project)

    if success:
        print(f"Deleted: {args.id}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_search(args, storage: TodoStorage):
    """Search TODOs."""
    todos = storage.search(args.query, project=args.project)

    if not todos:
        print(f"No TODOs found matching: {args.query}")
        return

    for todo in todos:
        print(todo)


def cmd_summary(args, storage: TodoStorage):
    """Show TODO summary."""
    summary = storage.get_summary(project=args.project)

    print(f"Total: {summary['total']}")
    print(f"  Pending: {summary['pending']}")
    print(f"  In Progress: {summary['in_progress']}")
    print(f"  Completed: {summary['completed']}")

    if summary['by_priority']:
        print("\nBy Priority:")
        for pri, count in summary['by_priority'].items():
            print(f"  {pri}: {count}")


def cmd_export(args, storage: TodoStorage):
    """Export TODOs as Markdown."""
    markdown = storage.export_markdown(project=args.project)
    print(markdown)


def cmd_clear_completed(args, storage: TodoStorage):
    """Clear completed TODOs."""
    count = storage.clear_completed(project=args.project)
    print(f"Cleared {count} completed TODOs")


def cmd_create_issue(args, storage: Optional[TodoStorage] = None):
    """Create a GitHub issue from a prompt."""
    try:
        from .github_issues import create_issue_from_prompt, GitHubIssueCreator
    except ImportError:
        print("Error: GitHub integration requires 'requests' library.")
        print("Install with: pip install requests")
        sys.exit(1)

    # Parse repo (owner/repo format)
    repo_parts = args.repo.split("/")
    if len(repo_parts) != 2:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = repo_parts

    # Get token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token required.")
        print("Set GITHUB_TOKEN environment variable or use --token")
        sys.exit(1)

    # Custom labels
    labels = args.labels.split(",") if args.labels else None

    try:
        # Create the issue
        issue = create_issue_from_prompt(
            prompt=args.prompt,
            owner=owner,
            repo=repo,
            token=token,
            start=args.start,
            find_related=not args.no_related,
            custom_labels=labels,
        )

        print(f"✓ Created issue #{issue['number']}: {issue['title']}")
        print(f"  URL: {issue['html_url']}")
        if issue.get("labels"):
            labels_str = ", ".join([l['name'] for l in issue['labels']])
            print(f"  Labels: {labels_str}")

    except Exception as e:
        print(f"Error creating issue: {e}")
        sys.exit(1)


def cmd_create_issues_batch(args, storage: Optional[TodoStorage] = None):
    """Create multiple GitHub issues from a file or stdin."""
    try:
        from .github_issues import IssueParser, GitHubIssueCreator
    except ImportError:
        print("Error: GitHub integration requires 'requests' library.")
        print("Install with: pip install requests")
        sys.exit(1)

    # Parse repo
    repo_parts = args.repo.split("/")
    if len(repo_parts) != 2:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)

    owner, repo = repo_parts

    # Get token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token required.")
        sys.exit(1)

    # Read input
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    else:
        print("Reading from stdin (Ctrl+D when done)...")
        text = sys.stdin.read()

    # Parse into multiple issues
    templates = IssueParser.parse_multiple(text)

    if not templates:
        print("No issues found in input.")
        sys.exit(1)

    print(f"Found {len(templates)} issues to create:")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t.title}")

    # Confirm
    if not args.yes:
        response = input("\nCreate these issues? [y/N]: ")
        if response.lower() != "y":
            print("Cancelled.")
            sys.exit(0)

    # Create issues
    creator = GitHubIssueCreator(owner, repo, token=token)
    created = []

    for template in templates:
        if args.start:
            template.labels = ["in-progress"]

        try:
            issue = creator.create_issue(template)
            created.append(issue)
            print(f"✓ Created #{issue['number']}: {issue['title']}")
        except Exception as e:
            print(f"✗ Failed to create '{template.title}': {e}")

    print(f"\nCreated {len(created)}/{len(templates)} issues.")


def main():
    parser = argparse.ArgumentParser(
        description="MCP TODO CLI - Manage your tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    mcp-todo add "Fix the bug" --priority high --tags "bug,urgent"
    mcp-todo list --status pending
    mcp-todo complete abc123
    mcp-todo search "authentication"
        """
    )

    parser.add_argument(
        "--storage-dir",
        help="Directory for TODO storage (default: ~/.mcp_todo/)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new TODO")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-d", "--description", help="Task description")
    add_parser.add_argument(
        "-p", "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Priority level"
    )
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    add_parser.add_argument("--project", help="Project name")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_parser.add_argument("-c", "--context", help="Additional context")

    # List command
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List TODOs")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument(
        "--status",
        choices=["pending", "in_progress", "completed", "blocked", "cancelled"],
        help="Filter by status"
    )
    list_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        help="Filter by priority"
    )
    list_parser.add_argument("-t", "--tags", help="Filter by tags (comma-separated)")
    list_parser.add_argument(
        "--hide-completed",
        action="store_true",
        help="Hide completed tasks"
    )

    # Get command
    get_parser = subparsers.add_parser("get", help="Get TODO details")
    get_parser.add_argument("id", help="TODO ID")
    get_parser.add_argument("--project", help="Project name")

    # Complete command
    complete_parser = subparsers.add_parser("complete", aliases=["done"], help="Mark TODO complete")
    complete_parser.add_argument("id", help="TODO ID")
    complete_parser.add_argument("--project", help="Project name")

    # Start command
    start_parser = subparsers.add_parser("start", help="Mark TODO as in progress")
    start_parser.add_argument("id", help="TODO ID")
    start_parser.add_argument("--project", help="Project name")

    # Delete command
    delete_parser = subparsers.add_parser("delete", aliases=["rm"], help="Delete a TODO")
    delete_parser.add_argument("id", help="TODO ID")
    delete_parser.add_argument("--project", help="Project name")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search TODOs")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--project", help="Project name")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show TODO summary")
    summary_parser.add_argument("--project", help="Project name")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export as Markdown")
    export_parser.add_argument("--project", help="Project name")

    # Clear completed command
    clear_parser = subparsers.add_parser("clear-completed", help="Clear completed TODOs")
    clear_parser.add_argument("--project", help="Project name")

    # GitHub issue creation commands
    issue_parser = subparsers.add_parser("create-issue", help="Create a GitHub issue")
    issue_parser.add_argument("prompt", help="Issue description (natural language)")
    issue_parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    issue_parser.add_argument("--token", help="GitHub token (or use GITHUB_TOKEN env var)")
    issue_parser.add_argument("--start", action="store_true", help="Mark as in-progress")
    issue_parser.add_argument("--labels", help="Additional labels (comma-separated)")
    issue_parser.add_argument("--no-related", action="store_true", help="Don't search for related issues")

    # Batch issue creation
    batch_parser = subparsers.add_parser("create-issues", help="Create multiple issues")
    batch_parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    batch_parser.add_argument("--token", help="GitHub token (or use GITHUB_TOKEN env var)")
    batch_parser.add_argument("--file", help="Read from file (default: stdin)")
    batch_parser.add_argument("--start", action="store_true", help="Mark all as in-progress")
    batch_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    storage = TodoStorage(args.storage_dir)

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "ls": cmd_list,
        "get": cmd_get,
        "complete": cmd_complete,
        "done": cmd_complete,
        "start": cmd_start,
        "delete": cmd_delete,
        "rm": cmd_delete,
        "search": cmd_search,
        "summary": cmd_summary,
        "export": cmd_export,
        "clear-completed": cmd_clear_completed,
        "create-issue": cmd_create_issue,
        "create-issues": cmd_create_issues_batch,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        # GitHub issue commands don't need storage
        if args.command in ["create-issue", "create-issues"]:
            cmd_func(args)
        else:
            cmd_func(args, storage)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
