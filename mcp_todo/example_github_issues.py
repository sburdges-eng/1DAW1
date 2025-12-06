#!/usr/bin/env python3
"""
Example: Creating GitHub Issues from Natural Language

This example demonstrates how to use the GitHub issue creation feature
to convert natural language prompts into structured GitHub issues.

Requirements:
- pip install requests
- Set GITHUB_TOKEN environment variable
"""

import os
from mcp_todo.github_issues import (
    GitHubIssueTemplate,
    IssueParser,
    GitHubIssueCreator,
    create_issue_from_prompt,
)


def example_1_simple():
    """Example 1: Create a simple issue from natural language."""
    print("=" * 60)
    print("Example 1: Simple Issue Creation")
    print("=" * 60)

    # Parse natural language prompt
    template = IssueParser.parse_single(
        "Add user authentication with OAuth support"
    )

    print(f"Title: {template.title}")
    print(f"Priority: {template.priority}")
    print(f"Labels: {template.get_labels()}")
    print(f"Assignees: {template.assignees}")
    print()


def example_2_with_priority():
    """Example 2: Issue with priority detection."""
    print("=" * 60)
    print("Example 2: Issue with Priority Detection")
    print("=" * 60)

    template = IssueParser.parse_single(
        "Fix critical security vulnerability in login endpoint [urgent]"
    )

    print(f"Title: {template.title}")
    print(f"Priority: {template.priority}")
    print(f"Labels: {template.get_labels()}")
    print()


def example_3_multiline():
    """Example 3: Issue with detailed description."""
    print("=" * 60)
    print("Example 3: Multi-line Description")
    print("=" * 60)

    prompt = """Add PostgreSQL database support

We need to add PostgreSQL as an alternative to SQLite.
This should include:
- Connection pooling
- Migration support
- Query optimization
"""

    template = IssueParser.parse_single(prompt)

    print(f"Title: {template.title}")
    print(f"Body:\n{template.body}")
    print()


def example_4_batch():
    """Example 4: Create multiple issues from a list."""
    print("=" * 60)
    print("Example 4: Batch Issue Creation")
    print("=" * 60)

    text = """
    - Add logging to API endpoints
    - Implement rate limiting [high priority]
    - Write integration tests
    - Update API documentation
    - Add Prometheus metrics
    """

    templates = IssueParser.parse_multiple(text)

    print(f"Parsed {len(templates)} issues:")
    for i, t in enumerate(templates, 1):
        print(f"{i}. {t.title} (priority: {t.priority})")
    print()


def example_5_custom_template():
    """Example 5: Create a custom issue template."""
    print("=" * 60)
    print("Example 5: Custom Template")
    print("=" * 60)

    template = GitHubIssueTemplate(
        title="Implement Redis caching layer",
        body="Add Redis for session storage and API response caching",
        priority="high",
        labels=["performance", "backend"],
        checklist=[
            "Research Redis client libraries",
            "Design cache key structure",
            "Implement session storage",
            "Add API response caching",
            "Write cache invalidation logic",
            "Benchmark performance improvements",
            "Write tests",
            "Update documentation",
        ],
        relates_to=[15, 23],  # Related to issues #15 and #23
    )

    print(f"Title: {template.title}")
    print(f"Labels: {template.get_labels()}")
    print("\nFormatted body:")
    print("-" * 40)
    print(template.format_body())
    print()


def example_6_with_github_api():
    """Example 6: Actually create an issue (requires token and repo)."""
    print("=" * 60)
    print("Example 6: Create Issue via GitHub API")
    print("=" * 60)

    # Check for token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠ GITHUB_TOKEN not set - skipping API call")
        print("To actually create issues, set GITHUB_TOKEN environment variable")
        print()
        return

    # NOTE: Change these to your actual repo
    owner = "your-username"
    repo = "your-repo"

    print("⚠ This would create a real issue!")
    print(f"Repository: {owner}/{repo}")
    print("Set owner/repo variables to test this example")
    print()

    # Uncomment to actually create issue:
    # issue = create_issue_from_prompt(
    #     prompt="Test issue from Python script",
    #     owner=owner,
    #     repo=repo,
    #     token=token,
    # )
    # print(f"✓ Created issue #{issue['number']}: {issue['title']}")
    # print(f"  URL: {issue['html_url']}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "GitHub Issue Creation Examples" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    example_1_simple()
    example_2_with_priority()
    example_3_multiline()
    example_4_batch()
    example_5_custom_template()
    example_6_with_github_api()

    print("=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print()
    print("To actually create issues, use:")
    print("  python -m mcp_todo.cli create-issue 'Your prompt' --repo owner/repo")
    print()


if __name__ == "__main__":
    main()
