import base64
import json
import functions_framework
from datetime import datetime
from google.cloud import vision, firestore, bigquery

# --- INITIALIZE CLIENTS (Do this once outside the function) ---
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client()
bq_client = bigquery.Client()

@functions_framework.cloud_event
def parking_processor(cloud_event):
    # 1. Extract Pub/Sub message data
    pubsub_message = cloud_event.data["message"]
    
    if "data" in pubsub_message:
        decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        message_data = json.loads(decoded_data)
    else:
        print("No data in Pub/Sub message.")
        return

    bucket_name = message_data['bucket']
    file_name = message_data['name']
    image_uri = f"gs://{bucket_name}/{file_name}"

    # 2. Extract Plate Number via Vision API
    image = vision.Image(source=vision.ImageSource(gcs_image_uri=image_uri))
    response = vision_client.text_detection(image=image)
    
    if not response.text_annotations:
        print(f"No text detected in image {file_name}")
        return

    plate_text = response.text_annotations[0].description.split('\n')[0].strip().upper()

    # 3. Operational Logic: Entry or Exit?
    doc_ref = db.collection('active_sessions').document(plate_text)
    doc = doc_ref.get()
    now = datetime.utcnow()
    fee = 0.0
    event_type = ""

    if not doc.exists:
        # ARRIVAL: Create active record
        event_type = "ENTRY"
        doc_ref.set({
            'plate': plate_text,
            'entry_time': now,
            'status': 'ACTIVE'
        })
    else:
        # EXIT: Calculate fee and delete active record
        event_type = "EXIT"
        entry_time = doc.to_dict().get('entry_time')
        # Handle timezones by making 'now' naive or 'entry_time' UTC
        duration_hours = (now - entry_time.replace(tzinfo=None)).total_seconds() / 3600
        fee = round(max(5.0, duration_hours * 10.0), 2) 
        doc_ref.delete() 

    # 4. Analytical Logging: Record event in BigQuery
    # Replace with your actual project ID from your screenshots
    table_id = "cpc357-assignment-2-481614.parking_analytics.history"
    rows_to_insert = [{
        "plate": plate_text, 
        "event_type": event_type, 
        "timestamp": now.isoformat(), 
        "fee": fee
    }]
    
    errors = bq_client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"BigQuery Errors: {errors}")
    else:
        print(f"Processed {event_type} for {plate_text}. Fee: ${fee}")
