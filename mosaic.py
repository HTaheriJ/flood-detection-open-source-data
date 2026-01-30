import ee
# -----------------------------
# Sentinel-2 Mosaic by Date
# -----------------------------
def mosaic_s2(collection, roi):
    """
    Mosaic Sentinel-2 images by acquisition date using median.
    Keeps only mosaics that fully cover the ROI.

    Args:
        collection (ee.ImageCollection): Sentinel-2 image collection.
        roi (ee.Geometry): Region of interest.

    Returns:
        ee.ImageCollection: One mosaicked image per date (with full ROI coverage).
    """
    def add_date(img):
        date = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd')
        return img.set('date', date)

    collection = collection.map(add_date)
    unique_dates = collection.aggregate_array('date').distinct()

    def mosaic_on_date(date):
        date = ee.String(date)
        daily = collection.filter(ee.Filter.eq('date', date))
        merged_geometry = daily.geometry().dissolve()
        covers = merged_geometry.contains(roi, ee.ErrorMargin(10))

        mosaic = daily.median().clip(roi)
        metadata = {
            'date': date,
            'system:time_start': ee.Date(date).millis(),
            'coverage': 'full',
            'image_count': daily.size()
        }

        return ee.Algorithms.If(
            covers,
            mosaic.set(metadata),
            None
        )

    mosaics = ee.List(unique_dates.map(mosaic_on_date)).removeAll([None])
    return ee.ImageCollection(mosaics)
