Input > Polygon of desired tiles, Zoom Level

Create envelope for polygon
Buffer polygon by tile width/2 for zoom level
Calculate map tile x,y coords within bounding box
for each pair, get centroid of tile
Check if centroid is within buffered polygon
Yes > add to to-request list
No > skip tile
write to-request list to disk (json)
for each to-request, send request

Output > StartTime, EndTime, to-request list, requested list