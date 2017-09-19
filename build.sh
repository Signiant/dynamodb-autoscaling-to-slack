#!/bin/bash

mkdir -p dist
cp -f lambda/dynamodb-as-notify-slack.py ./dist/dynamodb-as-notify-slack.py
cd dist
zip -r dynamodb-as-notify-slack .
cd ..
