"use client"

import * as React from "react"
import { ChatMessage, type Message } from "./chat-message"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

interface ChatMessageListProps {
  messages: Message[]
  isLoading?: boolean
}

export function ChatMessageList({ messages, isLoading }: ChatMessageListProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  return (
    <ScrollArea
      ref={scrollRef}
      className="flex-1 w-full"
    >
      <div className="flex flex-col">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center p-8">
            <h2 className="text-2xl font-semibold mb-2">Start a conversation</h2>
            <p className="text-muted-foreground">
              Ask me anything about your documents
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex w-full gap-3 p-4 justify-start">
                <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow-sm">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
                <div className="flex flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-muted">
                  <div className="whitespace-pre-wrap">Thinking...</div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </ScrollArea>
  )
}
