"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface ScoreBreakdownProps {
    score: any;
}

export function ScoreBreakdown({ score }: ScoreBreakdownProps) {
    const categories = [
        { name: "Market Demand", value: score.market_demand_score, color: "bg-blue-500" },
        { name: "Competition", value: score.competition_score, color: "bg-green-500" },
        { name: "Trend Strength", value: score.trend_strength_score, color: "bg-purple-500" },
        { name: "Revenue Potential", value: score.revenue_potential_score, color: "bg-yellow-500" },
        { name: "Tech Feasibility", value: score.tech_feasibility_score, color: "bg-indigo-500" },
        { name: "Cost to Build", value: score.cost_to_build_score, color: "bg-pink-500" },
        { name: "Risk Level", value: score.risk_level_score, color: "bg-red-500" },
        { name: "User Adoption", value: score.user_adoption_score, color: "bg-teal-500" },
        { name: "Scalability", value: score.scalability_score, color: "bg-cyan-500" },
        { name: "Innovation", value: score.innovation_score, color: "bg-orange-500" },
        { name: "Moat Strength", value: score.moat_strength_score, color: "bg-lime-500" },
        { name: "Operational Complexity", value: score.operational_complexity_score, color: "bg-amber-500" },
        { name: "Time to Market", value: score.time_to_market_score, color: "bg-emerald-500" },
        { name: "Team Requirements", value: score.team_requirements_score, color: "bg-violet-500" },
        { name: "Social Impact", value: score.social_impact_score, color: "bg-fuchsia-500" },
        { name: "Global Expansion", value: score.global_expansion_score, color: "bg-rose-500" },
    ];

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Score Breakdown by Category</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {categories.map((category) => (
                        <div key={category.name} className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="font-medium">{category.name}</span>
                                <span className="text-muted-foreground">
                                    {category.value?.toFixed(1) || "N/A"}
                                </span>
                            </div>
                            <Progress value={category.value || 0} className="h-2" />
                        </div>
                    ))}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Overall Metrics</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-sm text-muted-foreground">Overall Score</p>
                        <p className="text-2xl font-bold">{score.overall_score?.toFixed(1)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Normalized Score</p>
                        <p className="text-2xl font-bold">{score.normalized_score?.toFixed(1)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Percentile Rank</p>
                        <p className="text-2xl font-bold">
                            {score.percentile_rank ? `${score.percentile_rank.toFixed(0)}%` : "N/A"}
                        </p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Confidence</p>
                        <p className="text-2xl font-bold">
                            {score.confidence_score?.toFixed(0)}%
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
