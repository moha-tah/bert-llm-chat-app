"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChatMessageList } from "@/components/chat/chat-message-list";
import { ChatInput } from "@/components/chat/chat-input";
import { useChat } from "@/hooks/use-chat";
import { Trash2, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function AskPage() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="w-full max-w-4xl flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
                <span className="sr-only">Back to home</span>
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">Ask Barfield AI</h1>
          </div>
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearMessages}
              disabled={isLoading}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        {/* Chat Container */}
        <Card className="flex flex-col h-[calc(100vh-200px)] max-h-[700px] overflow-hidden">
          {/* Error Message */}
          {error && (
            <div className="bg-destructive/10 text-destructive px-4 py-3 border-b border-destructive/20">
              <p className="text-sm">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {/* Messages */}
          <ChatMessageList messages={messages} isLoading={isLoading} />

          {/* Input */}
          <ChatInput
            onSend={sendMessage}
            disabled={isLoading}
            placeholder="Ask a question about your documents..."
          />
        </Card>
      </div>
    </div>
  );
}
