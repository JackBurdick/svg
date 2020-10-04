import fontforge
from glyph_to_sfd import GlyphWriter
import pickle
import urllib
import os
import time

DS_SIZE = 10
URL_LIST_IN = "./glyphazzn_urls.txt"
TTF_OUT_DIR = "./font_ttfs"
TTF_OUT_TEMPLATE = TTF_OUT_DIR + "/{}.ttf"
GLYPH_OUT_TEMPLATE = "./glyph_out/{}"


# download
with open(URL_LIST_IN) as fp:
    for i, l in enumerate(fp):
        f_name, split_name, url = l.split(",")
        save_path = TTF_OUT_TEMPLATE.format(f_name)
        if not os.path.isfile(save_path):
            try:
                urllib.urlretrieve(url, save_path)
                print("downloading: {}".format(f_name))
            except IOError:
                print("passing: {}".format(url))
                pass
            time.sleep(1)
        if i > DS_SIZE:
            break


def _write_pickle(obj, name):
    with open(name + ".pkl", "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def parse_F(F):
    cur_pd = {}
    gwriter = GlyphWriter()

    cur_id = 0
    for name in F:
        cur_id += 1
        uni = F[name].unicode
        width = F[name].width
        vwidth = F[name].vwidth
        gwriter.set_glyph(F[name])
        try:
            sfd = gwriter.dumps()
        except IndexError:
            return

        cur_pd["uni"] = uni
        cur_pd["width"] = width
        cur_pd["vwidth"] = vwidth
        cur_pd["sfd"] = sfd
        cur_pd["id"] = str(cur_id)
        cur_pd["binary_fp"] = binary_fp

        # writing out to pickle such that I can use two separate python environments
        # because using fontforge on ubuntu is not straight forward
        _write_pickle(cur_pd, GLYPH_OUT_TEMPLATE.format(f_name))


# parse to object
for f_name in os.listdir(TTF_OUT_DIR):
    binary_fp = f_name.split(".")[0]
    try:
        F = fontforge.open(os.path.join(TTF_OUT_DIR, f_name))
        parse_F(F)
    except EnvironmentError:
        print("skipping: {}".format(f_name))
        pass
