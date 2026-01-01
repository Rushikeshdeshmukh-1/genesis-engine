import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Navigation } from "@/components/navigation";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Idea Engine - Business Idea Generator & Research Platform",
    description: "Generate, research, score, and rank unlimited tech business ideas using AI",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <Providers>
                    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-blue-950">
                        <Navigation />
                        <main className="container mx-auto px-4 py-8">
                            {children}
                        </main>
                    </div>
                </Providers>
            </body>
        </html>
    );
}
