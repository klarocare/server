from core.migrations import changelog_20250323175131

ALL_MIGRATIONS = [
    changelog_20250323175131.run,
]

async def run_migrations():
    for migration in ALL_MIGRATIONS:
        await migration()
