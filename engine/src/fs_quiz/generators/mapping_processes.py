"""Domain: mapping-processes-and-methods (14-21 FS questions).

6 generators: photo scale, contour interpolation, UTM zones, raster vs vector,
LiDAR products, State Plane projections. Original content throughout.
"""
from __future__ import annotations

import math

from fs_quiz.generators.survey_computations import _fmt, _mcq
from fs_quiz.registry import register
from fs_quiz.schema import SCHEMA_VERSION, Question

DOMAIN = "mapping-processes-and-methods"


def _mk(rng, qid, topic, difficulty, stem, choices, answer_index,
        explanation, parameters):
    return Question(
        qid=qid, schema_version=SCHEMA_VERSION, domain=DOMAIN, topic=topic,
        difficulty=difficulty, stem=stem, choices=choices,
        answer_index=answer_index, explanation=explanation,
        parameters=parameters, seed=hash(qid) % (2 ** 31),
    )


# ------------------------------------------------------------- photo scale
@register(DOMAIN, "photo-scale")
def gen_photo_scale(rng, qid):
    f_in = rng.choice([6.0, 8.25, 12.0])
    H_ft = rng.uniform(2000, 6000)
    denom = H_ft * 12.0 / f_in
    stem = (f"An aerial photo is taken with a {_fmt(f_in, 2)}-inch focal-length "
            f"camera from {_fmt(H_ft, 0)} ft above the terrain. What is the "
            f"photo scale?")
    correct = f"1:{denom:,.0f}"
    distractors = [
        f"1:{H_ft / f_in:,.0f}",        # forgot inches-to-feet
        f"1:{H_ft * 12.0 * f_in:,.0f}",  # multiplied by f
        f"1:{f_in * 12.0 / H_ft:,.4f}",  # inverted
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Scale = f / H. Convert to common units: {_fmt(H_ft, 0)} ft \u00d7 12 "
            f"= {_fmt(H_ft * 12, 0)} in; {_fmt(H_ft * 12, 0)} / {_fmt(f_in, 2)} "
            f"= {denom:,.0f} \u2192 1:{denom:,.0f}.")
    return _mk(rng, qid, "photo-scale", 2, stem, choices, ai, expl,
               {"f_in": f_in, "H_ft": H_ft})


# ------------------------------------------------------------- contour interpolation
@register(DOMAIN, "contour-interpolation")
def gen_contour(rng, qid):
    e1 = rng.uniform(100, 200)
    e2 = e1 + rng.uniform(4, 9)
    L = rng.uniform(40, 80)
    target = math.floor(e1) + 1
    if target >= e2:
        target = round((e1 + e2) / 2)
    d = (target - e1) / (e2 - e1) * L
    stem = (f"Two spot elevations, {_fmt(e1)} ft and {_fmt(e2)} ft, are "
            f"{_fmt(L, 0)} ft apart. How far from the {_fmt(e1)}-ft point does "
            f"the {target}-ft contour fall?")
    correct = f"{_fmt(d)} ft"
    distractors = [
        f"{_fmt((target - e1))} ft",   # elevation difference used as distance
        f"{_fmt(L)} ft",               # full spacing
        f"{_fmt((math.ceil(e2) - target) / (e2 - e1) * L)} ft",  # wrong contour
    ]
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Linear interpolation: d = ({target} \u2212 {_fmt(e1)}) / "
            f"({_fmt(e2)} \u2212 {_fmt(e1)}) \u00d7 {_fmt(L, 0)} = {_fmt(d)} ft "
            f"from the lower point.")
    return _mk(rng, qid, "contour-interpolation", 2, stem, choices, ai, expl,
               {"e1": e1, "e2": e2, "L": L, "target": target})


