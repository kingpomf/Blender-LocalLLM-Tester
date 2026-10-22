"""Read-only model discovery using the existing global OpenCode credentials.

Run manually with Python 3; never prints the credential or submits inference.
"""

import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    config_path = Path.home() / ".config/opencode/opencode.json"
    config = json.loads(config_path.read_text())
    provider = config["provider"]["z6-llama"]
    options = provider["options"]
    key = options.get("apiKey", "")
    if key.startswith("{file:") and key.endswith("}"):
        key = Path(key[6:-1]).expanduser().read_text().strip()
    elif key.startswith("{env:") and key.endswith("}"):
        key = os.environ[key[5:-1]]
    request = Request(
        options["baseURL"].rstrip("/") + "/models",
        headers={"Authorization": "Bearer " + key},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Z6 model discovery failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    advertised = sorted(item["id"] for item in payload["data"])
    print(json.dumps({
        "configured_models": sorted(provider["models"]),
        "advertised_models": advertised,
        "selected_model": "qwen38-27b",
        "selected_advertised": "qwen38-27b" in advertised,
        "inference_submitted": False,
    }, indent=2))
    return 0 if "qwen38-27b" in advertised else 1


if __name__ == "__main__":
    raise SystemExit(main())
