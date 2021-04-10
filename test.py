import reverse_geocoder as rg

coordinates = (28.613939, 77.209023)
result = rg.search(coordinates)

print(result)