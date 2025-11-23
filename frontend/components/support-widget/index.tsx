"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "@/components/chat/chat-message";
import { ChatInput } from "@/components/chat/chat-input";
import { SummaryCard } from "./summary-card";
import { useSupportChat, getMessageText } from "@/hooks/use-support-chat";
import { MessageCircle, X, RefreshCw, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * SupportWidget Component
 *
 * A floating support intake widget that appears globally across the application.
 * Opens a modal with a chat interface to extract structured intake information.
 */
export function SupportWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    sendMessage,
    isLoading,
    extractedData,
    isComplete,
    validationError,
    reset,
    resume,
  } = useSupportChat();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Determine if we should show the summary (derived state)
  const showSummary = isComplete && extractedData !== null;

  /**
   * Handle opening the widget
   */
  const handleOpen = () => {
    setIsOpen(true);
  };

  /**
   * Handle closing the widget
   */
  const handleClose = () => {
    setIsOpen(false);
    // Don't reset immediately - allow user to reopen and see the conversation
  };

  /**
   * Handle starting a new conversation
   */
  const handleNewConversation = () => {
    reset();
  };

  /**
   * Handle resuming the conversation (edit)
   */
  const handleEdit = () => {
    resume();
  };

  /**
   * Handle sending a message
   */
  const handleSend = async (message: string) => {
    // Use sendMessage to add a new user message to the conversation
    await sendMessage({ text: message });
  };

  /**
   * Handle submitting the intake request
   */
  const handleSubmitIntake = () => {
    // Resume conversation to show the chat interface
    resume();
    // Send the confirmation message to trigger the final AI response
    handleSend("Everything is correct");
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={handleOpen}
          className={cn(
            "fixed bottom-6 right-6 z-50",
            "h-14 w-14 rounded-full shadow-lg",
            "bg-accent hover:bg-accent/90",
            "text-white border border-[--color-oxford-blue]",
            "flex items-center justify-center",
            "transition-all duration-200 ease-in-out",
            "hover:scale-110 active:scale-95",
            "focus:outline-none focus:ring-2 focus:ring-[--color-pigment-red] focus:ring-offset-2"
          )}
          aria-label="Open support chat"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Modal Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-end p-6">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={handleClose}
            aria-hidden="true"
          />

          {/* Widget Card */}
          <Card
            className={cn(
              "relative w-full max-w-md h-[600px]",
              "flex flex-col",
              "shadow-2xl border-[--color-oxford-blue]",
              "animate-in slide-in-from-bottom-5 duration-300"
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-[--color-oxford-blue] text-white rounded-t-lg">
              <div className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5" />
                <h2 className="font-semibold text-lg">Support Intake</h2>
              </div>
              <div className="flex items-center gap-1">
                {messages.length > 0 && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleNewConversation}
                    className="h-8 w-8 text-primary hover:bg-primary/20"
                    title="Start new conversation"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleClose}
                  className="h-8 w-8 text-primary hover:bg-primary/20"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 flex flex-col min-h-0">
              {/* Show summary if complete */}
              {showSummary && extractedData ? (
                <div className="flex-1 overflow-auto p-4">
                  <SummaryCard
                    data={extractedData}
                    onEdit={handleEdit}
                    onSubmit={handleSubmitIntake}
                  />
                </div>
              ) : (
                <>
                  {/* Messages Area */}
                  <ScrollArea ref={scrollRef} className="flex-1 p-4">
                    {messages.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center p-6">
                        <MessageCircle className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-semibold text-lg mb-2">
                          Welcome to Support Intake
                        </h3>
                        <p className="text-sm text-muted-foreground max-w-xs">
                          I&apos;ll help you report your issue and route it to
                          the right team. Let&apos;s start by understanding your
                          problem.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {messages
                          .filter(
                            (msg) =>
                              msg.role === "user" || msg.role === "assistant"
                          )
                          .map((message) => (
                            <ChatMessage
                              key={message.id}
                              message={{
                                id: message.id,
                                role: message.role as "user" | "assistant",
                                content: getMessageText(message),
                              }}
                            />
                          ))}
                        {isLoading && (
                          <div className="flex items-center gap-2 p-4 text-muted-foreground">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Thinking...</span>
                          </div>
                        )}
                      </div>
                    )}
                  </ScrollArea>

                  {/* Validation Error */}
                  {validationError && (
                    <div className="px-4 py-2 bg-yellow-50 dark:bg-yellow-950/20 border-t border-yellow-200 dark:border-yellow-900">
                      <p className="text-xs text-yellow-700 dark:text-yellow-300">
                        {validationError}
                      </p>
                    </div>
                  )}

                  {/* Input Area */}
                  <ChatInput
                    onSend={handleSend}
                    disabled={isLoading || isComplete}
                    placeholder={
                      isComplete
                        ? "Conversation complete"
                        : "Describe your issue..."
                    }
                  />
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t bg-muted/50 text-xs text-center text-muted-foreground rounded-b-lg">
              Powered by AI • Air France / Barfield
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
