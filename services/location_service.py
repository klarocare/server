import os
import requests

class LocationService():

    def __init__(self) -> None:
        self.API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
        self.URL = "https://places.googleapis.com/v1/places:searchText"
        self.headers = {
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.googleMapsUri,places.location,places.primaryType,places.primaryTypeDisplayName,places.id",
            "X-Goog-Api-Key": self.API_KEY,
            "Content-Type": "application/json"
        }

    async def get_places(self, query: str, page_size: int = 3):
        data = {
            "textQuery": query,
            "pageSize": page_size
        }

        try:
            response = requests.post(self.URL, headers=self.headers, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the JSON response from the API
        except requests.HTTPError as exc:
            raise Exception(exc)