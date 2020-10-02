"""
Copyright Mozbug 2009. All right reserved.

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#      
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#      
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


source: http://fontforge.10959.n7.nabble.com/Python-glyph-gt-sfd-formatter-module-td9734.html
# this is a partial copy, and may contain minor modifications
"""
FLOATPRECISION = 3

import sys
import fontforge


def float2str(float_list, prec=FLOATPRECISION):
    """Convert a list of float to a list of string with tailing '.0' strippped."""
    fmt = "%%.%df" % prec
    txt = [(fmt % x).rstrip("0").rstrip(".") for x in float_list]
    return tuple(txt)


class GlyphWriter:
    """Write out glyph info in the sfd format."""

    def __init__(self, glyph=None):
        self.glyph = glyph

    def set_glyph(self, glyph):
        """Set the glyph to write."""
        self.glyph = glyph

    def dumps(self):
        """Dump the glyph info as a sfd string."""
        if not self.glyph:
            return
        txt = []
        txt.append(self.prelude())
        ltxt = self.layers()
        if ltxt:
            txt.append(ltxt)
        txt.append(self.postlude())
        txt.append("")  # extra linefeed
        return "\n".join(txt)

    def prelude(self):
        """Return prelude of the glyph as a string."""
        glyph = self.glyph
        font = glyph.font
        gclasses = {
            "automatic": 0,
            "noclass": 1,
            "baseglyph": 2,
            "baseligature": 3,
            "mark": 4,
            "component": 5,
        }
        gdict = {
            "StartChar": glyph.glyphname,
            "Encoding": "%s %s %s" % (glyph.encoding, glyph.unicode, glyph.originalgid),
            "Width": str(glyph.width),
        }
        txt = []
        for key in ["StartChar", "Encoding", "Width"]:
            txt.append("%s: %s" % (key, gdict[key]))
        if glyph.font.hasvmetrics:
            txt.append("VWidth: %s" % glyph.vwidth)

        if glyph.glyphclass != "automatic":
            txt.append("GlyphClass: %s" % gclasses[glyph.glyphclass])
        flags = " "
        if glyph.width >= 0:
            flags += "W"
        txt.append("Flags:%s" % flags.rstrip())

        def flatten(x):
            """flatten(sequence) -> list"""
            result = []
            for el in x:
                if hasattr(el, "__iter__") and not isinstance(el, basestring):
                    result.extend(flatten(el))
                else:
                    result.append(el)
            return result

        if glyph.hhints:
            hvalue = flatten(glyph.hhints)
            hvalue = float2str(hvalue)
            txt.append("HStem: %s" % " ".join(hvalue))
        if glyph.vhints:
            hvalue = flatten(glyph.vhints)
            hvalue = float2str(hvalue)
            txt.append("VStem: %s" % " ".join(hvalue))
        if glyph.dhints:
            hvalue = flatten(glyph.dhints)
            hvalue = float2str(hvalue)
            txt.append("DStem: %s" % " ".join(hvalue))

        # truetype instructions
        ttxt = self.ttinstrs()
        if ttxt:
            txt.append(ttxt)

        if glyph.altuni:
            atxt = []
            for alt in glyph.altuni:
                selector = alt[1] if alt[1] >= 0 else 0xFFFFFFFF
                atxt.append("%06x.%06x.%x" % (alt[0], selector, alt[2]))
            txt.append(" ".join(atxt))

        # misc
        if glyph.persistent:
            import pickle

            txt.append("PickledData: %s" % pickle.dumps(glyph.persistent))

        # extra info for the glyph. Will be ignored by fontforge
        txt.append("Comment: EM=%s" % font.em)
        txt.append("Comment: FontName=%s" % font.fontname.decode("utf8").encode("utf7"))
        txt.append("Comment: Version=%s" % font.version)

        if glyph.comment:
            cmt = glyph.comment.decode("utf-8").encode("utf-7")
            txt.append("Comment: %s" % cmt)
        else:
            txt.append("Comment:")

        if glyph.color and glyph.color >= 0:
            txt.append("Color: %06x" % glyph.color)
        if glyph.unlinkRmOvrlpSave:
            txt.append("UnlinkRmOvrlpSave: %s" % glyph.unlinkRmOvrlpSave)

        return "\n".join(txt)

    def postlude(self):
        txt = []
        txt.append("EndChar")
        return "\n".join(txt)

    def ttinstrs(self):
        """Return truetype instruction info of the font."""
        txt = []
        glyph = self.glyph
        if glyph.ttinstrs:
            instrs = fontforge.unParseTTInstrs(glyph.ttinstrs).strip()
            txt.append("TtInstrs:")
            txt.append(instrs)
            txt.append("EndTTInstrs")

        if glyph.anchorPoints:
            for pts in glyph.anchorPoints:
                if len(pts) == 5:
                    lig = pts[4]
                else:
                    lig = 0
                coord = "%s %s" % float2str(pts[2:4])
                aname = pts[0].decode("utf8").encode("utf-7")
                atype = pts[1]
                if atype == "base":
                    atype = "basechar"
                elif atype == "ligature":
                    atype = "baselig"
                atxt = 'AnchorPoint: "%s" %s %s %s' % (aname, coord, atype, lig)
                txt.append(atxt)
        return "\n".join(txt)

    def contour(self, contour, point_start=0):
        """Return one contour as string."""
        txt = []
        oncurve = 0
        offcurve = 0
        pts = []

        # Append the first point to closed contour
        contr0 = [p for p in contour]
        if contour.closed:
            contr0.append(contr0[0])
        plen = len(contr0)
        for i in range(plen):
            p = contr0[i]
            if p.on_curve:
                oncurve += 1
            else:
                offcurve += 1

            # count point, last point is point 0 for closed contour
            myidx = i
            if myidx == plen - 1 and contour.closed:
                myidx = 0

            next_ctrl = -1
            if myidx + 1 < plen and not contr0[myidx + 1].on_curve:
                next_ctrl = myidx + 1

            prev_ctrl = -1
            if myidx != 0:
                if not contr0[myidx - 1].on_curve:
                    prev_ctrl = myidx - 1
            elif contour.closed:  # open contour, prev_ctrl of 0 is always -1
                if not contr0[plen - 2].on_curve:
                    prev_ctrl = plen - 2

            if next_ctrl != -1 and prev_ctrl != -1:
                flag = 0x0
            elif next_ctrl == -1 and prev_ctrl == -1:
                flag = 0x1
            else:
                flag = 0x2
            if p.selected:
                # FIXME: some point could be corner here.
                flag = flag | 0x4

            if contour.is_quadratic:
                if next_ctrl >= 0:
                    next_ctrl += point_start
                idx = "%s,%s" % (myidx + point_start, next_ctrl)

                if not txt:
                    coord = "%s %s" % (float2str([p.x, p.y]))
                    txt.append("%s m %s,%s" % (coord, flag, idx))
                    pts = []
                elif oncurve == 2 and offcurve == 0:
                    coord = "%s %s" % (float2str((p.x, p.y)))
                    txt.append(" %s l %s,%s" % (coord, flag, idx))
                    oncurve = 1
                    offcurve = 0
                    pts = []
                elif oncurve == 2 and offcurve == 1:
                    coord = "%s %s %s %s %s %s" % (
                        float2str(
                            (
                                pts[1].x,
                                pts[1].y,
                                pts[1].x,
                                pts[1].y,
                                p.x,
                                p.y,
                            )
                        )
                    )
                    txt.append(" %s c %s,%s" % (coord, flag, idx))
                    oncurve = 1
                    offcurve = 0
                    pts = []
                elif offcurve == 2:
                    px = (pts[1].x + p.x) / 2.0
                    py = (pts[1].y + p.y) / 2.0
                    coord = "%s %s %s %s %s %s" % (
                        float2str(
                            (
                                pts[1].x,
                                pts[1].y,
                                pts[1].x,
                                pts[1].y,
                                px,
                                py,
                            )
                        )
                    )
                    idx = "-1,%s" % (myidx + point_start)  # I'm the ctrl point
                    txt.append(" %s c 128,%s" % (coord, idx))
                    oncurve = 1
                    offcurve = 1
                    pts = [None]  # really don't need pts[0]
            else:
                if not txt:
                    coord = "%s %s" % (float2str([p.x, p.y]))
                    txt.append("%s m %s" % (coord, flag))
                    pts = []
                elif oncurve == 2 and offcurve == 0:
                    coord = "%s %s" % (float2str([p.x, p.y]))
                    txt.append(" %s l %s" % (coord, flag))
                    oncurve = 1
                    offcurve = 0
                    pts = []
                elif oncurve == 2 and offcurve == 2:
                    coord = "%s %s %s %s %s %s" % (
                        float2str(
                            (
                                pts[1].x,
                                pts[1].y,
                                pts[2].x,
                                pts[2].y,
                                p.x,
                                p.y,
                            )
                        )
                    )
                    txt.append(" %s c %s" % (coord, flag))
                    oncurve = 1
                    offcurve = 0
                    pts = []
            pts.append(p)
        return "\n".join(txt)

    def layer(self, layer):
        """Return one layer as string."""
        txt = []
        ptn = 0
        if len(layer) > 0:
            txt.append("SplineSet")
            for contour in layer:
                ctxt = self.contour(contour, ptn)
                txt.append(ctxt)
                ptn += len(contour)
            txt.append("EndSplineSet")
        return "\n".join(txt)

    def layers(self):
        """Return all the layers as string."""
        layers = self.glyph.layers
        lrefs = self.glyph.layerrefs
        txt = []
        txt.append("LayerCount: %s" % self.glyph.layer_cnt)

        ltxt = []
        tmp = self.layer(layers[1])
        if tmp:
            ltxt.append(tmp)
        tmp = self.reference(lrefs[1])
        if tmp:
            ltxt.append(tmp)
        if ltxt:
            txt.append("Fore")
            txt.append("\n".join(ltxt))

        ltxt = []
        tmp = self.layer(layers[0])
        if tmp:
            ltxt.append(tmp)
        tmp = self.reference(lrefs[0])
        if tmp:
            ltxt.append(tmp)
        if ltxt:
            txt.append("Back")
            txt.append("\n".join(ltxt))

        for i in range(self.glyph.layer_cnt - 2):
            i += 2
            layer = layers[i]
            ltxt = []
            tmp = self.layer(layer)
            if tmp:
                ltxt.append(tmp)
            tmp = self.reference(lrefs[i])
            if tmp:
                ltxt.append(tmp)
            if ltxt:
                txt.append("Layer: %s" % i)
                txt.append("\n".join(ltxt))
        return "\n".join(txt)

    def reference(self, refs):
        """Write out list of references as string.
        refs: result of glyph.layerrefs[n]
        """
        txt = []
        for ref in refs:
            coord = " ".join(float2str(ref[1]))
            g = self.glyph.font[ref[0]]
            txt.append("Refer: %s %s N %s 0" % (g.originalgid, g.unicode, coord))
        return "\n".join(txt)


def export_sfd(junk, obj):
    """Export Glyph SFD menu function."""
    ext = ".glyph"
    if isinstance(obj, fontforge.glyph):
        glyphs = [obj]
    else:
        glyphs = []
        for g in obj.selection:
            glyphs.append(obj[g])
    if not glyphs:
        return
    prefix = glyphs[0].font.fontname
    if len(glyphs) == 1:
        surfix = glyphs[0].glyphname
    else:
        glyphs.sort(lambda g1, g2: (g1.originalgid - g2.originalgid))
        name1 = glyphs[0].glyphname.replace(".", "_")
        name2 = glyphs[-1].glyphname.replace(".", "_")
        surfix = "%s-%s" % (name1, name2)
    defname = "%s-%s%s" % (prefix, surfix, ext)
    ofname = fontforge.saveFilename("Save glyph to sfd format", defname, "*.glyph")
    if not ofname:
        return
    ofd = open(ofname, "w")
    writer = GlyphWriter()
    for glyph in glyphs:
        writer.set_glyph(glyph)
        ofd.write(writer.dumps())
        ofd.write("\n")


def register_menu():
    fontforge.registerMenuItem(
        export_sfd, None, None, ("Glyph", "Font"), None, "Export Glyph SFD..."
    )
