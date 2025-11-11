"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { User, Bot } from "lucide-react"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
}

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div
      className={cn(
        "flex w-full gap-3 p-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow-sm">
          <Bot className="h-4 w-4" />
        </div>
      )}
      <div
        className={cn(
          "flex flex-col gap-2 rounded-lg px-3 py-2 text-sm max-w-[80%]",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        )}
      >
        <div className="whitespace-pre-wrap wrap-break-word">{message.content}</div>
      </div>
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow-sm">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  )
}
