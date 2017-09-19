#!/bin/bash

echo "Creating dist folder"
mkdir -p dist
echo "Copying lambda code into dist folder"
cp -f lambda/dynamodb-as-notify-slack.py ./dist/dynamodb-as-notify-slack.py
cd dist
echo "Creating lambda zip"
zip -r dynamodb-as-notify-slack .
cd ..
echo "DONE"
