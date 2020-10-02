import pickle
import apache_beam as beam
import pyarrow


def load_obj(name):
    with open(f"{name}.pkl", "rb") as f:
        return pickle.load(f)


# template = {
#     "uni": pyarrow.int64(),  # unicode value of this glyph
#     "width": pyarrow.int64(),  # width of this glyph's viewport (provided by fontforge)
#     "vwidth": pyarrow.int64(),  # vertical width of this glyph's viewport
#     "sfd": pyarrow.string(),  # glyph, converted to .sfd format, with a single SplineSet
#     "id": pyarrow.string(),  # id of this glyph
#     "binary_fp": pyarrow.string(),
# } [(t[0], t[1]) for t in template.items()]


d = load_obj("trial")
with beam.Pipeline() as p:
    records = p | "Read" >> beam.Create(
        [
            d,
        ]
    )
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
print("hi")