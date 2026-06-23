import urllib.request
import json
import re
import os

def fetch_merged_prs():
    username = "omnipotentchaos"
    url = f"https://api.github.com/search/issues?q=type:pr+author:{username}+is:merged&per_page=100"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    token = os.environ.get("GITHUB_TOKEN")
    
    if token:
        headers["Authorization"] = f"token {token}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data.get("items", [])
        except Exception as e:
            print(f"Error fetching PRs with GITHUB_TOKEN: {e}. Retrying without token...")
            
    # Fallback to unauthenticated request
    headers.pop("Authorization", None)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("items", [])
    except Exception as e:
        print(f"Error fetching PRs from GitHub API: {e}")
        return []

def format_prs(items):
    if not items:
        return "No merged pull requests found or API rate limit exceeded."
        
    repos = {}
    for item in items:
        repo_url = item.get("repository_url", "")
        repo_name = repo_url.split("/repos/")[-1] if "/repos/" in repo_url else "Unknown"
        title = item.get("title", "")
        html_url = item.get("html_url", "")
        number = item.get("number", "")
        merged_at = item.get("closed_at", "")[:10]  # Close date as approximation
        
        # We only want to list GSSOC contributions or external ones, but listing all merged is great!
        if repo_name not in repos:
            repos[repo_name] = []
        repos[repo_name].append(f"  - ⚡ **[#{number}]({html_url})**: {title} *({merged_at})*")

    markdown_lines = []
    markdown_lines.append("### 🚀 Merged Pull Requests & Contributions\n")
    
    # Sort repos by number of contributions descending
    sorted_repos = sorted(repos.items(), key=lambda x: len(x[1]), reverse=True)
    
    for repo, prs in sorted_repos:
        # Ignore user's own profile repo to keep contributions clean
        if repo.lower() == "omnipotentchaos/omnipotentchaos":
            continue
        markdown_lines.append(f"#### 📂 **[{repo}](https://github.com/{repo})**")
        for pr in prs:  # show all PRs per repo
            markdown_lines.append(pr)
        markdown_lines.append("")
        
    return "\n".join(markdown_lines)

def update_readme(pr_content):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} not found.")
        return
        
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"<!-- MERGED_PRS_START -->.*?<!-- MERGED_PRS_END -->"
    replacement = f"<!-- MERGED_PRS_START -->\n\n{pr_content}\n\n<!-- MERGED_PRS_END -->"
    
    if re.search(pattern, content, flags=re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated README.md with merged PRs.")
    else:
        print("Warning: Placeholders <!-- MERGED_PRS_START --> and <!-- MERGED_PRS_END --> not found in README.md.")

if __name__ == "__main__":
    print("Fetching merged PRs...")
    prs = fetch_merged_prs()
    print(f"Fetched {len(prs)} merged PRs.")
    formatted = format_prs(prs)
    update_readme(formatted)
