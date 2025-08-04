import folium

from directory import get_directory

df = get_directory()

# Only include those with a location
df = df.dropna(subset="lat")

# Make the map using folium
lat0 = df["lat"].mean()
lon0 = df["lon"].mean()
m = folium.Map(
    location=[lat0, lon0],
    zoom_start=10,
)
folium.Marker(
    [lat0, lon0],
    popup="Person-weighted Center",
    icon=folium.Icon(prefix="fa", icon="arrows-to-circle", color="red"),
).add_to(m)
folium.Marker(
    [35.99088771045777, -84.18989279737596],
    icon=folium.Icon(prefix="fa", icon="church", color="green"),
).add_to(m)
for addr, grp in df.groupby(["lat", "lon"]):
    row = grp.iloc[0]
    folium.Marker(
        [row["lat"], row["lon"]], popup=" / ".join(grp["Family"].unique())
    ).add_to(m)
m.save("map.html")
