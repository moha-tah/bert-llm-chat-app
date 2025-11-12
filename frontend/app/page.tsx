"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Github, PlaneTakeoff } from "lucide-react";
import { useTheme } from "next-themes";

export default function Home() {
  const { theme } = useTheme();

  return (
    <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-background via-background to-secondary/20">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <main className="flex flex-col items-center justify-center gap-8 p-8 text-center max-w-4xl">
        <div className="flex flex-col items-center gap-6">
          <div
            className={`flex items-center gap-3 rounded-md p-2 ${
              theme === "dark" ? "bg-white" : ""
            }`}
          >
            <Image
              src="/images/barfield-logo.png"
              alt="Barfield Logo"
              width={300}
              height={60}
              priority
              className="h-16 w-auto"
            />
          </div>
          <h1 className="text-6xl font-bold tracking-tight text-primary">
            Ask Barfield AI
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl leading-relaxed">
            Your AI assistant powered by BERT, LLaMA and RAG technology, hosted
            on AWS App Runner with a Docker image in an Elastic Container
            Registry.
          </p>
          <p className="text-sm text-muted-foreground italic">
            Powered by Mohamed Tahiri, for Barfield Inc. (Air France)
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <Link
            href="https://github.com/moha-tah/bert-llm-chat-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-8 py-6 h-auto"
            >
              <Github className="mr-2 h-5 w-5" />
              View Docs and Code on GitHub
            </Button>
          </Link>
          <Link href="/ask">
            <Button size="lg" className="text-lg px-8 py-6 h-auto">
              <PlaneTakeoff className="mr-2 h-5 w-5" />
              Start Chatting
            </Button>
          </Link>
        </div>

        <div className="mt-8 text-xs text-muted-foreground">
          <p>
            This is a demonstration project showcasing RAG (Retrieval-Augmented
            Generation) technology
          </p>
        </div>
      </main>
    </div>
  );
}
