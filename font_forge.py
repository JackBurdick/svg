import fontforge

F = fontforge.open("FG_Jeff.ttf")
for name in F:
    print(name)