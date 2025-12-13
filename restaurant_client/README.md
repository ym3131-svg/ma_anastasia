# restaurant-client

A lightweight Python client for the **Foursquare Places API** that lets users search for restaurants near a location and retrieve useful details such as **ratings, price level, and opening hours**.

The package supports both **Python usage** and a simple **command-line interface (CLI)**, returning results as a clean **pandas DataFrame** for easy analysis.

---

## Features

- Search restaurants by **query + location (`near`)**
- Optional filters: result limit, radius, categories
- Retrieve restaurant **details**:
  - Rating (when available)
  - Price tier → minimum price (`$`–`$$$$`)
  - Opening hours / open-now status (when available)
- Output results as a **pandas DataFrame**
- Simple **CLI** for typed requests
- Secure API key handling via **environment variables** (`python-dotenv`)

---

## Installation

### From TestPyPI (recommended for testing)

```bash
pip install -i https://test.pypi.org/simple/ restaurant-client
