import geopandas as gpd
import pandas as pd
import folium
from shapely.geometry import Point
import numpy as np

# Load the shapefile with city boundaries
cities_gdf = gpd.read_file('C:/Geospatial-Data-Engineering/Data/pol_adm_gov_v02_20220414_shp/pol_admbnda_adm2_gov_v02_20220414.shp')

# Load the CSV file that has store counts per city
stores_count_by_city = pd.read_csv('C:/Geospatial-Data-Engineering/Zabka/Result/Data/stores_count_by_city.csv')

# Join store count data with cities GeoDataFrame
cities_with_store_count_gdf = cities_gdf.merge(stores_count_by_city, left_on='ADM2_PL', right_on='city', how='left')

# Fill NaN values with 0 (assuming cities with no stores have NaN after join)
cities_with_store_count_gdf['store_count'] = cities_with_store_count_gdf['store_count'].fillna(0)

# Classify the cities into bins based on the number of stores
bins = [0, 5, 10, 50, 100, 200, cities_with_store_count_gdf['store_count'].max()]
labels = ['0-4', '5-10', '11-50', '51-100', '101-200', f'201-{int(cities_with_store_count_gdf["store_count"].max())}']
cities_with_store_count_gdf['store_count_bins'] = pd.cut(cities_with_store_count_gdf['store_count'], bins=bins, labels=labels, include_lowest=True)

# Define a color palette for the bins
color_dict = {
    '0-4': '#FF0000',   # Red color for fewer than 5 stores
    '5-10': '#f1eef6',  # Light color for 5-10 stores
    '11-50': '#bdc9e1', # Slightly darker for 11-50 stores
    '51-100': '#74a9cf', # Mid-tone blue for 51-100 stores
    '101-200': '#2b8cbe',# Darker blue for 101-200 stores
    f'201-{int(cities_with_store_count_gdf["store_count"].max())}': '#045a8d' # Dark blue for the highest category
}

# Calculate bounds to centralize the map
bounds = cities_with_store_count_gdf.total_bounds  # [minx, miny, maxx, maxy]
center_lat = (bounds[1] + bounds[3]) / 2  # Average of miny and maxy
center_lon = (bounds[0] + bounds[2]) / 2  # Average of minx and maxx

# Initialize the map using the calculated center
m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

# Add a title using HTML (centered at the top)
title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%);
                background-color: white; padding: 10px; 
                font-size: 20px; font-weight: bold; z-index: 9999; 
                border: 1px solid black; border-radius: 5px;">
        Żabka Stores in Poland 
    </div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Style function for GeoJSON layer
def style_function(feature):
    bin_value = feature['properties']['store_count_bins']
    return {
        'fillColor': color_dict[bin_value],
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.7,
        'lineOpacity': 0.2
    }

# Add GeoJSON layer to the map
folium.GeoJson(
    cities_with_store_count_gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['ADM2_PL', 'store_count'],
        aliases=['City: ', 'Number of stores: '],
        localize=True
    )
).add_to(m)

# Add a smaller legend
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 180px; 
     background-color: white; border: 1px solid grey; z-index:9999; font-size:12px;
     padding: 5px;">
     <div style="text-align: center; font-weight: bold;">
         Stores
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
         <span>0-4</span> <i style="background:#FF0000; width:15px; height:15px; display:inline-block;"></i>
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center;">
         <span>5-10</span> <i style="background:#f1eef6; width:15px; height:15px; display:inline-block;"></i>
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center;">
         <span>11-50</span> <i style="background:#bdc9e1; width:15px; height:15px; display:inline-block;"></i>
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center;">
         <span>51-100</span> <i style="background:#74a9cf; width:15px; height:15px; display:inline-block;"></i>
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center;">
         <span>101-200</span> <i style="background:#2b8cbe; width:15px; height:15px; display:inline-block;"></i>
     </div>
     <div style="display: flex; justify-content: space-between; align-items: center;">
         <span>201+</span> <i style="background:#045a8d; width:15px; height:15px; display:inline-block;"></i>
     </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Fit the map bounds to the data
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# Save the map to an HTML file
m.save('poland_classified_stores_map_with_centered_zoom_no_layer.html')

# Display the map (for Jupyter Notebook users)
m
