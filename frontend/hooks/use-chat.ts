"use client";

import { useState, useCallback } from "react";
import { createParser } from "eventsource-parser";
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
        const response = await fetch(`${apiUrl}/ask-stream`, {
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

        const parser = createParser({
          onEvent: (event) => {
            const data = event.data;

            if (data === "[DONE]") {
              return;
            }

            try {
              const parsed = JSON.parse(data);

              // Handle different response formats
              let contentChunk = "";
              if (parsed.content) {
                contentChunk = parsed.content;
              } else if (parsed.choices?.[0]?.delta?.content) {
                contentChunk = parsed.choices[0].delta.content;
              } else if (parsed.token) {
                contentChunk = parsed.token;
              } else if (typeof parsed === "string") {
                contentChunk = parsed;
              }

              if (contentChunk) {
                accumulatedContent += contentChunk;

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
              console.error("Failed to parse streaming data:", e, "Data:", data);
            }
          },
        });

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          parser.feed(chunk);
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
