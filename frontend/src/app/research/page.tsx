"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Search, Building2, TrendingUp } from "lucide-react";
import { useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function ResearchPage() {
    const [selectedIdea, setSelectedIdea] = useState<string>("");

    const { data: ideas } = useQuery({
        queryKey: ["ideas", "researched"],
        queryFn: () => api.getIdeas({
            page: 1,
            page_size: 100,
            status: "researched",
        }),
    });

    const { data: research, isLoading: researchLoading } = useQuery({
        queryKey: ["research", selectedIdea],
        queryFn: () => api.getResearch(selectedIdea),
        enabled: !!selectedIdea,
    });

    const { data: competitors } = useQuery({
        queryKey: ["competitors", selectedIdea],
        queryFn: () => api.getCompetitors(selectedIdea),
        enabled: !!selectedIdea,
    });

    const { data: market } = useQuery({
        queryKey: ["market", selectedIdea],
        queryFn: () => api.getMarketResearch(selectedIdea),
        enabled: !!selectedIdea,
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Research Artifacts</h1>
                <p className="text-muted-foreground">
                    View detailed research data for business ideas
                </p>
            </div>

            {/* Idea Selector */}
            <Card>
                <CardHeader>
                    <CardTitle>Select an Idea</CardTitle>
                </CardHeader>
                <CardContent>
                    <Select value={selectedIdea} onValueChange={setSelectedIdea}>
                        <SelectTrigger>
                            <SelectValue placeholder="Choose an idea to view research..." />
                        </SelectTrigger>
                        <SelectContent>
                            {ideas?.ideas.map((idea: any) => (
                                <SelectItem key={idea.id} value={idea.id}>
                                    {idea.title}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </CardContent>
            </Card>

            {selectedIdea && (
                <>
                    {/* Research Artifacts */}
                    {researchLoading ? (
                        <div className="flex justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                        </div>
                    ) : (
                        <>
                            {/* General Research */}
                            {research && research.length > 0 && (
                                <div className="space-y-4">
                                    <h2 className="text-2xl font-bold">Research Findings</h2>
                                    {research.map((artifact: any) => (
                                        <Card key={artifact.id}>
                                            <CardHeader>
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <CardTitle>{artifact.title}</CardTitle>
                                                        <CardDescription>
                                                            Type: {artifact.research_type}
                                                        </CardDescription>
                                                    </div>
                                                    <Badge>
                                                        Confidence: {artifact.confidence_score}%
                                                    </Badge>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-muted-foreground">{artifact.summary}</p>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}

                            {/* Competitor Analysis */}
                            {competitors && competitors.length > 0 && (
                                <div className="space-y-4">
                                    <h2 className="text-2xl font-bold flex items-center gap-2">
                                        <Building2 className="w-6 h-6" />
                                        Competitor Analysis
                                    </h2>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {competitors.map((comp: any) => (
                                            <Card key={comp.id}>
                                                <CardHeader>
                                                    <CardTitle>{comp.name}</CardTitle>
                                                    <CardDescription>
                                                        {comp.market_position && (
                                                            <Badge variant="outline">{comp.market_position}</Badge>
                                                        )}
                                                    </CardDescription>
                                                </CardHeader>
                                                <CardContent className="space-y-4">
                                                    {comp.url && (
                                                        <a
                                                            href={comp.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-sm text-blue-600 hover:underline"
                                                        >
                                                            {comp.url}
                                                        </a>
                                                    )}
                                                    <p className="text-sm">{comp.description}</p>

                                                    {comp.strengths && comp.strengths.length > 0 && (
                                                        <div>
                                                            <h4 className="font-semibold text-sm mb-2">Strengths</h4>
                                                            <ul className="text-sm text-muted-foreground list-disc list-inside">
                                                                {comp.strengths.map((s: string, i: number) => (
                                                                    <li key={i}>{s}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}

                                                    {comp.weaknesses && comp.weaknesses.length > 0 && (
                                                        <div>
                                                            <h4 className="font-semibold text-sm mb-2">Weaknesses</h4>
                                                            <ul className="text-sm text-muted-foreground list-disc list-inside">
                                                                {comp.weaknesses.map((w: string, i: number) => (
                                                                    <li key={i}>{w}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Market Research */}
                            {market && (
                                <div className="space-y-4">
                                    <h2 className="text-2xl font-bold flex items-center gap-2">
                                        <TrendingUp className="w-6 h-6" />
                                        Market Analysis
                                    </h2>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>TAM</CardTitle>
                                                <CardDescription>Total Addressable Market</CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-2xl font-bold">{market.tam}</p>
                                            </CardContent>
                                        </Card>
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>SAM</CardTitle>
                                                <CardDescription>Serviceable Addressable Market</CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-2xl font-bold">{market.sam}</p>
                                            </CardContent>
                                        </Card>
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>SOM</CardTitle>
                                                <CardDescription>Serviceable Obtainable Market</CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-2xl font-bold">{market.som}</p>
                                            </CardContent>
                                        </Card>
                                    </div>

                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Market Insights</CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            <div>
                                                <h4 className="font-semibold mb-2">Growth Rate</h4>
                                                <p className="text-muted-foreground">{market.growth_rate}</p>
                                            </div>

                                            {market.trends && market.trends.length > 0 && (
                                                <div>
                                                    <h4 className="font-semibold mb-2">Market Trends</h4>
                                                    <ul className="text-muted-foreground list-disc list-inside">
                                                        {market.trends.map((trend: string, i: number) => (
                                                            <li key={i}>{trend}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {market.drivers && market.drivers.length > 0 && (
                                                <div>
                                                    <h4 className="font-semibold mb-2">Market Drivers</h4>
                                                    <ul className="text-muted-foreground list-disc list-inside">
                                                        {market.drivers.map((driver: string, i: number) => (
                                                            <li key={i}>{driver}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                </div>
                            )}
                        </>
                    )}
                </>
            )}

            {!selectedIdea && (
                <Card>
                    <CardContent className="py-12 text-center text-muted-foreground">
                        <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Select an idea above to view its research data</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
