#!/bin/bash
shopt -s extglob 

mkdir -p dist
pip install slacker -t ./dist
cp -f lambda/dynamodb-as-notify-slack.py ./dist/dynamodb-as-notify-slack.py
pushd .
cd dist
zip -r dynamodb-as-notify-slack .
rm -- !(dynamodb-as-notify-slack.zip)
popd 
