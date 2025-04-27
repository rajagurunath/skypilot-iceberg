# /scripts/1_reconstruct_git_files.py

import subprocess
import os
import csv
from pathlib import Path
from datetime import datetime
import sys
import argparse
sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib.supabase_client import SupabaseClient

supabase = SupabaseClient()

# Git functions
def get_tracked_files(git_repo_path):
    result = subprocess.run(['git', 'ls-files','catalogs/v6'], cwd=git_repo_path, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip().split('\n')

def get_commits_for_file(git_repo_path, file_path):
    result = subprocess.run(
        ['git', 'log', '--reverse', '--pretty=format:%H|%ad', '--date=iso', '--', file_path],
        cwd=git_repo_path,
        stdout=subprocess.PIPE, text=True
    )
    lines = result.stdout.strip().split('\n')
    return [tuple(line.split('|')) for line in lines if line]

def get_file_content_at_commit(git_repo_path, commit_hash, file_path):
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit_hash}:{file_path}'],
            cwd=git_repo_path,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def get_commit_metadata(git_repo_path, commit_hash):
    try:
        result = subprocess.run(
            ['git', 'show', '-s', '--format=%an|%ad|%s', '--date=iso', commit_hash],
            cwd=git_repo_path,
            stdout=subprocess.PIPE, text=True
        )
        author, date, message = result.stdout.strip().split('|', 2)
        return author, date, message
    except Exception as e:
        print(f"Failed to get metadata for commit {commit_hash}: {e}")
        return None, None, None

def reconstruct_history(git_repo_path, output_csv='git_file_history.csv', resume=True):
    # Get the last checkpoint
    checkpoint = supabase.get_checkpoint() if resume else None
    print(f"🔎 Last checkpoint: {checkpoint}")

    all_files = get_tracked_files(git_repo_path)

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['commit', 'author', 'date', 'message', 'file', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        latest_commit = None
        latest_date = None

        for file_path in all_files:
            if 'vms' not in file_path:
                continue
            print(f"🔎 Processing file: {file_path}")
            commits = get_commits_for_file(git_repo_path, file_path)
            for commit, commit_date in commits:
                if not commit:
                    continue

                # Skip already processed commits
                if checkpoint and commit <= checkpoint['last_commit']:
                    continue

                content = get_file_content_at_commit(git_repo_path, commit, file_path)
                author, date, message = get_commit_metadata(git_repo_path, commit)

                if content is not None:
                    writer.writerow({
                        'commit': commit,
                        'author': author,
                        'date': date,
                        'message': message,
                        'file': file_path,
                        'content': content.strip()
                    })

                # track the latest commit seen
                latest_commit = commit
                latest_date = commit_date

        if latest_commit:
            supabase.save_checkpoint(latest_commit, latest_date)

    print(f"✅ Done. File history written to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconstruct Git files into CSV.")
    parser.add_argument("--repo", type=str, required=True, help="Local path to the Git repository", default="/Users/gurunathlunkupalivenugopal/ionet/oss/skypilot-catalog")
    parser.add_argument("--output", type=str, default="git_file_history.csv", help="Output CSV filename")
    parser.add_argument("--resume", default=True, action="store_true", help="Resume from last checkpoint")
    args = parser.parse_args()

    os.chdir(Path(__file__).parent.parent)  # move to repo root
    reconstruct_history(git_repo_path=args.repo, output_csv=args.output, resume=args.resume)