"use client";

import { Card } from "@/components/ui/card";
import { defaultPrompts } from "@/lib/default-prompts";

interface DefaultPromptsProps {
  onPromptSelect: (prompt: string) => void;
}

export function DefaultPrompts({ onPromptSelect }: DefaultPromptsProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 p-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-foreground">Ask me anything</h2>
        <p className="text-muted-foreground">
          Select a prompt below or type your own question
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
        {defaultPrompts.map((prompt) => (
          <Card
            key={prompt.id}
            className="p-4 cursor-pointer hover:bg-accent/10 hover:border-accent transition-colors"
            onClick={() => onPromptSelect(prompt.prompt)}
          >
            <div className="space-y-2">
              {prompt.category && (
                <span className="text-xs font-medium text-primary/70">
                  {prompt.category}
                </span>
              )}
              <h3 className="font-semibold text-foreground">{prompt.title}</h3>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {prompt.prompt}
              </p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
