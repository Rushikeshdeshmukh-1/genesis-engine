"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, TrendingUp, Search, BarChart3, FileText, Play } from "lucide-react";
import { useParams } from "next/navigation";
import { ScoreBreakdown } from "@/components/score-breakdown";

export default function IdeaDetailPage() {
    const params = useParams();
    const ideaId = params.id as string;
    const queryClient = useQueryClient();

    const { data: idea, isLoading } = useQuery({
        queryKey: ["idea", ideaId],
        queryFn: () => api.getIdea(ideaId),
    });

    const { data: research } = useQuery({
        queryKey: ["research", ideaId],
        queryFn: () => api.getResearch(ideaId),
        enabled: !!idea && idea.status !== "generated",
    });

    const { data: score } = useQuery({
        queryKey: ["score", ideaId],
        queryFn: () => api.getScore(ideaId),
        enabled: !!idea && (idea.status === "scored" || idea.status === "ranked"),
    });

    const researchMutation = useMutation({
        mutationFn: () => api.startResearch(ideaId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
            queryClient.invalidateQueries({ queryKey: ["research", ideaId] });
        },
    });

    const scoreMutation = useMutation({
        mutationFn: () => api.scoreIdea(ideaId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
            queryClient.invalidateQueries({ queryKey: ["score", ideaId] });
        },
    });

    const reportMutation = useMutation({
        mutationFn: () => api.generateReport(ideaId, "markdown"),
    });

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!idea) {
        return <div>Idea not found</div>;
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <div className="flex items-center gap-2 mb-2">
                    <Badge>{idea.status}</Badge>
                    {idea.category && <Badge variant="outline">{idea.category}</Badge>}
                </div>
                <h1 className="text-4xl font-bold mb-2">{idea.title}</h1>
                <p className="text-lg text-muted-foreground">{idea.description}</p>
            </div>

            {/* Score Card */}
            {idea.overall_score && (
                <Card>
                    <CardHeader>
                        <CardTitle>Overall Score</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4">
                            <div className="text-5xl font-bold text-green-600">
                                {idea.overall_score.toFixed(1)}
                            </div>
                            <div className="flex-1">
                                <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                                        style={{ width: `${idea.overall_score}%` }}
                                    />
                                </div>
                                <p className="text-sm text-muted-foreground mt-2">
                                    {idea.rank && `Ranked #${idea.rank}`}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Actions */}
            <div className="flex gap-2">
                <Button
                    onClick={() => researchMutation.mutate()}
                    disabled={researchMutation.isPending}
                    variant="outline"
                    className="gap-2"
                >
                    {researchMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Search className="w-4 h-4" />
                    )}
                    {idea.status === "generated" ? "Start Research" : "Re-research"}
                </Button>
                <Button
                    onClick={() => scoreMutation.mutate()}
                    disabled={scoreMutation.isPending || idea.status === "generated"}
                    variant="outline"
                    className="gap-2"
                >
                    {scoreMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <BarChart3 className="w-4 h-4" />
                    )}
                    Score Idea
                </Button>
                <Button
                    onClick={() => reportMutation.mutate()}
                    disabled={reportMutation.isPending}
                    variant="outline"
                    className="gap-2"
                >
                    {reportMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <FileText className="w-4 h-4" />
                    )}
                    Generate Report
                </Button>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="details" className="w-full">
                <TabsList>
                    <TabsTrigger value="details">Details</TabsTrigger>
                    <TabsTrigger value="research">Research</TabsTrigger>
                    <TabsTrigger value="scoring">Scoring</TabsTrigger>
                </TabsList>

                <TabsContent value="details" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Problem Statement</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>{idea.problem_statement || "Not available"}</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Target Audience</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>{idea.target_audience || "Not specified"}</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Value Proposition</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>{idea.value_proposition || "Not specified"}</p>
                        </CardContent>
                    </Card>

                    {idea.tags && idea.tags.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Tags</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-2">
                                    {idea.tags.map((tag: string) => (
                                        <Badge key={tag} variant="secondary">
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="research" className="space-y-4">
                    {research && research.length > 0 ? (
                        research.map((artifact: any) => (
                            <Card key={artifact.id}>
                                <CardHeader>
                                    <CardTitle>{artifact.title}</CardTitle>
                                    <CardDescription>
                                        Type: {artifact.research_type} • Confidence: {artifact.confidence_score}%
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p>{artifact.summary}</p>
                                </CardContent>
                            </Card>
                        ))
                    ) : (
                        <Card>
                            <CardContent className="py-12 text-center text-muted-foreground">
                                No research data available. Click "Start Research" to begin.
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="scoring">
                    {score ? (
                        <ScoreBreakdown score={score} />
                    ) : (
                        <Card>
                            <CardContent className="py-12 text-center text-muted-foreground">
                                No scoring data available. Complete research first, then click "Score Idea".
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
