"""
Tests for GitHub issue creation functionality.
"""

import pytest
from mcp_todo.github_issues import (
    GitHubIssueTemplate,
    IssueParser,
)


class TestGitHubIssueTemplate:
    """Test issue template formatting."""

    def test_basic_template(self):
        """Test creating a basic template."""
        template = GitHubIssueTemplate(
            title="Test Issue",
            body="This is a test",
        )

        assert template.title == "Test Issue"
        assert template.body == "This is a test"
        assert "sburdges-eng" in template.assignees

    def test_format_body_with_checklist(self):
        """Test body formatting with checklist."""
        template = GitHubIssueTemplate(
            title="Test",
            body="Description here",
            checklist=["Task 1", "Task 2"],
        )

        body = template.format_body()
        assert "Description here" in body
        assert "## Checklist" in body
        assert "- [ ] Task 1" in body
        assert "- [ ] Task 2" in body

    def test_format_body_with_related_issues(self):
        """Test body formatting with related issues."""
        template = GitHubIssueTemplate(
            title="Test",
            body="Test body",
            relates_to=[10, 20],
            depends_on=[5],
            blocks=[30],
        )

        body = template.format_body()
        assert "Relates to #10" in body
        assert "Depends on #5" in body
        assert "Blocks #30" in body

    def test_priority_labels(self):
        """Test priority-based label assignment."""
        # High priority
        template = GitHubIssueTemplate(
            title="Urgent task",
            priority="high",
        )
        labels = template.get_labels()
        assert "high-priority" in labels
        assert "todo" in labels

        # Medium priority (no high-priority label)
        template2 = GitHubIssueTemplate(
            title="Normal task",
            priority="medium",
        )
        labels2 = template2.get_labels()
        assert "high-priority" not in labels2
        assert "todo" in labels2


class TestIssueParser:
    """Test natural language parsing."""

    def test_parse_simple_prompt(self):
        """Test parsing a simple prompt."""
        template = IssueParser.parse_single("Add user authentication")

        assert template.title == "Add user authentication"
        assert template.priority == "medium"
        assert "todo" in template.labels

    def test_parse_with_priority(self):
        """Test parsing prompt with priority marker."""
        template = IssueParser.parse_single("Fix critical bug [high priority]")

        assert "Fix critical bug" in template.title
        assert template.priority == "high"

        # Test urgent
        template2 = IssueParser.parse_single("Deploy now [urgent]")
        assert template2.priority == "urgent"

    def test_parse_multiline(self):
        """Test parsing multiline description."""
        prompt = """Add SQLite support
        
Need to add SQLite database backend
for better performance"""

        template = IssueParser.parse_single(prompt)

        assert template.title == "Add SQLite support"
        assert "SQLite database backend" in template.body

    def test_parse_with_start_flag(self):
        """Test parsing with start flag."""
        template = IssueParser.parse_single("Implement feature", start=True)

        assert "in-progress" in template.labels
        assert "todo" not in template.labels

    def test_parse_multiple_bullets(self):
        """Test parsing multiple bullet points."""
        text = """
        - Add logging support
        - Implement error handling
        - Write unit tests
        """

        templates = IssueParser.parse_multiple(text)

        assert len(templates) == 3
        assert templates[0].title == "Add logging support"
        assert templates[1].title == "Implement error handling"
        assert templates[2].title == "Write unit tests"

    def test_parse_multiple_numbered(self):
        """Test parsing numbered list."""
        text = """
        1. Create API endpoint
        2. Add validation
        3. Write documentation
        """

        templates = IssueParser.parse_multiple(text)

        assert len(templates) == 3
        assert templates[0].title == "Create API endpoint"

    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Add support for PostgreSQL database with connection pooling"

        keywords = IssueParser.extract_keywords(text)

        # Should extract meaningful words, not stop words
        assert "support" not in keywords  # Stop word
        assert "PostgreSQL" in keywords or "postgresql" in keywords
        assert "database" in keywords
        assert len(keywords) <= 5


class TestGitHubIntegration:
    """Test GitHub API integration (mocked/manual only)."""

    def test_issue_template_to_api_format(self):
        """Test that template converts correctly for API."""
        template = GitHubIssueTemplate(
            title="Test Issue",
            body="Test description",
            priority="high",
            labels=["bug"],
        )

        # Get formatted data
        body = template.format_body()
        labels = template.get_labels()

        # Verify structure
        assert isinstance(body, str)
        assert isinstance(labels, list)
        assert "bug" in labels
        assert "high-priority" in labels

    # NOTE: Actual GitHub API tests would require:
    # - Mock responses using pytest-mock or responses library
    # - Or manual integration tests with real token
    # For now, just test the data structures
