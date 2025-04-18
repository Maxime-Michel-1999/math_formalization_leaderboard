from kili.client import Kili
import streamlit as st
import pandas as pd

# Data is ingested from Kili's platform
api_key = st.secrets["kili_api_key"]
kili = Kili(api_key=api_key)


def safe_extract_status(latest_label):
    if latest_label is None:
        return float('nan')
    try:
        if "CLASSIFICATION_JOB" in latest_label and 'categories' in latest_label["CLASSIFICATION_JOB"] and len(latest_label["CLASSIFICATION_JOB"]['categories']) > 0:
            return latest_label["CLASSIFICATION_JOB"]['categories'][0]["name"]
        else:
            return float('nan')
    except (TypeError, KeyError):
        return float('nan')
    
def process_assets_and_labels(project_id):
    """
    Process assets and labels from a Kili project to create structured dataframes.
    
    This function retrieves assets and their associated labels from a Kili project,
    processes them to extract relevant information, and returns two dataframes:
    one with all assets and another with only finished assets.

    Args:
        kili (Kili): An authenticated Kili client instance
        project_id (str): The ID of the Kili project to process

    Returns:
        tuple: A tuple containing two pandas DataFrames:
            - assets_df: DataFrame containing all processed assets
            - assets_df_finished: DataFrame containing only assets marked as "FINISHED"
    """
    # Extract assets with specific statuses and required fields
    assets = kili.assets(project_id=project_id, 
                        status_in=["LABELED", "ONGOING", 'REVIEWED', "TO_REVIEW"],
                        fields=("externalId", "jsonMetadata", "id"))
    
    # Get list of external IDs for label filtering
    externalIds = [asset["externalId"] for asset in assets]

    # Retrieve labels for the assets with specific fields and types
    labels = pd.DataFrame(kili.labels(project_id=project_id, 
                                    asset_external_id_strictly_in=externalIds,
                                    fields=("assetId", "secondsToLabel", "jsonResponse", "author.firstname", "author.lastname", "createdAt"),
                                    type_in=["DEFAULT", "REVIEW"]))
    
        
    # Extract email from author field
    labels["author"] = labels["author"].apply(lambda x: x["firstname"] + " " + x["lastname"])

    # Process each asset to add label information
    for asset in assets:
        try:
            # Assign the most recent jsonResponse to the asset
            asset["jsonResponse"] = labels[(labels["assetId"] == asset["id"])]["jsonResponse"].iloc[-1]
        except Exception as e:
            print(f"Failed to assign jsonResponse for asset {asset['externalId']}: {e}")

        try:
            # Find the row with maximum labeling time (excluding specific user)
            max_seconds_row = labels[(labels["assetId"] == asset["id"]) & 
                                   (labels["author"] != "maxime.michel@kili-technology.com")]\
                                   .sort_values(by="secondsToLabel", ascending=False).iloc[0]
        except Exception as e:
            print(f"Failed to find max_seconds_row for asset {asset['externalId']}: {e}")
            continue

        try:
            # Assign creation date and author from the max_seconds_row
            asset["createdAt"] = max_seconds_row["createdAt"]
            asset["author"] = max_seconds_row["author"]
        except Exception as e:
            print(f"Failed to assign createdAt or author for asset {asset['id']}: {e}")

        try:
            # Calculate total labeling time (excluding specific user)
            asset["secondsToLabel"] = labels[(labels["assetId"] == asset["id"]) & 
                                           (labels["author"] != "maxime.michel@kili-technology.com")]\
                                           ["secondsToLabel"].sum()
        except Exception as e:
            print(f"Failed to calculate secondsToLabel sum for asset {asset['externalId']}: {e}")

    # Convert assets list to DataFrame and process additional fields
    assets_df = pd.DataFrame(assets)
    
    # Extract status from jsonResponse using safe_extract_status function
    assets_df["status"] = assets_df["jsonResponse"].apply(safe_extract_status)

    # Convert seconds to hours for labeling time
    assets_df['hoursToLabel'] = assets_df['secondsToLabel'] / 3600
    
    # Extract source and domain from jsonMetadata
    assets_df["source"] = assets_df["jsonMetadata"].apply(lambda x: x["source"].split("_")[0])
    assets_df["domain"] = assets_df["jsonMetadata"].apply(lambda x: x.get("domain", float('nan')))

    # Extract time taken
    assets_df["estimated_time_taken"] = assets_df.apply(lambda x: x["jsonResponse"].get("CLASSIFICATION_JOB_3", {}).get("categories", [{}])[0].get("name"), axis=1)
    # Classify unknown source as AIME or AMC 
    assets_df["source"] = assets_df.apply(lambda x: "AMC" if x["source"] == "problem" and x["estimated_time_taken"] == "30_MINUTES_AMC_0" else "AIME" if x["source"] == "problem" else x["source"], axis=1)


    # Convert creation date to datetime
    assets_df["createdAt"] = pd.to_datetime(assets_df["createdAt"])
    
    # Create filtered DataFrame with only finished assets
    assets_df_finished = assets_df[assets_df["status"] == "FINISHED"]

    return assets_df, assets_df_finished
