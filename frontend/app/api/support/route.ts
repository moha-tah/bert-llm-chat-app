import { openai } from "@ai-sdk/openai";
import { streamText, convertToModelMessages } from "ai";
import { IntakeSchema, type Intake } from "@/lib/intake-schema";
import { SYSTEM_PROMPT, DOCUMENTS } from "@/lib/prompts";

/**
 * POST /api/support
 *
 * Streaming chat endpoint for the support intake widget
 * Accepts conversation history and returns streaming AI responses
 */
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { messages } = body;

    if (!messages || !Array.isArray(messages)) {
      return new Response("Invalid request: messages array required", {
        status: 400,
      });
    }

    // Verify OpenAI API key is configured
    if (!process.env.OPENAI_API_KEY) {
      return new Response("OpenAI API key not configured", { status: 500 });
    }

    // Convert UIMessages to ModelMessages
    const convertedMessages = convertToModelMessages(messages);

    // Build the full conversation with system prompt and documents
    const conversationMessages = [
      {
        role: "system" as const,
        content: SYSTEM_PROMPT,
      },
      // Inject documents as the first assistant message
      {
        role: "assistant" as const,
        content: `I have access to the following knowledge base:\n\n${DOCUMENTS}\n\nHello — how can I help today?`,
      },
      // Add user conversation history
      ...convertedMessages,
    ];

    // Stream the response using Vercel AI SDK
    const result = streamText({
      model: openai("gpt-4o"),
      messages: conversationMessages,
      temperature: 0.7,
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error("Error in support chat API:", error);
    return new Response("Internal server error", { status: 500 });
  }
}

/**
 * Validates if a string contains a valid JSON object matching the IntakeSchema
 * Used by the frontend to detect when the conversation is complete
 */
export function validateIntakeJSON(text: string): {
  valid: boolean;
  data?: Intake;
  error?: string;
} {
  try {
    // Try to extract JSON from the text
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      return { valid: false, error: "No JSON found" };
    }

    const parsed = JSON.parse(jsonMatch[0]);
    const validated = IntakeSchema.parse(parsed);

    return { valid: true, data: validated };
  } catch (error) {
    return {
      valid: false,
      error: error instanceof Error ? error.message : "Invalid JSON",
    };
  }
}
