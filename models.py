from google.cloud import aiplatform

# Set your project ID and location
PROJECT_ID = "gen-lang-client-0038893414"
LOCATION = "us-central1"  # or "europe-west4", etc.

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# List models
models = aiplatform.Model.list()
for model in models:
    print(f"Model Name: {model.display_name}")
    print(f"Model ID: {model.resource_name}")
    print(f"Supported Predict Schemas: {model.supported_input_storage_formats}")
    print("-" * 30)
