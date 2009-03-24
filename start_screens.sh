#!/bin/sh
screen -d -m -S pyscreen0
screen -d -m -S pyscreen1
screen -d -m -S pyscreen2
screen -d -m -S pyscreen3

screen -S pyscreen0 -X stuff clisp
screen -S pyscreen1 -X stuff clisp
screen -S pyscreen2 -X stuff clisp
screen -S pyscreen3 -X stuff clisp
