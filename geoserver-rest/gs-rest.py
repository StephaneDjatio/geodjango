# Import the library
from geo.Geoserver import Geoserver

# Initialize the library
geo = Geoserver('http://127.0.0.1:8083/geoserver', username='admin', password='geoserver')

# get geoserver version
# version = geo.get_version()
# print(version)

# get all the datastores
datastores = geo.get_datastores()
print(datastores)

# For creating workspace
# geo.create_workspace(workspace='demo')

# For uploading raster data to the geoserver
# geo.create_coveragestore(layer_name='raster1', path=r'S:\AGEOS\GEOAPI\udemy\geoserver-rest\data\raster\raster1.tif', workspace='demo')

# For creating postGIS connection and publish postGIS table
# geo.create_featurestore(store_name='geo_data', workspace='demo', db='training', host='localhost', pg_user='postgres',
#                         pg_password='ageosdatabase')
# geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='jamoat-db')

# For uploading SLD file and connect it with layer
# geo.upload_style(path=r'S:\AGEOS\GEOAPI\udemy\geoserver-rest\data\style\raster1.sld', workspace='demo')
# geo.publish_style(layer_name='raster1', style_name='raster1', workspace='demo')

# geo.create_coveragestyle(raster_path=r'S:\AGEOS\GEOAPI\udemy\geoserver-rest\data\raster\raster1.tif', style_name='raster-new', workspace='demo',
#                          color_ramp='hsv')
# geo.publish_style(layer_name='raster1', style_name='raster-new', workspace='demo')