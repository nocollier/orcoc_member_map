import folium
import pandas as pd

from locations import locations


def parse_vcf_to_dataframe(vcf_file_path):
    contacts = []
    current_contact = {}

    with open(vcf_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "BEGIN:VCARD":
                current_contact = {}  # Start a new contact
            elif line == "END:VCARD":
                contacts.append(current_contact)  # Add completed contact to list
            elif ":" in line:
                # Basic parsing for key:value pairs
                key, value = line.split(":", 1)
                # Handle potential parameters (e.g., TEL;TYPE=HOME)
                if ";" in key:
                    key = key.split(";")[0]
                current_contact[key] = value.replace(";", " ").strip()

    df = pd.DataFrame(contacts)
    return df


df = parse_vcf_to_dataframe("Directory.vcf")
df["Family"] = df["N"].apply(
    lambda n: " ".join(n.split()[:2]) if "Buskirk" in n else n.split()[0]
)
df = df[
    (df["Family"] != "Pickrell")
    & (df["Family"] != "Andersons")
    & (df["Family"] != "Bruney")
]
df["latlon"] = df["ADR"].apply(lambda a: locations[a] if a in locations else pd.NA)

noaddr = df[df["latlon"].isna()]
if len(noaddr):
    print("No addresses for:")
    print(noaddr)

df = df.dropna(subset="latlon")
m = folium.Map(
    location=[
        df["latlon"].apply(lambda v: v[0]).mean(),
        df["latlon"].apply(lambda v: v[1]).mean(),
    ],
    zoom_start=10,
)
for addr, grp in df.groupby("ADR"):
    row = grp.iloc[0]
    folium.Marker(row["latlon"], popup=" / ".join(grp["Family"].unique())).add_to(m)

# Save the map to an HTML file
m.save("map.html")
