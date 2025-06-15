from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore  # Используем хранилище в памяти

scheduler = AsyncIOScheduler(jobstores={'default': MemoryJobStore()})  # Планировщик в памяти
