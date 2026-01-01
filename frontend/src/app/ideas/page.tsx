"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Lightbulb, TrendingUp, Loader2, Plus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

export default function IdeasPage() {
    const [page, setPage] = useState(1);
    const [category, setCategory] = useState<string>("all");
    const [sortBy, setSortBy] = useState("created_at");
    const [generating, setGenerating] = useState(false);

    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ["ideas", page, category, sortBy],
        queryFn: () => api.getIdeas({
            page,
            page_size: 20,
            category: category === "all" ? undefined : category,
            sort_by: sortBy,
            sort_order: "desc",
        }),
    });

    const generateMutation = useMutation({
        mutationFn: (count: number) => api.generateIdeas({ count }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["ideas"] });
            setGenerating(false);
        },
    });

    const handleGenerate = () => {
        setGenerating(true);
        generateMutation.mutate(20);
    };

    const getStatusColor = (status: string) => {
        const colors: Record<string, string> = {
            generated: "bg-gray-500",
            researched: "bg-blue-500",
            scored: "bg-green-500",
            ranked: "bg-purple-500",
        };
        return colors[status] || "bg-gray-500";
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Business Ideas</h1>
                    <p className="text-muted-foreground">
                        Browse and manage generated business ideas
                    </p>
                </div>
                <Button onClick={handleGenerate} disabled={generating} className="gap-2">
                    {generating ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Generating...
                        </>
                    ) : (
                        <>
                            <Plus className="w-4 h-4" />
                            Generate Ideas
                        </>
                    )}
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardHeader>
                    <CardTitle>Filters</CardTitle>
                </CardHeader>
                <CardContent className="flex gap-4">
                    <div className="flex-1">
                        <Input
                            placeholder="Search ideas..."
                            className="w-full"
                        />
                    </div>
                    <Select value={category} onValueChange={setCategory}>
                        <SelectTrigger className="w-[200px]">
                            <SelectValue placeholder="All Categories" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Categories</SelectItem>
                            <SelectItem value="SaaS">SaaS</SelectItem>
                            <SelectItem value="Marketplace">Marketplace</SelectItem>
                            <SelectItem value="AI/ML">AI/ML</SelectItem>
                            <SelectItem value="FinTech">FinTech</SelectItem>
                            <SelectItem value="HealthTech">HealthTech</SelectItem>
                        </SelectContent>
                    </Select>
                    <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger className="w-[200px]">
                            <SelectValue placeholder="Sort by" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="created_at">Newest</SelectItem>
                            <SelectItem value="overall_score">Highest Score</SelectItem>
                            <SelectItem value="rank">Best Ranked</SelectItem>
                        </SelectContent>
                    </Select>
                </CardContent>
            </Card>

            {/* Ideas Grid */}
            {isLoading ? (
                <div className="flex justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {data?.ideas.map((idea: any) => (
                            <Link key={idea.id} href={`/ideas/${idea.id}`}>
                                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                                    <CardHeader>
                                        <div className="flex justify-between items-start mb-2">
                                            <Badge className={getStatusColor(idea.status)}>
                                                {idea.status}
                                            </Badge>
                                            {idea.overall_score && (
                                                <div className="flex items-center gap-1 text-sm font-semibold">
                                                    <TrendingUp className="w-4 h-4 text-green-600" />
                                                    {idea.overall_score.toFixed(1)}
                                                </div>
                                            )}
                                        </div>
                                        <CardTitle className="line-clamp-2">{idea.title}</CardTitle>
                                        <CardDescription className="line-clamp-3">
                                            {idea.description}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex flex-wrap gap-2">
                                            {idea.category && (
                                                <Badge variant="outline">{idea.category}</Badge>
                                            )}
                                            {idea.tags?.slice(0, 2).map((tag: string) => (
                                                <Badge key={tag} variant="secondary">
                                                    {tag}
                                                </Badge>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            </Link>
                        ))}
                    </div>

                    {/* Pagination */}
                    {data && data.total > 20 && (
                        <div className="flex justify-center gap-2 mt-6">
                            <Button
                                variant="outline"
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                Previous
                            </Button>
                            <span className="flex items-center px-4">
                                Page {page} of {Math.ceil(data.total / 20)}
                            </span>
                            <Button
                                variant="outline"
                                onClick={() => setPage(p => p + 1)}
                                disabled={page >= Math.ceil(data.total / 20)}
                            >
                                Next
                            </Button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
