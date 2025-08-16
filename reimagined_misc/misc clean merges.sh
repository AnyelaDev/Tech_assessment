#!/bin/bash
# Usage: ./git-squash-merge.sh <feature-branch> <base-branch>
# Example: ./git-squash-merge.sh AAA BBB

set -e  # exit on error

FEATURE=$1
BASE=$2

if [ -z "$FEATURE" ] || [ -z "$BASE" ]; then
  echo "Usage: $0 <feature-branch> <base-branch>"
  exit 1
fi

echo "Fetching latest changes..."
git fetch origin

echo "Checking out base branch: $BASE"
git checkout $BASE
git pull origin $BASE

echo "Squash merging $FEATURE into $BASE..."
git merge --squash $FEATURE

echo "Creating squashed commit..."
git commit -m "Squashed merge of branch '$FEATURE' into '$BASE'"

echo "Creating dummy merge commit with two parents..."
git merge -s ours --no-commit $FEATURE
git commit -m "Merge branch '$FEATURE' into '$BASE' (squash merge with preserved parentage)"

echo "Pushing result to origin..."
git push origin $BASE

echo "Done! Branch $FEATURE has been squash-merged into $BASE with two parents."
