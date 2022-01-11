#!/bin/bash

dir="$1"
cd "$dir"

git init -b test_main

echo 'Hello, world!' >a.txt
git add a.txt
git commit -m '1st commit'

echo 'Hey there!' >b.txt
git add b.txt
git commit -m '2nd commit'

echo 'Come here often?' >>a.txt
git add a.txt
git commit -m '3rd commit'

git rm b.txt
git commit -m '4th commit'
