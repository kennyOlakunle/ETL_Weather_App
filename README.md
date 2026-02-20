# Weather ETL Pipeline – Daily Data Ingestion & Orchestration

A complete, production-ready **end-to-end ETL pipeline** that:

- **Extracts** current weather data for Bournemouth (UK) from the OpenWeatherMap API  
- **Transforms** the data (temperature conversion, rounding, quality checks)  
- **Loads** it into a Supabase PostgreSQL database  
- **Orchestrates & schedules** execution with **Prefect 3** (modern Python-native workflow engine)  
- **Containerizes** both the flow runner and the Prefect worker using **Docker**

This project demonstrates core Data Engineering skills: reliable data ingestion, transformation, loading, orchestration, observability, containerization, and local deployment.

## Features

- Daily automated execution (configurable schedule, e.g. 8 AM UTC)
- Retries, logging, and error handling built into Prefect tasks
- Secure secret management via `.env`
- Full observability via Prefect UI (flow graph, run history, logs)
- Dockerized for reproducibility and easy deployment
- Simple but realistic: API → Pandas → PostgreSQL

## Screenshots

### Prefect UI – Flow Graph
![Prefect Flow Graph](screenshots/prefect_flow_graph.png)

### Prefect UI – Successful Run
![Prefect Run Success](screenshots/prefect_run_success.png)

### Supabase Table – Loaded Weather Data
![Supabase Table](screenshots/supabase_table.png)

### Docker Worker Running
![Docker Worker Logs](screenshots/docker_worker_logs.png)

## Tech Stack

| Layer               | Technology                     | Purpose                                  |
|---------------------|--------------------------------|------------------------------------------|
| Language            | Python 3.12                    | Core scripting                           |
| Data Fetching       | requests                       | API calls to OpenWeatherMap              |
| Transformation      | pandas                         | Cleaning, rounding, derived columns      |
| Database            | Supabase (PostgreSQL)          | Persistent storage                       |
| Orchestration       | Prefect 3                      | Flows, tasks, retries, scheduling, UI    |
| Containerization    | Docker                         | Reproducible builds & execution          |
| Secrets             | python-dotenv                  | Secure API keys & connection strings     |
| Database Driver     | psycopg2-binary                | PostgreSQL connectivity                  |

## Prerequisites

- Python 3.12+
- Docker Desktop (or Docker Engine on Linux)
- Free OpenWeatherMap API key → https://home.openweathermap.org/api_keys
- Free Supabase project → https://supabase.com (create table `weather_data` as shown below)
- Prefect 3 (installed via pip)

### Supabase Table Creation (run once in SQL Editor)

```sql
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    city VARCHAR(100) NOT NULL,
    temp_kelvin NUMERIC(6,2),
    temp_celsius NUMERIC(6,2),
    humidity INTEGER,
    description VARCHAR(255),
    data_quality VARCHAR(50)
);

### Step-by-Step Local Setup

**1. Clone the repository

```
git clone https://github.com/YOUR-USERNAME/weather-etl-pipeline.git
cd weather-etl-pipeline
```

Replace `YOUR-USERNAME` with your actual GitHub username.

