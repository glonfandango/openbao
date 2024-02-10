#!/usr/bin/env python3
# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

import subprocess
import sys
import os

def check_staged():
    """Check if there are staged Go files and silently succeed if none."""
    try:
        # Get the list of staged .go files
        staged = subprocess.check_output(
            ['git', 'diff', '--name-only', '--cached', '--', '*.go'],
            stderr=subprocess.STDOUT  # Capture stderr in case of no changes
        ).decode().strip()

        if staged:
            staged_list = [file for file in staged.split('\n') if 'vendor/' not in file and not file.startswith('vendor/')]
            return staged_list
        else:
            return list()

    except subprocess.CalledProcessError as e:
        print(f"Error checking staged Go files: {e.output.decode()}")
        return e.returncode



def run_gofumpt(files, batch_size=100):
    """Run gofumpt on a list of files in batches."""
    files_needing_format = []
    
    # Process the list of files in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        try:
            result = subprocess.check_output(['go', 'run', 'mvdan.cc/gofumpt', '-l'] + batch).decode().strip()
            if result:
                files_needing_format.extend(result.split('\n'))
        except subprocess.CalledProcessError as e:
            print(f"Error running gofumpt: {e.output.decode()}")
            sys.exit(1)
    return files_needing_format

def find_go_files():
    go_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.go') and not file.endswith('pb.go'):
                go_files.append(os.path.join(root, file))
    return go_files

def main():
    files_to_check = check_staged()
    if files_to_check:
        print("Checking changed files...")
    else:
        print("No Go files to check.")
        return

    gofmt_files = run_gofumpt(files_to_check)

    if gofmt_files:
        print('gofumpt needs running on the following files:')
        print(gofmt_files)
        print("You can use the command: `make fmt` to reformat code.")
        sys.exit(1)
    else:
        print("All files comply with gofumpt requirements.")

main()