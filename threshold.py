import ee

# -----------------------------
# KMeans Classification on NDWI
# -----------------------------
def classify_kmeans(ndwi_img, aoi, n_clusters=2):
    """
    Classifies an NDWI image using KMeans clustering.

    Args:
        ndwi_img (ee.Image): Image with NDWI band named 'NDWI'.
        aoi (ee.Geometry): Area of interest for sampling and classification.
        n_clusters (int): Number of clusters (default is 2).

    Returns:
        ee.Image: Binary flood mask with 'flood_class' band (1 = flood, 0 = non-flood).
    """
    training = ndwi_img.sample(
        region=aoi,
        scale=10,
        numPixels=20000,
        seed=42
    )
    
    clusterer = ee.Clusterer.wekaKMeans(n_clusters).train(training)
    clustered = ndwi_img.cluster(clusterer).rename('raw_cluster')
    
    # Compute mean NDWI per cluster
    means = []
    for i in range(n_clusters):
        cluster_mask = clustered.eq(i)
        masked_ndwi = ndwi_img.updateMask(cluster_mask)
        mean_ndwi = masked_ndwi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=10,
            maxPixels=1e8
        ).get('NDWI')
        means.append(ee.Number(mean_ndwi))

    flood_cluster = ee.List(means).indexOf(ee.List(means).reduce(ee.Reducer.max()))
    flood_mask = clustered.eq(flood_cluster).rename('flood_class')

    return flood_mask.set('system:time_start', ndwi_img.get('system:time_start'))
