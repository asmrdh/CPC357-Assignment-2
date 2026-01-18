# CPC357-Assignment-2 - LPR Based Autonomous Parking Management System  on Google Cloud Platform

## Group Members

1. Bernadette Lee Pei Chen (163517)
2. Nur Asma Mardhiah binti Roszi (162175)

---

# 🚗 LPR Based Autonomous Parking Management System  on Google Cloud Platform

This repository documents the technical architecture and development process for a serverless parking management system built on **Google Cloud Platform (GCP)**. The system automates vehicle entry, exit tracking, and financial logging using AI-driven OCR and event-driven computing.

---

## 🏗 System Architecture & API Functions

The system is built as a fully serverless pipeline to ensure high availability and scalability.

* **Cloud Storage**: Serves as the landing zone for high-resolution images from gate cameras.
* **Cloud Pub/Sub**: Acts as the asynchronous messenger that decouples storage from processing, ensuring no parking event is lost.
* **Cloud Run Functions**: The serverless "Brain" (Python 3.12) that executes logic when triggered by a Pub/Sub event.
* **Cloud Vision API**: The OCR engine that extracts license plate text from uploaded images.
* **Cloud Firestore**: A NoSQL operational database used for real-time tracking of "ACTIVE" parking sessions.
* **BigQuery**: An enterprise data warehouse used for long-term historical logging and financial reporting.

---

## 🚀 Deployment & Setup Guide

### 1. Project Configuration

* **Project ID**: `cpc357-assignment-2-481614`.
* **Enabled APIs**: Cloud Vision, Cloud Run Functions, Pub/Sub, Firestore (Native Mode), and BigQuery.
* **Service Account**: Use the `Compute Engine default service account` for runtime identity.

### 2. Infrastructure Setup

* **Bucket Notifications**: Link your `parking-camera-uploads` bucket to your `parking-image-events` topic using Cloud Shell:
> `gcloud storage buckets notifications create gs://parking-camera-uploads --topic=parking-image-events`


* **BigQuery History Table**: Create a table named `history` in the `parking_analytics` dataset with the following schema: `plate` (STRING), `event_type` (STRING), `timestamp` (TIMESTAMP), `fee` (FLOAT).

### 3. Function Deployment

* **Environment**: Cloud Run functions (2nd Gen).
* **Runtime**: Python 3.12.
* **Entry Point**: `parking_processor`.
* **Trigger**: Cloud Pub/Sub Topic: `parking-image-events`.

---

## 🧪 Simulation & Testing Logic

The system uses "state-aware" logic to differentiate between arrivals and departures based on the database content.

1. **Car Arrival**:
* **Action**: Upload a plate image (e.g., `car1.jpg`) to the bucket.
* **Result**: The function finds no active session, creates a new Firestore record, and logs an "ENTRY" in BigQuery.


2. **Car Departure**:
* **Action**: Wait a few minutes and upload the **same image** (`car1.jpg`) again.
* **Result**: The function calculates a fee based on the duration, deletes the Firestore record, and logs an "EXIT" row with the fee in BigQuery.



---

## 📊 Analytical Reporting

To verify the system's performance and revenue, run the following SQL query in BigQuery Studio:

```sql
SELECT 
  event_type, 
  COUNT(*) as total_count, 
  SUM(fee) as total_revenue_usd
FROM `cpc357-assignment-2-481614.parking_analytics.history`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY 1;

```

---

## 📂 Repository Contents

* `main.py`: Core Python function logic.
* `requirements.txt`: Python dependencies (functions-framework, google-cloud-vision, etc.).
* `/images`: Sample images for system verification.
