"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Github, Info, PlaneTakeoff } from "lucide-react";
import { useTheme } from "next-themes";

export default function Home() {
  const { theme } = useTheme();

  return (
    <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-background via-background to-primary/20">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <main className="flex flex-col items-center justify-center gap-8 p-8 text-center max-w-4xl">
        {/* New Feature Notification */}
        <div className="w-full max-w-2xl bg-accent/10 border-l-4 border-accent p-4 rounded shadow-sm text-left">
          <div className="flex">
            <div className="shrink-0">
              <Info className="h-5 w-5 text-accent" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                <span className="font-bold">New:</span> Click on the red button
                on the bottom right to test the new &quot;AI Support Agent&quot;
                feature.
              </p>
            </div>
          </div>
        </div>

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

        <div className="flex flex-col sm:flex-row gap-4 items-center w-full sm:w-auto">
          <Link
            href="https://github.com/moha-tah/bert-llm-chat-app"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full sm:w-auto"
          >
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-8 py-6 h-auto w-full sm:w-auto"
            >
              <Github className="mr-2 h-5 w-5" />
              View Docs and Code on GitHub
            </Button>
          </Link>
          <Link href="/ask" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="text-lg px-8 py-6 h-auto w-full sm:w-auto"
            >
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
