# Currency Exchange Data Pipeline (Medallion Architecture)

An end-to-end ELT data processing pipeline extracting currency metrics from the Frankfurter API and storing structured results inside an analytical SQLite database engine.

## Architecture Pipeline Overview
- **Bronze**: Raw immutable data ingestion audit logging storage format.
- **Silver**: Deduped, type cast parsed currencies verifying `rate > 0`.
- **Gold**: Fact tables tracking percentage variances and 7-day trailing metrics joined with time/currency dimensions.

## Setup Instructions

1. **Install Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
