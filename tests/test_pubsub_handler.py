import base64
import json

from covid_pipeline.events.pubsub_handler import extract_gcs_object


def test_extract_gcs_object_from_pubsub_event():
    payload = {"bucket": "covid-bucket", "name": "sample/covid.csv"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    event = {"message": {"data": encoded}}

    assert extract_gcs_object(event) == ("covid-bucket", "sample/covid.csv")
