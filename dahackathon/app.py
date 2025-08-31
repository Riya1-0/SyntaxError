import pandas as pd
import folium

# Your MapTiler API key
maptiler_key = "Z30zg9tcCeRGrgKfYAFL"

# 1. Read Excel file
try:
    df = pd.read_excel("CDS.xlsx", engine="openpyxl")
except FileNotFoundError:
    print("Error: 'CDS.xlsx' not found. Please make sure the file is in the same folder as the script.")
    exit()

# 2. Drop rows with missing latitude or longitude
df = df.dropna(subset=["Latitude", "Longitude"])
if df.empty:
    print("Error: No valid latitude and longitude data found in the Excel file after cleaning.")
    exit()

# 3. Create folium map
m = folium.Map(
    location=[df.iloc[0]["Latitude"], df.iloc[0]["Longitude"]],
    zoom_start=5,
    tiles=None
)

# 4. Add MapTiler tiles
folium.TileLayer(
    tiles=f"https://api.maptiler.com/maps/basic/{{z}}/{{x}}/{{y}}.png?key={maptiler_key}",
    attr='&copy; <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> '
         '<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
    name="MapTiler",
    overlay=False,
    control=True
).add_to(m)

# 5. Add markers with popup HTML
for _, row in df.iterrows():
    project_name = row.get("Project name", "N/A")
    date_online = row.get("Date online", "N/A")
    decommission = row.get("Decommission", "N/A")
    product = row.get("Product", "N/A")
    announced = row.get("Announced", "N/A")
    size = row.get("Size", "N/A")
    capacity = row.get("All capacity", "N/A")

    # Styled popup card
    popup_html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif; width:250px;">
        <h4 style="margin:0; color:#27ae60;">{project_name}</h4>
        <hr style="margin:5px 0;">
        <b>Product:</b> {product}<br>
        <b>Size:</b> {size}<br>
        <b>Capacity:</b> {capacity}<br>
        <b>Date Online:</b> {date_online}<br>
        <b>Decommission:</b> {decommission}<br>
        <b>Announced:</b> {announced}<br>
    </div>
    """

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip=project_name,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# 6. Save to HTML
m.save("project_map_with_popups.html")
print("✅ Map with full project details created! Open 'project_map_with_popups.html'.")
