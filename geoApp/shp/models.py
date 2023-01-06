from django.db import models
import datetime
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from osgeo import ogr, osr
import geopandas as gpd
import os
import glob
import zipfile
import traceback
from sqlalchemy import *
from geoalchemy2 import Geometry, WKTElement
from geo.Geoserver import Geoserver
from pg.pg import Pg
from geoApp.settings import BASE_DIR

####################################################################################
# Please change the Pg parameters, Geoserver parameters and conn_str
####################################################################################
# initializing the library
db = Pg(dbname='geoapp', user='postgres',
        password='ageosdatabase', host='localhost', port='5432')
geo = Geoserver('http://127.0.0.1:8083/geoserver', username='admin', password='geoserver')
# Database connection string (postgresql://${database_user}:${databse_password}@${database_host}:${database_port}/${database_name}
conn_str = 'postgresql://postgres:ageosdatabase@localhost:5432/geoapp'

# Create shapefile model.
class Shp(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d', blank=True)
    uploaded_date = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Shp)
def publish_data(sender, instance, created, **kwargs):
    file = instance.file.path
    file_format = os.path.basename(file).split('.')[-1]
    file_name = os.path.basename(file).split('.')[0]
    file_path = os.path.dirname(file)

    print('----------------------------')
    print(file_name)
    print('----------------------------')

    #Check if uploaded file is zip file
    if not zipfile.is_zipfile(file):
        return "File not a valid zipfile."

    # Extract the zip file
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(file_path)

    # Remove the zip file
    os.remove(file)

    # To get the shp file
    shp = glob.glob(r'{}/**/*.shp'.format(file_path), recursive=True)[0]

    #using ogr to interact with the shapefile
    try:
        datasource = ogr.Open(shp)
        layer = datasource.GetLayer(0)
        shapefile_ok = True
        print('Shapefile ok')
    except:
        traceback.print_exc()
        shapefile_ok = False
        print('Bad Shapefile')

    if not shapefile_ok:
        return "Not a valid shapefile."

    # Make geodataframe
    gdf = gpd.read_file(shp)

    epsg = gdf.crs.to_epsg()

    print('----------------------------')
    print(epsg)
    print('----------------------------')

    if epsg is None:
        # WGS 84 coordinate system 
        epsg = 4326

    # geom_type = gdf.geom_type[1]

    # Create the SQLAlchemy's engine to use
    engine = create_engine(conn_str)

    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=epsg))

    # Drop the geometry column (since we already backup this column with geom)
    gdf.drop(columns='geometry', axis=1, inplace=True)

    #Post gdf to the postgreSql
    gdf.to_sql(file_name, engine, 'data', if_exists='replace', index=False, dtype={'geom': Geometry('Geometry', srid=epsg)})


    '''
    Publish shp to geoserver using geoserver-rest
    '''
    geo.create_featurestore(store_name='geoApp', workspace='geoapp', db='geoapp', host='localhost', pg_user='postgres',
                         pg_password='ageosdatabase', schema='data')
    geo.publish_featurestore(workspace='geoapp', store_name='geoApp', pg_table=file_name)

    # geo.create_outline_featurestyle('geoApp_shp', workspace='geoapp')
    # geo.publish_style(layer_name=file_name, style_name='geoApp_shp', workspace='geoapp')

    # os.remove(shp)




@receiver(post_delete, sender=Shp)
def delete_data(sender, instance, **kwargs):
    db.delete_table(instance.name, schema='data')
    geo.delete_layer(instance.name, 'geoapp')