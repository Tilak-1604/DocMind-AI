# DocMind AI Service - Startup Guide

## Production Startup (Optimized with 8 workers)
```bash
cd /home/guna-abhishek/IdeaProjects/DocMind-AI/Ai-Service
./start.sh
```

## Development Startup (Single worker with auto-reload)
```bash
cd /home/guna-abhishek/IdeaProjects/DocMind-AI/Ai-Service
./start-dev.sh
```

## Manual Startup with Custom Configuration
```bash
# Adjust workers based on load
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Worker Count Guidelines
- **Light load (< 50 concurrent users)**: 2-4 workers
- **Medium load (50-200 users)**: 4-8 workers  ✅ DEFAULT
- **Heavy load (200+ users)**: 8-16 workers
- **Formula**: (2 × CPU_cores) + 1

## Performance Notes
- Each worker uses ~80-150MB RAM
- 8 workers = ~600MB-1.2GB total memory usage
- Workers share the database connection pool (20 connections)
- Ensure MySQL max_connections > (pool_size × workers) = 160+

## Installing uvloop (if not already installed)
```bash
pip install uvicorn[standard]
# or
pip install uvloop
```
