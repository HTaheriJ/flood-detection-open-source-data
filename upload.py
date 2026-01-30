import ee

# -----------------------------
# Sentinel-2 Collection Loader
# -----------------------------
def load_s2_collection(aoi, start_date, end_date, cloud_threshold=100):
    """
    Load Sentinel-2 L2A image collection for a given area and date range, filtered by cloud cover.

    Args:
        aoi (ee.Geometry): Area of interest to clip images to.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        cloud_threshold (int): Max allowed CLOUDY_PIXEL_PERCENTAGE (default 20).

    Returns:
        ee.ImageCollection: Filtered and clipped image collection.
    """
    bands = ['B3', 'B8', 'SCL']  # Green, NIR, and Scene Classification Layer

    def clip(img):
        return img.clip(aoi).copyProperties(img, img.propertyNames())

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
        .select(bands)
        .map(clip)
    )

    return collection


# -----------------------------
# Permanent Water Mask (JRC)
# -----------------------------
def get_permanent_water(reference_date):
    """
    Generate a mask of permanent water bodies from the JRC Global Surface Water dataset.

    Args:
        reference_date (str): Reference date in 'YYYY-MM-DD' format; looks back 5 years from this date.

    Returns:
        ee.Image: A binary mask where 1 indicates permanent water (present at least once in the last 5 years).
    """
    water_history = (
        ee.ImageCollection("JRC/GSW1_4/YearlyHistory")
        .filterDate("1985-01-01", reference_date)
        .limit(5, "system:time_start", False)
        .map(lambda img: img.select("waterClass").eq(3))
        .sum()
        .unmask(0)
        .gt(0)
    )

    return water_history.rename("permanent_water")
