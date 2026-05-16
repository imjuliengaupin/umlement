Output ../images/demo.gif

Set Shell "bash"
Set WindowBar Colorful
Set FontSize 14
Set Width 860
Set Height 520
Set Padding 20
Set BorderRadius 12
Set TypingSpeed 35ms
Set Framerate 30

Require "python3"
Require "vhs"

Type "cd /Users/path/to/umlement" Enter
Sleep 500ms
Type "source .venv/bin/activate" Enter
Sleep 500ms
Type "python umlement.py demo/sample_project --recursive --format svg --progress" Enter
Sleep 8s
