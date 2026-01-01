"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Lightbulb, TrendingUp, Target, Zap } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
    const { data: stats } = useQuery({
        queryKey: ["stats"],
        queryFn: () => api.getStats(),
    });

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-4 py-12">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Unlimited Tech Business Ideas
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                    Generate, research, score, and rank business ideas using AI-powered multi-agent system
                </p>
                <div className="flex gap-4 justify-center pt-4">
                    <Link href="/ideas">
                        <Button size="lg" className="gap-2">
                            <Lightbulb className="w-5 h-5" />
                            View Ideas
                        </Button>
                    </Link>
                    <Link href="/ideas?generate=true">
                        <Button size="lg" variant="outline" className="gap-2">
                            <Zap className="w-5 h-5" />
                            Generate New Ideas
                        </Button>
                    </Link>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Ideas</CardTitle>
                        <Lightbulb className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_ideas || 0}</div>
                        <p className="text-xs text-muted-foreground">
                            Generated and analyzed
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                        <Target className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {stats?.average_score ? stats.average_score.toFixed(1) : "N/A"}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Across all ideas
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Scored Ideas</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {stats?.by_status?.scored || 0}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Fully evaluated
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>AI-Powered Generation</CardTitle>
                        <CardDescription>
                            Generate unlimited business ideas using advanced LLM technology
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>✓ Context-aware idea generation</li>
                            <li>✓ Trend-based suggestions</li>
                            <li>✓ Category filtering</li>
                            <li>✓ Customizable parameters</li>
                        </ul>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Deep Research</CardTitle>
                        <CardDescription>
                            Automated research using web scraping and AI analysis
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>✓ Competitor analysis</li>
                            <li>✓ Market sizing</li>
                            <li>✓ Trend identification</li>
                            <li>✓ Technology feasibility</li>
                        </ul>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>1000-Factor Scoring</CardTitle>
                        <CardDescription>
                            Comprehensive evaluation across 16 major categories
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>✓ Market demand analysis</li>
                            <li>✓ Competition assessment</li>
                            <li>✓ Revenue potential</li>
                            <li>✓ Risk evaluation</li>
                        </ul>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Detailed Reports</CardTitle>
                        <CardDescription>
                            Professional business analysis reports
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li>✓ Executive summaries</li>
                            <li>✓ Opportunity analysis</li>
                            <li>✓ Risk assessment</li>
                            <li>✓ PDF/Markdown export</li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
