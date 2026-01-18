# CPC357-Assignment-2 - LPR Based Autonomous Parking Management System  on Google Cloud Platform

## Group Members

1. Bernadette Lee Pei Chen (163517)
2. Nur Asma Mardhiah binti Roszi (162175)

---

# 🚗 Smart Parking System: AI-Driven Technical Architecture

This repository documents the development of an automated parking management system built on **Google Cloud Platform (GCP)**. The system leverages an event-driven architecture to automate car entry, exit, and billing using OCR and serverless computing.

## 🏗 System Architecture

The architecture is designed to be fully serverless, ensuring high scalability and cost-efficiency:

1. **Image Ingestion**: A gate camera uploads a car license plate photo to a **Cloud Storage** bucket.
2. **Event Notification**: Cloud Storage triggers a **Pub/Sub** message notifying the system of a new upload.
3. **Processing (The Brain)**: A **Cloud Run function** (Python 3.12) is triggered by the Pub/Sub message to execute the core logic.
4. **AI OCR**: The **Cloud Vision API** extracts the license plate text from the raw image.
5. **Operational State**: **Cloud Firestore** manages the real-time status of the parking lot (Entry vs. Exit).
6. **Data Warehousing**: All transactions are streamed into **BigQuery** for long-term financial and operational analytics.

---

## 📂 Repository Structure

* `main.py`: Python script containing the Cloud Run function logic and GCP client initializations.
* `requirements.txt`: List of dependencies including `functions-framework`, `google-cloud-vision`, `google-cloud-firestore`, and `google-cloud-bigquery`.
* `/images`: Sample car plate images used for system testing and simulation.
* `setup_guide.pdf`: A technical manual detailing API enablement and project configuration.

---

## 🚀 Deployment Steps

### 1. API Configuration

Enable the following APIs in the GCP Console:

* Cloud Vision API
* Cloud Run Functions API
* Pub/Sub API
* Firestore API (Native Mode)
* BigQuery API

### 2. BigQuery Schema

Create a table named `history` in the `parking_analytics` dataset with this schema:

* `plate` (STRING)
* `event_type` (STRING)
* `timestamp` (TIMESTAMP)
* `fee` (FLOAT)

### 3. Deploying the "Brain"

* Create a **Cloud Run function** (2nd Gen).
* Set the **Entry Point** to `parking_processor`.
* Link the **Pub/Sub trigger** to the `parking-image-events` topic.

---

## 🧪 Simulation & Testing

To verify the system logic (Step 7 of the development process):

1. **Car Arrival**: Upload an image to the `parking-camera-uploads` bucket.
* *Result*: A new document appears in Firestore's `active_sessions` collection, and an "ENTRY" row is logged in BigQuery.


2. **Car Departure**: Upload the **same image** again after a delay.
* *Result*: The system calculates a fee based on the duration, removes the active session from Firestore, and logs an "EXIT" row with the fee in BigQuery.



---

## 📈 Analytical Query

To generate a daily revenue report, run the following SQL in BigQuery Studio:

```sql
SELECT 
  event_type, 
  COUNT(*) as total_count, 
  SUM(fee) as revenue 
FROM `cpc357-assignment-2-481614.parking_analytics.history` 
GROUP BY event_type;

