"use client";

import { useChat } from "@ai-sdk/react";
import { useState, useEffect } from "react";
import { IntakeSchema, type Intake } from "@/lib/intake-schema";
import type { UIMessage } from "ai";
import { TextStreamChatTransport } from "ai";

/**
 * Helper function to extract text content from a UIMessage
 */
export function getMessageText(message: UIMessage): string {
  return message.parts
    .filter((part) => part.type === "text")
    .map((part) => (part as { type: "text"; text: string }).text)
    .join("");
}

/**
 * Custom hook for managing the support intake chat
 *
 * This hook wraps the Vercel AI SDK's useChat hook and adds:
 * - Automatic detection of final JSON output
 * - Zod validation of extracted data
 * - Completion state management
 */
export function useSupportChat() {
  const [extractedData, setExtractedData] = useState<Intake | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const chat = useChat({
    transport: new TextStreamChatTransport({
      api: "/api/support",
    }),
  });

  // Monitor the last assistant message for final JSON output
  useEffect(() => {
    if (chat.messages.length === 0) return;

    const lastMessage = chat.messages[chat.messages.length - 1];

    // Only check assistant messages
    if (lastMessage.role !== "assistant") return;

    // Extract text content from message parts
    const messageText = getMessageText(lastMessage);

    // Try to extract and validate JSON from the message
    const result = tryExtractIntakeJSON(messageText);

    if (result.valid && result.data) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setExtractedData(result.data);
      setIsComplete(true);
      setValidationError(null);
    } else if (result.attempted) {
      // JSON was found but validation failed
      setValidationError(result.error || "Invalid data format");
    }
  }, [chat.messages]);

  /**
   * Reset the chat and clear all state
   */
  const reset = () => {
    chat.setMessages([]);
    setExtractedData(null);
    setIsComplete(false);
    setValidationError(null);
  };

  /**
   * Resume the chat to allow corrections
   */
  const resume = () => {
    setIsComplete(false);
  };

  const isLoading = chat.status === "submitted" || chat.status === "streaming";

  return {
    messages: chat.messages,
    sendMessage: chat.sendMessage,
    isLoading,
    extractedData,
    isComplete,
    validationError,
    reset,
    resume,
  };
}

/**
 * Attempts to extract and validate JSON from a message
 */
function tryExtractIntakeJSON(text: string): {
  valid: boolean;
  attempted: boolean;
  data?: Intake;
  error?: string;
} {
  try {
    // Look for JSON object in the text
    const jsonMatch = text.match(/\{[\s\S]*\}/);

    if (!jsonMatch) {
      return { valid: false, attempted: false };
    }

    // Found JSON, now try to parse it
    const parsed = JSON.parse(jsonMatch[0]);

    // Validate against Zod schema
    const validated = IntakeSchema.parse(parsed);

    return { valid: true, attempted: true, data: validated };
  } catch (error) {
    return {
      valid: false,
      attempted: true,
      error: error instanceof Error ? error.message : "Invalid JSON format",
    };
  }
}
