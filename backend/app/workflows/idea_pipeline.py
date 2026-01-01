"""
Temporal workflow definitions for the idea pipeline.
"""

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
import logging

logger = logging.getLogger(__name__)


@workflow.defn
class IdeaPipelineWorkflow:
    """
    Main workflow orchestrating the complete idea generation and evaluation pipeline.
    
    Steps:
    1. Generate ideas
    2. Research each idea
    3. Score each idea
    4. Rank all ideas
    5. Generate reports
    """
    
    @workflow.run
    async def run(self, params: dict) -> dict:
        """
        Execute the complete pipeline.
        
        Args:
            params: Pipeline parameters
                - idea_count: Number of ideas to generate
                - category: Optional category filter
                - auto_research: Whether to auto-research
                - auto_score: Whether to auto-score
                - auto_rank: Whether to auto-rank
                - auto_report: Whether to auto-generate reports
        
        Returns:
            Pipeline execution results
        """
        workflow.logger.info(f"Starting idea pipeline with params: {params}")
        
        idea_count = params.get("idea_count", 10)
        category = params.get("category")
        auto_research = params.get("auto_research", True)
        auto_score = params.get("auto_score", True)
        auto_rank = params.get("auto_rank", True)
        auto_report = params.get("auto_report", False)
        
        results = {
            "idea_ids": [],
            "research_completed": 0,
            "scores_completed": 0,
            "reports_generated": 0,
            "status": "running"
        }
        
        try:
            # Step 1: Generate ideas
            workflow.logger.info(f"Generating {idea_count} ideas")
            idea_generation_result = await workflow.execute_activity(
                "generate_ideas_activity",
                args=[{"count": idea_count, "category": category}],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                )
            )
            
            results["idea_ids"] = idea_generation_result["idea_ids"]
            workflow.logger.info(f"Generated {len(results['idea_ids'])} ideas")
            
            # Step 2: Research ideas (if enabled)
            if auto_research and results["idea_ids"]:
                workflow.logger.info("Starting research phase")
                for idea_id in results["idea_ids"]:
                    try:
                        await workflow.execute_activity(
                            "research_idea_activity",
                            args=[{"idea_id": idea_id}],
                            start_to_close_timeout=timedelta(minutes=15),
                            retry_policy=RetryPolicy(
                                maximum_attempts=2,
                                initial_interval=timedelta(seconds=2),
                            )
                        )
                        results["research_completed"] += 1
                    except Exception as e:
                        workflow.logger.error(f"Research failed for idea {idea_id}: {e}")
                
                workflow.logger.info(f"Completed research for {results['research_completed']} ideas")
            
            # Step 3: Score ideas (if enabled)
            if auto_score and results["idea_ids"]:
                workflow.logger.info("Starting scoring phase")
                for idea_id in results["idea_ids"]:
                    try:
                        await workflow.execute_activity(
                            "score_idea_activity",
                            args=[{"idea_id": idea_id}],
                            start_to_close_timeout=timedelta(minutes=20),
                            retry_policy=RetryPolicy(
                                maximum_attempts=2,
                                initial_interval=timedelta(seconds=2),
                            )
                        )
                        results["scores_completed"] += 1
                    except Exception as e:
                        workflow.logger.error(f"Scoring failed for idea {idea_id}: {e}")
                
                workflow.logger.info(f"Completed scoring for {results['scores_completed']} ideas")
            
            # Step 4: Rank ideas (if enabled)
            if auto_rank and results["scores_completed"] > 0:
                workflow.logger.info("Ranking ideas")
                await workflow.execute_activity(
                    "rank_ideas_activity",
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )
            
            # Step 5: Generate reports (if enabled)
            if auto_report and results["idea_ids"]:
                workflow.logger.info("Generating reports")
                for idea_id in results["idea_ids"][:5]:  # Limit to top 5
                    try:
                        await workflow.execute_activity(
                            "generate_report_activity",
                            args=[{"idea_id": idea_id, "format": "markdown"}],
                            start_to_close_timeout=timedelta(minutes=10),
                            retry_policy=RetryPolicy(maximum_attempts=2)
                        )
                        results["reports_generated"] += 1
                    except Exception as e:
                        workflow.logger.error(f"Report generation failed for idea {idea_id}: {e}")
            
            results["status"] = "completed"
            workflow.logger.info("Pipeline completed successfully")
            
        except Exception as e:
            workflow.logger.error(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
