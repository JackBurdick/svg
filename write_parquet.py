import pickle
import apache_beam as beam
import pyarrow
import os


def load_obj(name):
    with open(f"{name}", "rb") as f:
        return pickle.load(f)


# template = {
#     "uni": pyarrow.int64(),  # unicode value of this glyph
#     "width": pyarrow.int64(),  # width of this glyph's viewport (provided by fontforge)
#     "vwidth": pyarrow.int64(),  # vertical width of this glyph's viewport
#     "sfd": pyarrow.string(),  # glyph, converted to .sfd format, with a single SplineSet
#     "id": pyarrow.string(),  # id of this glyph
#     "binary_fp": pyarrow.string(),
# } [(t[0], t[1]) for t in template.items()]


GLYPH_OUT_DIR = "./glyph_out"

dl = []  # load_obj("trial")
for f_name in os.listdir(GLYPH_OUT_DIR):
    dl.append(load_obj(os.path.join(GLYPH_OUT_DIR, f_name)))

with beam.Pipeline() as p:
    records = p | "Read" >> beam.Create(dl)
    _ = records | "Write" >> beam.io.WriteToParquet(
        "trial/trial_out",
        pyarrow.schema(
            [
                ("uni", pyarrow.int64()),
                ("width", pyarrow.int64()),
                ("vwidth", pyarrow.int64()),
                ("sfd", pyarrow.string()),
                ("id", pyarrow.string()),
                ("binary_fp", pyarrow.string()),
            ]
        ),
    )