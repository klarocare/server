# Google Sheets Setup for Callback Endpoint

This guide explains how to set up Google Sheets integration for the callback endpoint.

## Overview

The callback endpoint (`/api/callback/request`) accepts a topic and phone number, then stores this information in a Google Sheets document for follow-up.

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API

### 2. Create a Service Account

1. In the Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name (e.g., "callback-sheets-service")
4. Grant the "Editor" role
5. Create and download the JSON key file

### 3. Create a Google Sheets Document

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Add headers to the first row:
   - Column A: "Timestamp"
   - Column B: "Topic"
   - Column C: "Phone Number"
   - Column D: "Status"
4. Share the spreadsheet with the service account email (found in the JSON file)
5. Copy the spreadsheet ID from the URL (the long string between /d/ and /edit)

### 4. Configure Environment Variables

Add these environment variables to your `.env` file:

```bash
# Option 1: Use JSON credentials string
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}'

# Option 2: Use service account file path
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/service-account.json

# Required: Spreadsheet ID
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id-here
```

## API Usage

### Create Callback Request

```bash
curl -X POST "http://localhost:8000/api/callback/request" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Care Level Application",
    "phone_number": "+49123456789"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Callback request recorded successfully"
}
```

### Get All Callback Requests

```bash
curl -X GET "http://localhost:8000/api/callback/requests"
```

Response:
```json
{
  "success": true,
  "data": [
    ["2024-01-15 10:30:00", "Care Level Application", "+49123456789", "Pending"],
    ["2024-01-15 11:45:00", "Mobility Support", "+49987654321", "Pending"]
  ],
  "message": "Retrieved 2 callback requests"
}
```

## Troubleshooting

### Common Issues

1. **"Google Sheets not configured"**
   - Check that all environment variables are set correctly
   - Verify the service account has access to the spreadsheet

2. **"Invalid credentials"**
   - Ensure the JSON credentials are valid
   - Check that the service account email has been added to the spreadsheet

3. **"Spreadsheet not found"**
   - Verify the spreadsheet ID is correct
   - Ensure the service account has access to the spreadsheet

### Testing

Run the test script to verify the endpoint works:

```bash
python test_callback_endpoint.py
```

## Security Notes

- Keep your service account credentials secure
- Don't commit credentials to version control
- Use environment variables or secure secret management
- Consider using Google Cloud Secret Manager for production deployments 