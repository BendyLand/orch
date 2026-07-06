import subprocess
from pathlib import Path
import sys


def discover_repositories(base_path: Path):
    manifest = {}
    # We use .rglob('*') to recursively find everything, but we will
    # use a helper set to prune paths so we don't dive into found repos.
    for path in sorted(base_path.rglob(".git")):
        # .rglob('.git') gives us the path to the actual .git folder.
        # We want the parent directory, which is the project root.
        repo_root = path.parent
        # Check if we are already inside a repository we've recorded
        # This prevents picking up internal things like runtime/grammars/sources
        already_tracked = False
        for tracked_path in manifest.keys():
            if tracked_path in repo_root.parents:
                already_tracked = True
                break
        if already_tracked:
            continue
        # Get the relative path from your main code directory
        rel_path = repo_root.relative_to(base_path)
        # Query Git natively for the remote origin URL
        try:
            url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            url = "no-remote"
        manifest[repo_root] = (rel_path, url)
    return manifest


def start():
    args = sys.argv
    if len(args) < 2:
        print("Usage: orch <path>")
        exit(1)
