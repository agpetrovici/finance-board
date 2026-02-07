def polygon_to_bbox(polygon) -> list[list[float]] | None:
    """
    Convert Mindee polygon (list of Point objects with .x and .y attributes)
    to bbox format expected by frontend: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    """
    if not polygon:
        return None
    return [[point.x, point.y] for point in polygon]
