from src.core.omicspred_client import OmicsPredClient
import json

client = OmicsPredClient()
details = client.get_score_details("OPGS000890")
formatted = client.format_score_for_ui(details)
print(f"ID: {formatted.get('id')}")
print(f"Dev Cohorts: '{formatted.get('dev_cohorts')}'")
print(f"Dataset Name: '{formatted.get('dataset_name')}'")
