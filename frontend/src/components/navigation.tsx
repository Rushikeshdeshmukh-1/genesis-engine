"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Lightbulb, Search, BarChart3, FileText, Home } from "lucide-react";

const navigation = [
    { name: "Home", href: "/", icon: Home },
    { name: "Ideas", href: "/ideas", icon: Lightbulb },
    { name: "Research", href: "/research", icon: Search },
    { name: "Ranking", href: "/ranking", icon: BarChart3 },
    { name: "Reports", href: "/reports", icon: FileText },
];

export function Navigation() {
    const pathname = usePathname();

    return (
        <nav className="border-b bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Lightbulb className="w-8 h-8 text-blue-600" />
                        <span className="text-xl font-bold">Idea Engine</span>
                    </div>

                    <div className="flex gap-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;

                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                                        isActive
                                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-100"
                                            : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                                    )}
                                >
                                    <Icon className="w-4 h-4" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>
        </nav>
    );
}
