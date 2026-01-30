import ee

# -----------------------------
# Remove Small Flood Areas
# -----------------------------
def remove_small_area(mask_collection, roi, min_area):
    """
    Post-process flood masks to keep patches larger than min_area (in m²).
    Output pixels have value 2 (flood depth); others are masked.

    Args:
        mask_collection (ee.ImageCollection): Binary flood masks (0 = dry, 1 = flood).
        roi (ee.Geometry): Area of interest.
        min_area (float): Minimum flood patch area to retain (in square meters).

    Returns:
        ee.ImageCollection: Cleaned flood images with 'depth' band.
    """
    def process_image(image):
        date = image.get('date')

        # Convert area to pixel count (10m resolution = 100 m²/pixel)
        min_pixels = ee.Number(min_area).divide(100).round()

        # Count connected pixels in each flood patch
        patch_sizes = image.connectedPixelCount(
            maxSize=128, eightConnected=True
        )

        # Mask out small patches
        cleaned = image.updateMask(patch_sizes.gte(min_pixels)).clip(roi)

        # Convert flood pixels to depth = 1
        depth = cleaned.rename('depth').selfMask().toFloat()

        return depth.set({'date': date})

    return mask_collection.map(process_image)


# -----------------------------
# Sentinel-2 Cloud Mask (SCL)
# -----------------------------
def mask_clouds(img):
    """
    Generates a binary mask where 1 = cloud/cirrus/shadow, 0 = valid land or water.

    Args:
        img (ee.Image): Sentinel-2 image containing the 'SCL' band.

    Returns:
        ee.Image: Single-band mask image ('cloud_mask').
    """
    scl = img.select('SCL')

    cloud_shadow = scl.eq(3)
    cloud = scl.eq(8)
    cirrus = scl.eq(9)

    cloud_mask = cloud_shadow.Or(cloud).Or(cirrus).rename('cloud_mask')
    return cloud_mask.copyProperties(img, img.propertyNames())
