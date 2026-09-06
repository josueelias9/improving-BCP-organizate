from datetime import date

from src.Aframework.gateway.content_extractor.scotiabank_parser import ScotiabankParser


def test_scotiabank_ocr_extracts_balance_and_account(monkeypatch, tmp_path):
    image_path = tmp_path / "scotiabank_snapshot.jpg"
    image_path.write_bytes(b"fake-image-bytes")

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    def fake_post(url, files=None, data=None):
        assert "/tesseract" in url
        assert files is not None
        assert data is not None
        return FakeResponse(
            {
                "data": {
                    "stdout": "S/ 7,326.90\nScotiabank: 833-0832476\nCCI: 009-724-208330832476-67"
                }
            }
        )

    monkeypatch.setattr(
        "src.Aframework.gateway.content_extractor.scotiabank_parser.requests.post",
        fake_post,
    )

    parser = ScotiabankParser()
    extracted_text = parser.read_file(str(image_path))

    assert "7,326.90" in extracted_text
    assert parser.get_balance(extracted_text) == 7326.9
    assert parser.get_account(extracted_text) == "833-0832476"
    assert parser.get_initial_day(extracted_text) == date.today()
