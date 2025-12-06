"""
GitHub Issue Creator

Creates and manages GitHub issues from natural language prompts.
Integrates with the MCP TODO system for seamless task-to-issue conversion.

Features:
- Create issues from natural language
- Auto-assign to sburdges-eng
- Add labels (todo, in-progress, high-priority, etc.)
- Add default checklists
- Link to related issues
- Batch issue creation
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

try:
    import requests
except ImportError:
    requests = None


@dataclass
class GitHubIssueTemplate:
    """Template for creating a GitHub issue."""
    title: str
    body: str
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=lambda: ["sburdges-eng"])
    milestone: Optional[int] = None
    priority: str = "medium"  # low, medium, high, urgent

    # Checklist items to add to the body
    checklist: List[str] = field(default_factory=lambda: [
        "Define task requirements",
        "Implement initial solution",
        "Write/update tests",
        "Review and refine",
        "Submit PR"
    ])

    # Related issues
    relates_to: List[int] = field(default_factory=list)
    blocks: List[int] = field(default_factory=list)
    depends_on: List[int] = field(default_factory=list)

    def format_body(self) -> str:
        """Format the issue body with checklist and related issues."""
        parts = []

        # Description
        if self.body:
            parts.append(self.body)
            parts.append("")

        # Checklist
        if self.checklist:
            parts.append("## Checklist")
            for item in self.checklist:
                parts.append(f"- [ ] {item}")
            parts.append("")

        # Related issues
        if self.relates_to:
            parts.append("## Related Issues")
            for issue_num in self.relates_to:
                parts.append(f"- Relates to #{issue_num}")
            parts.append("")

        if self.depends_on:
            if not self.relates_to:
                parts.append("## Dependencies")
            for issue_num in self.depends_on:
                parts.append(f"- Depends on #{issue_num}")
            parts.append("")

        if self.blocks:
            if not self.relates_to and not self.depends_on:
                parts.append("## Blocks")
            for issue_num in self.blocks:
                parts.append(f"- Blocks #{issue_num}")
            parts.append("")

        return "\n".join(parts).strip()

    def get_labels(self) -> List[str]:
        """Get all labels including priority-based ones."""
        labels = list(self.labels)

        # Add priority label
        if self.priority == "high" or self.priority == "urgent":
            if "high-priority" not in labels:
                labels.append("high-priority")

        # Ensure todo label is present
        if "todo" not in labels and "in-progress" not in labels:
            labels.append("todo")

        return labels


class GitHubIssueCreator:
    """
    Creates GitHub issues using the GitHub API.

    Supports authentication via:
    - Environment variable: GITHUB_TOKEN
    - Config file: ~/.mcp_todo/github_config.json
    """

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        config_dir: Optional[str] = None
    ):
        """
        Initialize GitHub issue creator.

        Args:
            owner: Repository owner (username or org)
            repo: Repository name
            token: GitHub personal access token (optional, reads from env/config)
            config_dir: Configuration directory (default: ~/.mcp_todo/)
        """
        if requests is None:
            raise ImportError(
                "requests library required for GitHub integration. "
                "Install with: pip install requests"
            )

        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

        # Get token from various sources
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token and config_dir:
            self.token = self._load_token_from_config(config_dir)

        if not self.token:
            # Try default config location
            default_config = os.path.expanduser("~/.mcp_todo")
            self.token = self._load_token_from_config(default_config)

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _load_token_from_config(self, config_dir: str) -> Optional[str]:
        """Load GitHub token from config file."""
        config_path = os.path.join(config_dir, "github_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("token")
            except Exception:
                pass
        return None

    def create_issue(self, template: GitHubIssueTemplate) -> Dict[str, Any]:
        """
        Create a GitHub issue from a template.

        Args:
            template: Issue template with title, body, labels, etc.

        Returns:
            GitHub API response with issue details

        Raises:
            requests.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/issues"

        # Build request payload
        payload = {
            "title": template.title,
            "body": template.format_body(),
            "labels": template.get_labels(),
        }

        if template.assignees:
            payload["assignees"] = template.assignees

        if template.milestone:
            payload["milestone"] = template.milestone

        # Make request
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def search_issues(self, query: str, state: str = "all") -> List[Dict[str, Any]]:
        """
        Search for issues by keyword.

        Args:
            query: Search query
            state: Issue state (open, closed, all)

        Returns:
            List of matching issues
        """
        search_url = "https://api.github.com/search/issues"
        params = {
            "q": f"{query} repo:{self.owner}/{self.repo} is:issue",
            "per_page": 10,
        }

        response = requests.get(search_url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json().get("items", [])

    def find_related_issues(self, keywords: List[str]) -> List[int]:
        """
        Find related issues by searching for keywords.

        Args:
            keywords: List of keywords to search for

        Returns:
            List of issue numbers
        """
        related = []
        for keyword in keywords:
            try:
                issues = self.search_issues(keyword)
                related.extend([issue["number"] for issue in issues[:3]])
            except Exception:
                continue

        # Remove duplicates and return
        return list(set(related))


class IssueParser:
    """
    Parses natural language prompts into GitHub issue templates.
    """

    @staticmethod
    def parse_single(prompt: str, start: bool = False) -> GitHubIssueTemplate:
        """
        Parse a single natural language prompt into an issue template.

        Args:
            prompt: Natural language description
            start: If True, mark as in-progress

        Returns:
            Issue template ready to be created

        Examples:
            "Finish Phase 1 testing and attach logs" →
                title: "Finish Phase 1 testing and attach logs"
                labels: ["todo"]
                checklist: default

            "Add SQLite support [high priority]" →
                title: "Add SQLite support"
                priority: "high"
                labels: ["todo", "high-priority"]
        """
        # Extract priority markers
        priority = "medium"
        priority_patterns = [
            (r"\[high priority\]", "high"),
            (r"\[urgent\]", "urgent"),
            (r"\[low priority\]", "low"),
            (r"high priority", "high"),
            (r"urgent", "urgent"),
        ]

        clean_prompt = prompt
        for pattern, pri in priority_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                priority = pri
                clean_prompt = re.sub(pattern, "", clean_prompt, flags=re.IGNORECASE)
                break

        clean_prompt = clean_prompt.strip()

        # Extract title (first line or sentence)
        lines = clean_prompt.split("\n")
        title = lines[0].strip()

        # Body is remaining lines
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Determine labels
        labels = ["in-progress"] if start else ["todo"]

        return GitHubIssueTemplate(
            title=title,
            body=body,
            priority=priority,
            labels=labels,
        )

    @staticmethod
    def parse_multiple(text: str) -> List[GitHubIssueTemplate]:
        """
        Parse multiple issues from text (bullet list or paragraphs).

        Args:
            text: Multi-line text with issue descriptions

        Returns:
            List of issue templates

        Examples:
            '''
            - MCP server: missing help text
            - CLI: add --scan mode
            - Storage backend: add SQLite support
            '''
            →  3 separate issues
        """
        templates = []

        # Try parsing as bullet list first
        lines = text.split("\n")
        bullet_items = []

        for line in lines:
            line = line.strip()
            # Match common bullet formats: -, *, •, 1., etc.
            if re.match(r"^[-*•]\s+", line) or re.match(r"^\d+\.\s+", line):
                # Remove bullet marker
                item = re.sub(r"^[-*•]\s+", "", line)
                item = re.sub(r"^\d+\.\s+", "", item)
                bullet_items.append(item.strip())

        if bullet_items:
            # Parse each bullet as separate issue
            for item in bullet_items:
                if item:
                    templates.append(IssueParser.parse_single(item))
        else:
            # Try parsing as paragraphs separated by blank lines
            paragraphs = re.split(r"\n\s*\n", text)
            for para in paragraphs:
                para = para.strip()
                if para:
                    templates.append(IssueParser.parse_single(para))

        return templates

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract keywords for finding related issues.

        Args:
            text: Issue text

        Returns:
            List of potential keywords
        """
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "should", "could", "may", "might",
            "add", "create", "implement", "fix", "update", "remove", "delete"
        }

        # Extract words (alphanumeric sequences)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Filter out stop words
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords, up to 5
        return list(dict.fromkeys(keywords))[:5]


def create_issue_from_prompt(
    prompt: str,
    owner: str,
    repo: str,
    token: Optional[str] = None,
    start: bool = False,
    find_related: bool = True,
    custom_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    High-level function to create a GitHub issue from a natural language prompt.

    Args:
        prompt: Natural language description
        owner: Repository owner
        repo: Repository name
        token: GitHub token (optional)
        start: Mark as in-progress immediately
        find_related: Search for and link related issues
        custom_labels: Additional custom labels

    Returns:
        Created issue details from GitHub API

    Examples:
        >>> create_issue_from_prompt(
        ...     "Add support for PostgreSQL database",
        ...     owner="myorg",
        ...     repo="myproject",
        ...     start=True
        ... )
    """
    # Parse prompt
    template = IssueParser.parse_single(prompt, start=start)

    # Add custom labels
    if custom_labels:
        template.labels.extend(custom_labels)

    # Create issue creator
    creator = GitHubIssueCreator(owner, repo, token=token)

    # Find related issues
    if find_related:
        keywords = IssueParser.extract_keywords(prompt)
        related = creator.find_related_issues(keywords)
        if related:
            template.relates_to = related[:3]  # Limit to 3

    # Create the issue
    return creator.create_issue(template)


def create_issues_batch(
    prompts: List[str],
    owner: str,
    repo: str,
    token: Optional[str] = None,
    start_all: bool = False,
) -> List[Dict[str, Any]]:
    """
    Create multiple GitHub issues from a list of prompts.

    Args:
        prompts: List of natural language descriptions
        owner: Repository owner
        repo: Repository name
        token: GitHub token (optional)
        start_all: Mark all as in-progress

    Returns:
        List of created issue details
    """
    creator = GitHubIssueCreator(owner, repo, token=token)
    results = []

    for prompt in prompts:
        try:
            template = IssueParser.parse_single(prompt, start=start_all)
            issue = creator.create_issue(template)
            results.append(issue)
        except Exception as e:
            # Log error but continue with other issues
            print(f"Error creating issue for '{prompt[:50]}...': {e}")
            results.append({"error": str(e), "prompt": prompt})

    return results
