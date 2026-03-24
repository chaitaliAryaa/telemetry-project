import json, unittest, datetime

# Read the three JSON files
with open("./data-1.json", "r", encoding="utf-8") as f:
    jsonData1 = json.load(f)
with open("./data-2.json", "r", encoding="utf-8") as f:
    jsonData2 = json.load(f)
with open("./data-result.json", "r", encoding="utf-8") as f:
    jsonExpectedResult = json.load(f)


def convertFromFormat1(jsonObject):
    """
    Format 1 has:
    - 'location' as a slash-separated string: country/city/area/factory/section
    - 'operationStatus' instead of 'status'
    - 'temp' instead of 'temperature'
    - timestamp already in milliseconds since epoch (integer)
    """
    locationParts = jsonObject["location"].split("/")

    result = {
        "deviceID": jsonObject["deviceID"],
        "deviceType": jsonObject["deviceType"],
        "timestamp": jsonObject["timestamp"],
        "location": {
            "country":  locationParts[0],
            "city":     locationParts[1],
            "area":     locationParts[2],
            "factory":  locationParts[3],
            "section":  locationParts[4]
        },
        "data": {
            "status":      jsonObject["operationStatus"],
            "temperature": jsonObject["temp"]
        }
    }
    return result


def convertFromFormat2(jsonObject):
    """
    Format 2 has:
    - device id/type nested under 'device'
    - ISO 8601 timestamp string → must convert to milliseconds since epoch
    - location fields as flat top-level keys (country, city, area, factory, section)
    - 'data' block already has correct keys (status, temperature)
    """
    # Convert ISO 8601 timestamp to milliseconds since epoch
    dt = datetime.datetime.strptime(jsonObject["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = round((dt - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

    result = {
        "deviceID":   jsonObject["device"]["id"],
        "deviceType": jsonObject["device"]["type"],
        "timestamp":  timestamp,
        "location": {
            "country": jsonObject["country"],
            "city":    jsonObject["city"],
            "area":    jsonObject["area"],
            "factory": jsonObject["factory"],
            "section": jsonObject["section"]
        },
        "data": jsonObject["data"]   # status + temperature already correct
    }
    return result


def main(jsonObject):
    """Route to the correct converter based on which format is detected."""
    if jsonObject.get("device") is None:
        return convertFromFormat1(jsonObject)
    else:
        return convertFromFormat2(jsonObject)


# ── Unit Tests ─────────────────────────────────────────────────────────────────

class TestSolution(unittest.TestCase):

    def test_sanity(self):
        """Expected result file loads correctly."""
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(result, jsonExpectedResult)

    def test_dataType1(self):
        """Format 1 converts to unified format correctly."""
        result = main(jsonData1)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 1 failed")

    def test_dataType2(self):
        """Format 2 converts to unified format correctly."""
        result = main(jsonData2)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 2 failed")


if __name__ == "__main__":
    unittest.main()
