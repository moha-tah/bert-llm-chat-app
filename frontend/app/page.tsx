import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <main className="flex flex-col items-center justify-center gap-8 p-8 text-center">
        <div className="flex flex-col items-center gap-4">
          <h1 className="text-6xl font-bold tracking-tight">
            Ask Barfield AI
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Your intelligent document assistant powered by advanced language models
          </p>
        </div>

        <Link href="/ask">
          <Button size="lg" className="text-lg px-8 py-6 h-auto">
            <MessageSquare className="mr-2 h-5 w-5" />
            Start Chatting
          </Button>
        </Link>
      </main>
    </div>
  );
}