# ------------------------------------------------------------- UTM zone
@register(DOMAIN, "utm-zone")
def gen_utm(rng, qid):
    lon = rng.uniform(-125, -66)
    zone = int((lon + 180) // 6) + 1
    stem = (f"A project is centered at longitude {_fmt(lon, 1)}\u00b0. "
            f"What is its UTM zone?")
    correct = f"Zone {zone}"
    cand = [f"Zone {zone - 1}", f"Zone {zone + 1}", f"Zone {int(abs(lon) // 6) + 1}"]
    distractors = list(dict.fromkeys(c for c in cand if c != correct))
    while len(distractors) < 3:
        extra = f"Zone {rng.randint(10, 20)}"
        if extra != correct and extra not in distractors:
            distractors.append(extra)
    choices, ai = _mcq(rng, correct, distractors)
    expl = (f"Zone = floor((lon + 180)/6) + 1 = floor(({_fmt(lon, 1)} + 180)/6) + 1 "
            f"= {zone}. Zones are 6\u00b0 wide starting at 180\u00b0W.")
    return _mk(rng, qid, "utm-zone", 1, stem, choices, ai, expl, {"lon": lon})


# ------------------------------------------------------------- raster vs vector
_RASTER_FACTS = [
    ("a county-wide aerial orthoimage used as a basemap", "Raster data"),
    ("parcel boundary polygons with owner attributes", "Vector data"),
    ("a LiDAR-derived elevation grid", "Raster data"),
    ("road centerlines for network routing", "Vector data"),
]
_RASTER_CHOICES = ["Raster data", "Vector data", "Both equally", "Neither \u2014 it is tabular data"]


@register(DOMAIN, "raster-vector")
def gen_raster_vector(rng, qid):
    facts, correct = rng.choice(_RASTER_FACTS)
    stem = f"A GIS layer holds {facts}. Is this raster or vector data?"
    distractors = [c for c in _RASTER_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = ("Raster = gridded cells (imagery, elevation surfaces). Vector = "
            "discrete points/lines/polygons with attributes (parcels, roads).")
    return _mk(rng, qid, "raster-vector", 1, stem, choices, ai, expl,
               {"correct": correct})


# ------------------------------------------------------------- LiDAR products
_LIDAR_FACTS = [
    ("a bare-earth terrain model for drainage design", "DEM \u2014 bare earth"),
    ("a surface model that includes buildings and tree canopy, for line-of-sight work",
     "DSM \u2014 surface with features"),
    ("a floodplain study needing ground elevations under forest canopy",
     "DEM \u2014 bare earth"),
]
_LIDAR_CHOICES = ["DEM \u2014 bare earth", "DSM \u2014 surface with features",
                  "Hillshade \u2014 visualization only", "Slope map \u2014 derived product"]


@register(DOMAIN, "lidar-products")
def gen_lidar(rng, qid):
    facts, correct = rng.choice(_LIDAR_FACTS)
    stem = f"A project needs {facts}. Which LiDAR product is appropriate?"
    distractors = [c for c in _LIDAR_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = ("DEM = bare-earth terrain (filtered returns). DSM = first-return "
            "surface including buildings and canopy. Pick the product that "
            "matches what you need to measure.")
    return _mk(rng, qid, "lidar-products", 1, stem, choices, ai, expl,
               {"correct": correct})


# ------------------------------------------------------------- State Plane projections
_SP_FACTS = [
    ("spans about 400 miles east-west but only 120 miles north-south",
     "Lambert conformal conic"),
    ("spans about 350 miles north-south but only 100 miles east-west",
     "Transverse Mercator"),
]
_SP_CHOICES = ["Lambert conformal conic", "Transverse Mercator",
               "Azimuthal equidistant", "State Plane uses a single projection in every state"]


@register(DOMAIN, "state-plane-projection")
def gen_sp(rng, qid):
    facts, correct = rng.choice(_SP_FACTS)
    stem = (f"A State Plane zone {facts}. Which projection family does it use?")
    distractors = [c for c in _SP_CHOICES if c != correct]
    choices, ai = _mcq(rng, correct, distractors[:3])
    expl = ("Lambert conformal conic suits east-west zones (minimal distortion "
            "along parallels); transverse Mercator suits north-south zones "
            "(minimal distortion along the central meridian).")
    return _mk(rng, qid, "state-plane-projection", 2, stem, choices, ai, expl,
               {"correct": correct})
