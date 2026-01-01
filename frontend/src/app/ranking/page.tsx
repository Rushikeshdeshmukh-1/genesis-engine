"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Trophy, TrendingUp } from "lucide-react";
import Link from "next/link";

export default function RankingPage() {
    const { data: ideas, isLoading } = useQuery({
        queryKey: ["ideas", "ranked"],
        queryFn: () => api.getIdeas({
            page: 1,
            page_size: 50,
            sort_by: "rank",
            sort_order: "asc",
        }),
    });

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
        );
    }

    const rankedIdeas = ideas?.ideas.filter((idea: any) => idea.rank) || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Top Ranked Ideas</h1>
                <p className="text-muted-foreground">
                    Ideas ranked by comprehensive scoring across 1000+ factors
                </p>
            </div>

            {/* Top 3 Podium */}
            {rankedIdeas.length >= 3 && (
                <div className="grid grid-cols-3 gap-4 mb-8">
                    {/* 2nd Place */}
                    <Link href={`/ideas/${rankedIdeas[1].id}`}>
                        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                            <CardHeader className="text-center pb-2">
                                <div className="mx-auto w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center mb-2">
                                    <span className="text-2xl font-bold text-gray-600">2</span>
                                </div>
                                <CardTitle className="text-lg line-clamp-2">
                                    {rankedIdeas[1].title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="text-center">
                                <div className="text-3xl font-bold text-gray-600 mb-2">
                                    {rankedIdeas[1].overall_score?.toFixed(1)}
                                </div>
                                <Badge variant="outline">{rankedIdeas[1].category}</Badge>
                            </CardContent>
                        </Card>
                    </Link>

                    {/* 1st Place */}
                    <Link href={`/ideas/${rankedIdeas[0].id}`}>
                        <Card className="hover:shadow-lg transition-shadow cursor-pointer border-yellow-400 border-2">
                            <CardHeader className="text-center pb-2">
                                <div className="mx-auto w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center mb-2">
                                    <Trophy className="w-10 h-10 text-white" />
                                </div>
                                <CardTitle className="text-xl line-clamp-2">
                                    {rankedIdeas[0].title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="text-center">
                                <div className="text-4xl font-bold text-yellow-600 mb-2">
                                    {rankedIdeas[0].overall_score?.toFixed(1)}
                                </div>
                                <Badge variant="outline">{rankedIdeas[0].category}</Badge>
                            </CardContent>
                        </Card>
                    </Link>

                    {/* 3rd Place */}
                    <Link href={`/ideas/${rankedIdeas[2].id}`}>
                        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                            <CardHeader className="text-center pb-2">
                                <div className="mx-auto w-16 h-16 rounded-full bg-orange-200 flex items-center justify-center mb-2">
                                    <span className="text-2xl font-bold text-orange-600">3</span>
                                </div>
                                <CardTitle className="text-lg line-clamp-2">
                                    {rankedIdeas[2].title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="text-center">
                                <div className="text-3xl font-bold text-orange-600 mb-2">
                                    {rankedIdeas[2].overall_score?.toFixed(1)}
                                </div>
                                <Badge variant="outline">{rankedIdeas[2].category}</Badge>
                            </CardContent>
                        </Card>
                    </Link>
                </div>
            )}

            {/* Full Ranking Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Complete Rankings</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        {rankedIdeas.map((idea: any) => (
                            <Link key={idea.id} href={`/ideas/${idea.id}`}>
                                <div className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer">
                                    <div className="w-12 text-center">
                                        <span className="text-2xl font-bold text-muted-foreground">
                                            #{idea.rank}
                                        </span>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="font-semibold">{idea.title}</h3>
                                        <p className="text-sm text-muted-foreground line-clamp-1">
                                            {idea.description}
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Badge variant="outline">{idea.category}</Badge>
                                        <Badge>{idea.status}</Badge>
                                    </div>
                                    <div className="text-right">
                                        <div className="flex items-center gap-1 text-lg font-bold text-green-600">
                                            <TrendingUp className="w-5 h-5" />
                                            {idea.overall_score?.toFixed(1)}
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>

                    {rankedIdeas.length === 0 && (
                        <div className="text-center py-12 text-muted-foreground">
                            No ranked ideas yet. Generate and score some ideas first!
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
