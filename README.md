# Tron Wallet Info Microservice

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12+-green.svg)
![Pre-commit](https://github.com/Sayrexxx/tron-wallet-info/actions/workflows/pre-commit.yml/badge.svg)
![CI](https://github.com/Sayrexxx/tron-wallet-info/actions/workflows/tests.yml/badge.svg)

_A FastAPI microservice for retrieving Tron wallet information (balance, bandwidth, energy) with query history tracking._

## Table of Contents
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Testing](#testing)
- [Database migrations](#database-migrations)
- [Usage examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **Wallet Information**: Get TRX balance, bandwidth, and energy for any Tron address
- **Query History**: Track all wallet lookup requests with pagination
- **Automated Documentation**: Built-in Swagger UI at `/docs`
- **CI/CD**: GitHub Actions for testing and pre-commit checks
- **Containerized**: Ready for Docker deployment

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirects to `/docs` |
| `/wallet-info` | POST | Get wallet info (requires `address` query parameter) |
| `/query-history` | GET | Get paginated query history (`?skip=0&limit=10`) |

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Sayrexxx/tron-wallet-info.git
   cd tron-wallet-info
   ```
1. Set up environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
1. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

```bash
docker-compose up --build
```

Access the API at http://localhost:8000

## Configuration

### Environment variables

|      Variable     |                   Default                  |           Description           |
|:-----------------:|:------------------------------------------:|:-------------------------------:|
| DATABASE_URL      | sqlite+aiosqlite:///sqlite_data/queries.db | Database connection string      |
| API_KEY           | -                                          | Your Tron API key               |
| PORT              | 8000                                       | Server port                     |

## Testing

### Run Tests Locally

```bash
pytest
```

### CI Workflows

We use two separate workflows:
1. Pre-commit Checks:
   - Runs linters and formatters
   - Triggered on push/PR to `main`
1. Tests:
   - Sets up test database
   - Runs all pytest suites
   - Requires `API_KEY` GitHub secret

## Database Migrations

Using **Alembic** for database schema management:
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Usage Examples

### 1. Parsing Wallet Information

**Request:**
```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/wallet-info?address=TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g' \
  -H 'accept: application/json' \
  -d ''
```

**Response:**
```json
{
  "balance": 85623170,
  "bandwidth": 600,
  "energy": 10
}
```

![изображение](https://github.com/user-attachments/assets/61bddc8a-76fe-4c39-ae4c-8420286c9052)

### 2. Checking Query History

**Request:**
```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/query-history?skip=0&limit=10' \
  -H 'accept: application/json'
```

**Response:**
```json
[
  {
    "timestamp": "2025-04-12T22:32:17.820441",
    "wallet_address": "TLw6HAySiPaJqQnTavhGg3T9C4d5dFVf5z",
    "id": 1
  },
  {
    "timestamp": "2025-04-12T22:33:38.029246",
    "wallet_address": "TZ4UXDV5ZhNW7fb2AMSbgfAEZ7hWsnYS2g",
    "id": 2
  }
]
```

![изображение](https://github.com/user-attachments/assets/e64ed1c8-8300-4f6b-bd0b-c3a0560c3850)

## Troubleshooting

### Common Issues

1. Database Connection Errors:
```log
    sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```
- Solution: Ensure the sqlite_data directory exists and has write permissions
- Fix:
```bash
mkdir -p sqlite_data && chmod 755 sqlite_data
```

1. Migration Problems
```log
    alembic.util.exc.CommandError: Can't locate revision identified by '123abc'
```
- Solution: Reset migrations:
```bash
rm -rf alembic/versions/*
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

1. **Tron API** Connection Issues
```log
    tronpy.exc.TronError: Failed to connect to Tron node
```
- Solution:
  - Check your internet connection
  - Verify Tron API endpoint in tron_service.py
  - Add retry logic for requests

1. Pre-commit Hooks Failing
```log
    black....................................................................Failed
```
- Solution: Run auto-formatting:
  ```bash
        black .
        isort .
  ```

1. Test Failures in CI
```log
    E   AssertionError: Unexpected status code: 500
```
- Solution:
  - Check test database setup in CI
  - Verify environment variables:
    ```yaml
    env:
        DATABASE_URL: sqlite+aiosqlite:///test_db.sqlite
        API_KEY: ${{ secrets.API_KEY }}
    ```
    
### Debugging Tips

1. View Detailed Logs
```bash
    docker-compose logs -f app
```

1. Check Database Contents
```bash
    sqlite3 sqlite_data/db.sqlite3 "SELECT * FROM wallet_queries LIMIT 5;"
```

1. Run Specific Tests
```bash
    pytest tests/test_api.py::test_wallet_info -v
```

1. Verify API Responses
```bash
    curl -v "http://localhost:8000/wallet-info?address=TEST_ADDRESS"
```

1. Reset Test Environment
```bash
    docker-compose down -v && docker-compose up --build
```

## License

Distributed under the MIT License. See [LICENSE](https://github.com/Sayrexxx/mattermost-voting-bot/blob/main/LICENSE) for more information.
