#!/usr/bin/env python3
"""arXiv digest end-to-end: fetch -> format -> deliver -> save."""

import subprocess
import sys
import os
import json
import tempfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
FETCH_SCRIPT = os.path.join(SCRIPT_DIR, "fetch_papers.py")
DELIVER_SCRIPT = os.path.join(SCRIPT_DIR, "deliver_wechat.py")


def run_cmd(cmd_list, stdin_text=None):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd_list,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=WORKSPACE,
            env=env,
            encoding="utf-8",
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout after 120s"
    except Exception as e:
        return -1, "", str(e)


def main():
    # Step 1: Fetch papers
    code, stdout, stderr = run_cmd([sys.executable, FETCH_SCRIPT])
    if code != 0 or not stdout.strip():
        print(f"Fetch failed: {stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        print(f"Invalid JSON from fetch: {stdout[:500]}", file=sys.stderr)
        sys.exit(1)

    if data.get("total_fetched", 0) == 0:
        print("No new papers today, skipping digest.")
        sys.exit(0)

    # Step 2: Format digest
    today = datetime.now(timezone.utc).strftime("%Y年%m月%d日")
    top = data.get("top_paper", {})
    additional = data.get("additional_papers", [])

    digest_lines = [
        "arXiv AI/ML 今日速递",
        today,
        "",
        f"论文总数：{data['total_fetched']} 篇",
        "涵盖：cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML",
        "",
        "---",
        "### 深度解读",
    ]

    if top:
        authors = top.get("authors", [])
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += " 等"
        digest_lines += [
            f"#### {top.get('title', 'N/A')}",
            f"**作者**：{author_str}",
            f"**领域**：{', '.join(top.get('categories', []))}",
            f"**链接**：{top.get('link', '')}",
            f"**摘要**：{top.get('abstract', 'N/A')[:400]}",
        ]

    digest_lines += [
        "",
        "---",
        "### 更多值得关注",
    ]

    for p in additional:
        title = p.get("title", "N/A")
        abstract = p.get("abstract", "")[:150]
        link = p.get("link", "")
        digest_lines.append(f"- **{title}** — {abstract} [链接]({link})")

    digest_lines += [
        "",
        "---",
        "数据来源：arxiv.org RSS feeds",
    ]

    digest = "\n".join(digest_lines)

    # Step 3: Save to memory
    os.makedirs(MEMORY_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    memory_path = os.path.join(MEMORY_DIR, f"arxiv-digest-{date_str}.md")
    with open(memory_path, "w", encoding="utf-8") as f:
        f.write(digest)
    print(f"Saved: {memory_path}")

    # Step 4: Deliver to WeChat
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False
    ) as tf:
        tf.write(digest)
        tmp_path = tf.name
    try:
        code, stdout, stderr = run_cmd(
            [sys.executable, DELIVER_SCRIPT, "--file", tmp_path]
        )
        if code == 0:
            print("Delivered to WeChat OK")
        else:
            print(f"Delivery failed (saved to file): {stderr}", file=sys.stderr)
    finally:
        os.unlink(tmp_path)

    # Summary
    print(f"Total papers: {data['total_fetched']}")
    if top:
        print(f"Top: {top.get('title', '')[:100]}")
    print(f"Additional: {len(additional)} papers")


if __name__ == "__main__":
    main()
