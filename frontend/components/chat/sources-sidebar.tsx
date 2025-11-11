"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface Source {
  name: string;
  filename: string;
}

export function SourcesSidebar() {
  const [sources, setSources] = React.useState<Source[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Fetch list of PDF files from the public/files directory
    // In a real scenario, you'd have an API endpoint that lists files
    // For now, we'll hardcode the known files
    const knownSources: Source[] = [
      {
        name: "Air France Presentation",
        filename: "air-france-presentation.pdf",
      },
      {
        name: "Aeronautics Introduction",
        filename: "aeronautics-introduction.pdf",
      },
      {
        name: "Barfield TT1200A Specifications",
        filename: "barfield-tt1200a.pdf",
      },
      {
        name: "Attention Is All You Need",
        filename: "attention-is-all-you-need.pdf",
      },
    ];

    setSources(knownSources);
    setLoading(false);
  }, []);

  const handleSourceClick = (filename: string) => {
    window.open(`/files/${filename}`, "_blank", "noopener,noreferrer");
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileText className="h-5 w-5" />
          Available Sources
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {loading ? (
          <div className="text-sm text-muted-foreground">
            Loading sources...
          </div>
        ) : sources.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No sources available
          </div>
        ) : (
          sources.map((source) => (
            <button
              key={source.filename}
              onClick={() => handleSourceClick(source.filename)}
              className={cn(
                "w-full flex items-center gap-2 p-3 rounded-lg text-left",
                "border border-border bg-card hover:bg-accent hover:text-accent-foreground",
                "transition-colors cursor-pointer group"
              )}
            >
              <FileText className="h-4 w-4 shrink-0 text-muted-foreground group-hover:text-accent-foreground" />
              <span className="flex-1 text-sm truncate">{source.name}</span>
              <ExternalLink className="h-3 w-3 shrink-0 text-muted-foreground group-hover:text-accent-foreground" />
            </button>
          ))
        )}
      </CardContent>
    </Card>
  );
}
