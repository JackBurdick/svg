import fontforge
from glyph_to_sfd import GlyphWriter

# {'uni': int64,  # unicode value of this glyph
#  'width': int64,  # width of this glyph's viewport (provided by fontforge)
#  'vwidth': int64,  # vertical width of this glyph's viewport
#  'sfd': binary/str,  # glyph, converted to .sfd format, with a single SplineSet
#  'id': binary/str,  # id of this glyph
#  'binary_fp': binary/str}  # font identifier (provided in glyphazzn_urls.txt)

binary_fp = "3789193592913674666"
f_name = "FG_Jeff.ttf"


F = fontforge.open(f_name)
gwriter = GlyphWriter()
for name in F:
    uni = F[name].unicode
    width = F[name].width
    vwidth = F[name].vwidth
    gwriter.set_glyph(F[name])
    sfd = gwriter.dumps()
