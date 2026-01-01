"""
Temporal worker process.
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from app.config import settings
from app.workflows.idea_pipeline import IdeaPipelineWorkflow
from app.workflows.activities import (
    generate_ideas_activity,
    research_idea_activity,
    score_idea_activity,
    rank_ideas_activity,
    generate_report_activity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run the Temporal worker."""
    logger.info(f"Connecting to Temporal server at {settings.temporal_host}")
    
    # Connect to Temporal server
    client = await Client.connect(settings.temporal_host)
    
    logger.info(f"Starting worker on task queue: {settings.temporal_task_queue}")
    
    # Create worker
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[IdeaPipelineWorkflow],
        activities=[
            generate_ideas_activity,
            research_idea_activity,
            score_idea_activity,
            rank_ideas_activity,
            generate_report_activity,
        ],
    )
    
    logger.info("Worker started successfully")
    
    # Run worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
