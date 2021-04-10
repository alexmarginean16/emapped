"""
from PIL import Image
from PIL.ExifTags import TAGS

my_img = Image.open("IMG_0547.jpg")

exif_data = my_img.getexif()
for tag_id in exif_data:
    tag = TAGS.get(tag_id, tag_id)
    data = exif_data.get(tag_id)

    print(f"{tag:16}: {data}")
"""

"""
import pyexiv2

metadata = pyexiv2.ImageMetadata('IMG_0547.jpg')
metadata.read()
"""

from GPSPhoto import gpsphoto
# Get the data from image file and return a dictionary
data = gpsphoto.getGPSData('IMG_0547.jpg')
rawData = gpsphoto.getRawData('IMG_0547.jpg')

# Print out just GPS Data of interest
for tag in data.keys():
    print (f"{tag:16}: {data[tag]}")

# Print out raw GPS Data for debugging
for tag in rawData.keys():
    print (f"{tag:16}: {rawData[tag]}")

# Create a GPSPhoto Object
"""photo = gpsphoto.GPSPhoto()
photo = gpsphoto.GPSPhoto("/path/to/photo.jpg")

# Create GPSInfo Data Object
info = gpsphoto.GPSInfo((35.104860, -106.628915))
info = gpsphoto.GPSInfo((35.104860, -106.628915), \
          timeStamp='1970:01:01 09:05:05')
info = gpsphoto.GPSInfo((35.104860, -106.628915), \
          alt=10, timeStamp='1970:01:01 09:05:05')

# Modify GPS Data
photo.modGPSData(info, '/path/to/newFile.jpg')

# Strip GPS Data
photo.stripData('/path/to/newFile.jpg')"""