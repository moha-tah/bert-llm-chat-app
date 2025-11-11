"use client";

import { useState, useCallback } from "react";
import type { Message } from "@/components/chat/chat-message";

interface UseChatOptions {
  apiUrl?: string;
}

export function useChat(options: UseChatOptions = {}) {
  const {
    apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: content.trim(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiUrl}/ask`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: content.trim(),
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Response body is not readable");
        }

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "",
        };

        setMessages((prev) => [...prev, assistantMessage]);

        let accumulatedContent = "";

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();

              if (data === "[DONE]") {
                continue;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  accumulatedContent += parsed.content;

                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === "assistant") {
                      lastMessage.content = accumulatedContent;
                    }
                    return newMessages;
                  });
                }
              } catch (e) {
                // Skip invalid JSON
                console.error("Failed to parse streaming data:", e);
              }
            }
          }
        }

        setIsLoading(false);
      } catch (err) {
        console.error("Error sending message:", err);
        setError(err instanceof Error ? err.message : "An error occurred");
        setIsLoading(false);

        // Remove the assistant message if there was an error
        setMessages((prev) => prev.slice(0, -1));
      }
    },
    [apiUrl]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  };
}
