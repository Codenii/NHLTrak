# NHLTRAK


## Overview

descript.

## Features
- 


---

## Pre-Requisites

- [Docker](https://docs.docker.com/get-docker/)


## Quickstart

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Codenii/NHLTrak.git
    cd NHLTRAk
    ```

2. **Start everything (API + database):**
    ```bash
    docker compose up
    ```
   This runs the FastAPI backend and a Postgres database in linked containers.  
   - The API server will be accessible at [http://localhost:8000](http://localhost:8000).
   - Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Configuration  
- Database connection and environment variables can be adjusted in `docker-compose.yml`.
- If you need to reset database state, stop containers and remove the `db_data` volume.

## Development notes  
- Hot-reloading is enabled by default for API code changes.  
- Attach to the running container with `docker-compose exec app bash` if you need shell access.
- All code is mounted live from your machine into the container.






