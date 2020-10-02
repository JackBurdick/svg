import fontforge
from glyph_to_sfd import GlyphWriter
import pickle


binary_fp = "3789193592913674666"  # provided by
f_name = "FG_Jeff.ttf"


def to_file(obj, name):
    with open(name + ".pkl", "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


pd = {}
F = fontforge.open(f_name)
gwriter = GlyphWriter()
cur_id = 0
for name in F:
    cur_id += 1
    uni = F[name].unicode
    width = F[name].width
    vwidth = F[name].vwidth
    gwriter.set_glyph(F[name])
    sfd = gwriter.dumps()

    pd["uni"] = uni
    pd["width"] = width
    pd["vwidth"] = vwidth
    pd["sfd"] = sfd
    pd["id"] = str(cur_id)
    pd["binary_fp"] = binary_fp

    # writing out to pickle such that I can use two seperate python environments
    # because using fontforge on ubuntu is not straight forward
    to_file(pd, "trial")
