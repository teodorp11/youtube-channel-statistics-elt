# YouTube Channel Statistics ELT Pipeline

This repository hosts the foundational data extraction layer of a cloud-native ELT (Extract, Load, Transform) pipeline designed to programmatically harvest and process YouTube channel statistics. Built with scalability and automation in mind, the project establishes a robust ingestion framework that will seamlessly integrate into a comprehensive data warehousing and orchestration architecture.

## Data Source

As a proof-of-concept and data source, the pipeline currently extracts data from the renowned educational channel **@freeCodeCamp**. This provides a rich, real-world dataset to validate the extraction logic. However, the architecture is channel-agnostic; it can be quickly reconfigured to scrape any YouTube channel by simply updating the `CHANNEL_HANDLE` environment or configuration variable.

## Current Features (Phase 1: Ingestion)

Currently, the project focuses on a robust, localized Python application capable of interacting with Google's RESTful services:

- **API Integration:** Connects securely to the YouTube Data API v3, fetching channel metadata, recursively traversing "Uploads" playlists, and extracting key performance metrics (Views, Likes, Comments, Duration).
- **Modular & Extensible Design:** Engineered using decoupled components and adhering to the single-responsibility principle, ensuring smooth transitions when integrating with downstream orchestration tools.
- **Secure Credential Handling:** Employs standard 12-factor app methodologies for configuration, utilizing `.env` files to isolate and inject API secrets securely.
- **Optimized Network Calls:** Implements intelligent batch processing (chunking API requests to the maximum allowable limit of 50) and handles token-based pagination to minimize latency and respect API rate limits.
- **Standards Compliant:** Strictly adheres to PEP 8 constraints for idiomatic, readable, and maintainable Python code.

### Pipeline Execution Example

When initiated, the pipeline interactively confirms the target channel, calculates the playlist references, and manages the ingestion of specified batches:

```console
(venv) PS C:\Users\Admin\Desktop\youtube-channel-statistics-elt-pipeline> python -u video_statistics.py
============================================================
INITIALIZING YOUTUBE SCRAPER FOR: @freecodecamp
============================================================
Channel Name:   freeCodeCamp.org
Uploads ID:     UU8butISFwT-Wl7EV0hUK0BQ
Enter the number of videos to fetch (default is 10): 6

No.  | Video ID        | URL
------------------------------------------------------------
1    | T8PMKaNP_UA     | https://youtu.be/T8PMKaNP_UA
2    | gM2Ra8GpGuU     | https://youtu.be/gM2Ra8GpGuU
3    | gLm8i6ryFmA     | https://youtu.be/gLm8i6ryFmA
4    | ajIss2t5FxM     | https://youtu.be/ajIss2t5FxM
5    | zJHXDuUzFkc     | https://youtu.be/zJHXDuUzFkc
6    | Q4reYv2-t4g     | https://youtu.be/Q4reYv2-t4g
------------------------------------------------------------
Fetching metadata for 6 videos...

[SUCCESS] Data saved to: data\youtube_data_2026-04-06.json
```

### Extracted Data Schema

The ingested data is structured uniformly before being persisted. Here is an excerpt of the extracted JSON artifact containing the core statistics for the target videos:

```json
[
  {
    "video_id": "T8PMKaNP_UA",
    "title": "To keep clients: Do what you promise, communicate clearly, listen closely, and show you really care",
    "published_at": "2026-04-05T12:43:28Z",
    "duration": "PT55S",
    "view_count": 3192,
    "like_count": 15,
    "comment_count": 1
  },
  {
    "video_id": "gM2Ra8GpGuU",
    "title": "Why was the developer unhappy at their job...?",
    "published_at": "2026-04-04T12:32:15Z",
    "duration": "PT13S",
    "view_count": 6939,
    "like_count": 39,
    "comment_count": 2
  },
  {
    "video_id": "gLm8i6ryFmA",
    "title": "When you're trying to learn a new deep skill, a structured approach is everything.",
    "published_at": "2026-04-03T12:18:34Z",
    "duration": "PT1M14S",
    "view_count": 15347,
    "like_count": 116,
    "comment_count": 1
  }
]
```

## Setup & Installation Guide

To run this data pipeline locally, follow these steps to bootstrap your environment:

### 1. Environment Setup

It is highly recommended to use a Python virtual environment to isolate the project's dependencies and prevent version conflicts with system-level packages.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment (Windows)
.venv\Scripts\activate

# Activate the environment (macOS/Linux)
# source .venv/bin/activate
```

### 2. Configure Credentials

Create a `.env` file in the root directory and add your Google Cloud API key:

```env
API_KEY=your_youtube_data_api_key_here
```

### 3. Install Dependencies

Install the required Python packages explicitly defined for this pipeline:

```bash
pip install -r requirements.txt
```

### 4. Execute the Pipeline

Run the main ingestion script. You will be prompted to enter the number of recent videos you wish to scrape:

```bash
python video_statistics.py
```

## Technology Stack (Current)

- **Language:** Python
- **Core Libraries:** `requests` (API interactions), `pathlib` (filesystem routing), `python-dotenv` (secrets management), `json`
- **Integrations:** YouTube Data API v3

## Roadmap: Productionization & Cloud Architecture

To evolve this foundational script into an enterprise-grade analytics pipeline, the following milestones are actively plotted on the architectural roadmap:

### 1. Containerization

- **Docker & Docker Compose:** Containerize the ingestion scripts to ensure immutable and reproducible environments across development and production, eliminating local environment discrepancies and ensuring cloud-readiness.

### 2. Orchestration

- **Apache Airflow:** Introduce Airflow DAGs (Directed Acyclic Graphs) to reliably schedule, monitor, and manage the execution lifecycle of data extraction tasks, providing visual observability and automated retry mechanisms for transient API failures.

### 3. Storage & Data Warehousing

- **PostgreSQL Database:** Transition from local filesystem JSON artifacts to a structured PostgreSQL Data Warehouse. Implement a formal relational schema to stage the raw data and prepare it for downstream analytical transformations and BI integration.

### 4. Quality & Testing

- **Data Quality Contracts (Soda):** Integrate Soda Core to institute rigorous data quality checks (e.g., verifying `view_count` integrity, anomaly detection) to catch pipeline errors and ensure data validity before it enters the warehouse.
- **Unit/Integration Testing:** Build robust test coverage to validate internal script logic, utilizing frameworks like `pytest` and mocking external API responses to simulate edge cases.

### 5. Automation (CI/CD)

- **GitHub Actions:** Implement continuous integration pipelines to automatically trigger code linting, execute the unit test suites, and build new Docker container images on every push to the main branch.
