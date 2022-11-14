#!/usr/bin/env zsh

flake8 backgammon
flake8 tests

mypy backgammon
mypy tests

pytest
