# Weather ETL Pipeline – Daily Automated Data Ingestion & Orchestration

![Project Banner](screenshots/banner.png) 

A complete, production-ready **end-to-end ETL pipeline** built during my career transition from Data Science to Data Engineering.

- **Extracts** current weather data for Bournemouth, UK from OpenWeatherMap API  
- **Transforms** it (temperature conversion, rounding, quality flag)  
- **Loads** it into a Supabase PostgreSQL database  
- **Orchestrates & schedules** daily runs with **Prefect 3**  
- **Containerizes** the flow runner and persistent worker using **Docker**

This project was my first serious step into Data Engineering — built from zero prior DE experience with a lot of debugging persistence.

**Status**: Fully functional locally (Dockerized, scheduled, observable)

## Project Motivation & Goals

Coming from a Data Science background (analysis, modeling, pandas), I wanted a fast, tangible project to learn core Data Engineering skills:

- Reliable data movement & infrastructure  
- ETL processes (ingestion → transformation → loading)  
- Workflow orchestration & scheduling  
- Database integration (relational, real-world)  
- Containerization & local deployment  
- Debugging production-like issues (connections, networking, env files)

**Why weather data?**  
- Public, free API with generous limits  
- Structured, time-series data — easy to verify  
- Real-world analogy: daily external data feed (e.g. logistics, marketing, agriculture)

**Outcome**: A scheduled, retryable, observable pipeline that runs automatically and loads clean data into a database every day.

## Features

- Daily automated execution (configurable schedule, e.g. 8 AM UTC)
- Retries, logging, and error handling built into Prefect tasks
- Secure secret management via `.env`
- Full observability via Prefect UI (flow graph, run history, logs)
- Dockerized for reproducibility and easy deployment
- Simple but realistic: API → Pandas → PostgreSQL

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

```

## Architecture & Tech Stack

### High-Level Flow

1. **Extract** → OpenWeatherMap API (current weather endpoint)  
2. **Transform** → Pandas (cleaning, unit conversion, derived columns)  
3. **Load** → Supabase PostgreSQL (transaction pooler)  
4. **Orchestrate** → Prefect 3 (flows, tasks with retries, logging)  
5. **Schedule** → Cron (e.g. daily at 8 AM UTC)  
6. **Containerize** → Docker (flow runner + persistent worker)  
7. **Observe** → Prefect UI (graph, logs, run history)

### Tech Stack

| Layer                  | Technology                     | Purpose / Why Chosen                                      |
|------------------------|--------------------------------|-----------------------------------------------------------|
| Language               | Python 3.12                    | Familiar from DS, excellent DE ecosystem                  |
| API Client             | requests                       | Simple, reliable, battle-tested                           |
| Data Processing        | pandas                         | Fast, familiar for transformation                         |
| Database Client        | psycopg2-binary                | Direct PostgreSQL access, no ORM overhead                 |
| Secrets                | python-dotenv                  | Standard, easy local secret management                    |
| Orchestration          | Prefect 3                      | Python-native, simpler than Airflow, great local UI       |
| Containerization       | Docker                         | Industry standard for reproducibility & deployment        |
| Database               | Supabase (PostgreSQL)          | Free hosted Postgres with easy UI                         |
| Data Source            | OpenWeatherMap API             | Free tier, real structured weather data                   |

## Step-by-Step Build Journey (Including Real Challenges)

### Phase 1: Environment & Database Setup
- Installed core libraries in venv  
- Obtained OpenWeatherMap API key  
- Created Supabase project & table

**Biggest Challenge**: Repeated "Tenant or user not found" / "Connection refused" errors  
**Root Causes**: Wrong pooler mode (direct vs transaction), IPv6 issues, incorrect username/port  
**Resolution**: Switched to transaction pooler (port 6543), copied exact string from dashboard, tested with debug script  
**Lesson**: Always verify connection independently before building pipeline

### Phase 2: Core ETL Logic
- Wrote extract (API + DF), transform (cleaning), load (INSERT) functions

**Challenge**: `datetime.utcnow()` deprecation warning  
**Fix**: Switched to timezone-aware `datetime.now(timezone.utc).isoformat()`  
**Lesson**: Pay attention to Python version-specific warnings

### Phase 3: Prefect Orchestration & Scheduling
- Decorated functions with `@task` and `@flow`  
- Added retries and logging  
- Deployed via interactive `prefect deploy`

**Challenges**:  
- Old `prefect deploy -f` syntax no longer worked  
- Backlog of late/scheduled runs when worker offline  
**Fixes**: Used new interactive CLI, wrote bulk cancellation script, paused schedules when needed  
**Lesson**: Orchestration tools evolve — read latest docs

### Phase 4: Containerization (Docker)
- Created `Dockerfile` for flow & `worker.Dockerfile` for persistent worker  
- Built & tested images

**Challenges**:  
- "No such file or directory" → wrong working directory  
- Invalid `requirements.txt` → accidentally copied bash heredoc into file  
- "Connection refused" to Prefect server inside container  
**Fixes**: Changed to correct folder, cleaned requirements, used `host.docker.internal` on macOS  
**Lesson**: Docker networking differs by OS — test connectivity inside container

### Phase 5: Final Testing & Polish
- Verified daily runs load data to Supabase  
- Added screenshots, `.env.example`, `.gitignore`  
- Documented full setup & troubleshooting

## How to Run Locally

### Prerequisites
- Python 3.12+
- Docker Desktop
- OpenWeatherMap API key
- Supabase project with `weather_data` table

### Steps

1. Clone repo
```
   git clone https://github.com/YOUR-USERNAME/weather-etl-pipeline.git
   cd weather-etl-pipeline
```
