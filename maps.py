from GPSPhoto import gpsphoto
import reverse_geocoder as rg

def getCoordinates(image_name):
	data = gpsphoto.getGPSData(image_name)

	latitude = data['Latitude']
	longitude = data['Longitude']

	list = []
	list.append(latitude)
	list.append(longitude)

	return list

def reverseGeocode(coordinates):
	result = rg.search(coordinates)
	city = result[0]['name']
	return city


coordinates = getCoordinates('IMG_0547.jpg')
coordinates = tuple(coordinates)
city = reverseGeocode(coordinates)
print(city)