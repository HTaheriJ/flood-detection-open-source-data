import ee

def add_layer_name(collection, prefix="Flood extent on "):
    """
    Adds a 'layer_name' property to each image using its date and source property.

    Args:
        collection (ee.ImageCollection): The image collection to update.
        prefix (str): Label prefix (default "Flood extent on ").

    Returns:
        ee.ImageCollection: Updated collection with 'layer_name' property added.
    """
    def set_layer_name(img):
        date_str = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd')
        source = ee.String(img.get('source'))  # Must be set beforehand
        layer_name = ee.String(prefix).cat(date_str).cat(" (").cat(source).cat(")")
        return img.set('layer_name', layer_name)

    return collection.map(set_layer_name)
