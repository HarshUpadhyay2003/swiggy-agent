import React, { useEffect, useRef } from 'react'
import UserMessage from './UserMessage'
import AssistantMessage from './AssistantMessage'
import TypingBubble from './TypingBubble'
import EmptyConversation from './EmptyConversation'

export function ConversationView({ messages = [], typing = false, onSelectPrompt }) {
  const bottomRef = useRef(null)

  // Scroll into view only during active conversation (messages > 1 or typing)
  useEffect(() => {
    if ((messages && messages.length > 1) || typing) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages?.length, typing])

  if (!messages || messages.length === 0) {
    return <EmptyConversation onSelectPrompt={onSelectPrompt} />
  }

  return (
    <div className="flex flex-col space-y-2 p-4 md:p-6 overflow-y-auto max-h-[520px] scrollbar-thin">
      {messages.map((msg, index) => {
        const isUser = msg.author === 'user' || msg.role === 'user' || msg.sender === 'user'

        if (isUser) {
          return <UserMessage key={msg.id || index} message={msg} />
        }

        return (
          <AssistantMessage
            key={msg.id || index}
            message={msg}
            onSelectPrompt={onSelectPrompt}
          />
        )
      })}

      {typing && <TypingBubble />}

      <div ref={bottomRef} />
    </div>
  )
}

export default ConversationView
