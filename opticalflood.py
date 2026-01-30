# opticalflood.py
"""
Unified optical flood mapping utilities.

Includes:
  * opticflood_s2: Sentinel-2 pipeline in Earth Engine (server-side).
  * opticflood_sk_local: SkySat pipeline fully local (no EE assets).

Assumptions:
  - Your EE-based helpers live in the Colab runtime and are importable:
      from upload import load_s2_collection, get_permanent_water
      from date_utilize import get_date_ranges
      from filter import mask_clouds, remove_small_area   # EE variant
      from threshold import classify_kmeans               # EE variant
      from mosaic import mosaic_s2
      from rename import add_layer_name

  - For the local SkySat path, you also have NumPy-based helpers
    named classify_kmeans and remove_small_area, OR you will pass
    callable overrides via the function parameters.

Author: you + a bit of tidy glue ✨
"""

# -----------------------
# Common / EE side imports
# -----------------------
import os
from typing import Callable, Dict, List, Optional

import ee

# EE helper modules (you already have these in your Colab dir)
from upload import load_s2_collection, get_permanent_water
from date_utilize import get_date_ranges
from filter import mask_clouds, remove_small_area  # EE-based version
from threshold import classify_kmeans              # EE-based version
from mosaic import mosaic_s2
from rename import add_layer_name

# -----------------------
# Local (raster) imports
# -----------------------
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.enums import Resampling


# =========================================================
# Small guard to ensure EE is initialized when S2 is used
# =========================================================
def _ensure_ee_initialized():
    try:
        # Tries a trivial server-side op; if not initialized it will throw
        ee.Number(1).getInfo()
    except Exception:
        ee.Initialize()


# =========================================================
# SENTINEL-2: Earth Engine pipeline (server-side)
# =========================================================
def opticflood_s2(
    aoi: ee.Geometry,
    flood_event_date: str,
    lag: int,
    cloud_threshold: int = 60,
    min_area: int = 10000,
    use_reference_for_permwater: bool = True,
    add_metadata: Optional[Dict[str, str]] = None,
) -> ee.ImageCollection:
    """
    Sentinel-2 flood mapping using your existing EE helpers:
      1) date ranges
      2) load S2 collection (cloud-threshold filtered)
      3) compute NDWI + cloud mask (mask_clouds returns 1=cloud, 0=clear)
      4) mosaic by date (mosaic_s2)
      5) KMeans classification (classify_kmeans) -> expected 1=flood, 0=dry
      6) remove permanent water + clouds (mask them out)
      7) remove small patches (remove_small_area)
      8) tag fields + layer_name (add_layer_name)

    Returns:
      ee.ImageCollection with a single band 'depth' (1=flood) and masked non-flood.
    """
    _ensure_ee_initialized()

    # 1) Dates
    post_start_date, post_end_date, ref_start_date, ref_end_date = get_date_ranges(
        flood_event_date, lag
    )

    # 2) Load S2 + permanent water
    s2 = load_s2_collection(aoi, post_start_date, post_end_date, cloud_threshold)

    if use_reference_for_permwater:
        permanent_water = get_permanent_water(ref_start_date)  # or (ref_start, ref_end) if supported
    else:
        permanent_water = get_permanent_water(post_start_date)

    # 3) Prepare NDWI + cloud mask
    def _prepare(img):
        cloud_mask_img = mask_clouds(img)  # 1=cloud, 0=clear
        ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")
        return ndwi.addBands(cloud_mask_img).copyProperties(img, img.propertyNames())

    ndwi_collection = s2.map(_prepare)

    # 4) Mosaic by date (expects 'NDWI' and 'cloud_mask' in each image)
    mosaicked = mosaic_s2(ndwi_collection, aoi)

    # 5) Classify + handle clouds & permanent water
    def _classify_and_mask(img: ee.Image):
        ndwi = img.select("NDWI")
        cloud_mask_img = img.select("cloud_mask")  # 1=cloud, 0=clear

        # Your EE helper: expects an Image + geometry; returns labeled image (1=flood, 0=dry)
        classified = classify_kmeans(ndwi, aoi).rename("depth")

        # Keep only flood (binary)
        flood = classified.eq(1)

        # Mask out permanent water entirely (unknown)
        flood = flood.where(permanent_water.eq(1), 0)

        # Mask out clouds (unknown)
        flood = flood.where(cloud_mask_img.eq(1), 0)

        cleaned = flood.updateMask(flood.eq(1)).rename("depth")
        cleaned = cleaned.set("system:time_start", img.get("system:time_start"))
        return cleaned

    flood_ic = mosaicked.map(_classify_and_mask)

    # 6) Remove small patches
    flood_ic = remove_small_area(flood_ic, aoi, min_area)

    # 7) Add metadata and layer names
    def _tag(img: ee.Image):
        meta = {"source": "S2", "sensor": "Sentinel-2", "algorithm": "kmeans_ndwi_v1"}
        if add_metadata:
            meta.update(add_metadata)
        return img.set(meta)

    flood_ic = flood_ic.map(_tag)
    final_collection = add_layer_name(flood_ic)
    return final_collection




    if not outputs:
        raise ValueError(f"No GeoTIFFs found in {input_dir}")

    return outputs
