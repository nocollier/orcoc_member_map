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


def manual_fixes(df: pd.DataFrame) -> pd.DataFrame:
    # Add a family name by parsing text
    df["Family"] = df["N"].apply(
        lambda n: " ".join(n.split()[:2]) if "Buskirk" in n else n.split()[0]
    )
    # Drop some families that have left but are still in the directory
    df = df[(df["Family"] != "Pickrell") & (df["Family"] != "Andersons")]
    # Add locations
    df = df.assign(
        lat=df["ADR"].apply(lambda a: locations[a][0] if a in locations else pd.NA)
    )
    df = df.assign(
        lon=df["ADR"].apply(lambda a: locations[a][1] if a in locations else pd.NA)
    )
    noaddr = df[df["lat"].isna()]
    if len(noaddr):
        print("No addresses for:")
        print(noaddr[["N", "ADR"]].to_string())
    return df


def get_directory() -> pd.DataFrame:
    df = parse_vcf_to_dataframe("Directory.vcf")
    df = manual_fixes(df)
    return df
