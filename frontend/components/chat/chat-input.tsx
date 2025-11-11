"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Type your message...",
}: ChatInputProps) {
  const [input, setInput] = React.useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full items-center gap-2 p-4 border-t bg-background"
    >
      <Input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1"
      />
      <Button
        type="submit"
        size="icon"
        disabled={disabled || !input.trim()}
        className={cn(
          "shrink-0",
          !input.trim() && "opacity-50 cursor-not-allowed"
        )}
      >
        <Send className="h-4 w-4" />
        <span className="sr-only">Send message</span>
      </Button>
    </form>
  )
}
