import json
import os
import zopfli

delete_frame_props = ["rotated", "trimmed",
                      "sourceSize", "filename", "spriteSourceSize"]
delete_meta_props = ["app", "version", "image", "format", "scale", "size"]


def filter_props(d: dict, delete_props: list[str]):
    return dict(filter(lambda a: a[0] not in delete_props, d.items()))


png = zopfli.ZopfliPNG()
for dirpath, _, files in os.walk("assets/sprite/"):
    paths = list(map(lambda p: os.path.join(dirpath, p), files))

    for f in filter(lambda f: f.endswith(".png"), paths):
        with open(f, "rb") as file:
            png_bytes = png.optimize(file.read())
        with open(f, "wb") as file:
            file.write(png_bytes)

    for f in filter(lambda f: f.endswith(".json"), paths):
        with open(f, "r") as file:
            data: dict = json.load(file)

        data["frames"] = list(map(lambda a: filter_props(
            a, delete_frame_props), data["frames"]))
        meta = data["meta"] = filter_props(
            data["meta"], delete_meta_props)
        meta["frameTags"] = list(map(lambda a: filter_props(
            a, ["direction"]), meta["frameTags"]))

        with open(f, "w") as file:
            json.dump(data, file, separators=(",", ":"))
