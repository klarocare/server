import os
import logging
from typing import Dict, Any
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from schemas.callback_schema import CallbackRequest


class GoogleSheetsService:
    """Service for handling Google Sheets operations"""
    
    def __init__(self):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Setup Google Sheets credentials"""
        try:
            # Get credentials from environment variable or service account file
            credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
            if credentials_json:
                # If credentials are provided as JSON string
                import json
                creds_dict = json.loads(credentials_json)
                self.credentials = Credentials.from_service_account_info(
                    creds_dict, scopes=self.scope
                )
            else:
                # Try to load from service account file
                service_account_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "service-account.json")
                if os.path.exists(service_account_file):
                    self.credentials = Credentials.from_service_account_file(
                        service_account_file, scopes=self.scope
                    )
                else:
                    logging.warning("No Google Sheets credentials found. Callback requests will not be saved.")
                    self.credentials = None
            
            if self.credentials:
                self.client = gspread.authorize(self.credentials)
                self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
                if self.spreadsheet_id:
                    self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                    self.worksheet = self.spreadsheet.sheet1  # Use first sheet
                else:
                    logging.warning("No Google Sheets spreadsheet ID found.")
                    self.spreadsheet = None
                    self.worksheet = None
            else:
                self.client = None
                self.spreadsheet = None
                self.worksheet = None
                
        except Exception as e:
            logging.error(f"Error setting up Google Sheets credentials: {e}")
            self.client = None
            self.spreadsheet = None
            self.worksheet = None
    
    def add_callback_request(self, request: CallbackRequest) -> Dict[str, Any]:
        """Add a callback request to Google Sheets"""
        try:
            if not self.worksheet:
                return {
                    "success": False,
                    "message": "Google Sheets not configured"
                }
            
            # Prepare row data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                request.topic,
                request.phone_number,
                "Pending"  # Status
            ]
            
            # Add row to worksheet
            self.worksheet.append_row(row_data)
            
            logging.info(f"Added callback request to Google Sheets: {request.topic} - {request.phone_number}")
            
            return {
                "success": True,
                "message": "Callback request recorded successfully"
            }
            
        except Exception as e:
            logging.error(f"Error adding callback request to Google Sheets: {e}")
            return {
                "success": False,
                "message": f"Error recording callback request: {str(e)}"
            }
    
    def get_all_callback_requests(self) -> Dict[str, Any]:
        """Get all callback requests from Google Sheets"""
        try:
            if not self.worksheet:
                return {
                    "success": False,
                    "message": "Google Sheets not configured"
                }
            
            # Get all values from worksheet
            all_values = self.worksheet.get_all_values()
            
            # Skip header row if it exists
            if all_values and len(all_values) > 1:
                data = all_values[1:]  # Skip header
            else:
                data = all_values
            
            return {
                "success": True,
                "data": data,
                "message": f"Retrieved {len(data)} callback requests"
            }
            
        except Exception as e:
            logging.error(f"Error retrieving callback requests from Google Sheets: {e}")
            return {
                "success": False,
                "message": f"Error retrieving callback requests: {str(e)}"
            } 