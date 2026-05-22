import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'

function ChatWindow({ messages, typing }) {
  const containerRef = useRef(null)

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  return (
    <div className="flex h-[520px] flex-col rounded-[32px] border border-slate-200/70 bg-white/90 p-4 shadow-soft backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-950/90">
      <div className="mb-4 flex items-center justify-between rounded-[28px] bg-slate-100 px-4 py-3 text-sm text-slate-600 shadow-sm shadow-slate-200/40 dark:bg-slate-900 dark:text-slate-300">
        <div>
          <p className="font-semibold text-slate-900 dark:text-slate-100">Conversation stream</p>
          <p className="text-xs text-slate-500 dark:text-slate-400">A modern AI chat flow for ordering, planning, and cart management.</p>
        </div>
        <span className="rounded-full bg-swiggy-50 px-3 py-1 text-[11px] font-semibold text-swiggy-800 dark:bg-swiggy-500/15 dark:text-swiggy-300">
          AI ready
        </span>
      </div>

      <div ref={containerRef} className="flex-1 space-y-4 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent dark:scrollbar-thumb-slate-700">
        {messages.map((message) => (
          <MessageBubble key={message.id} author={message.author} text={message.text} payload={message.data} timestamp={message.timestamp} />
        ))}

        {typing ? (
          <div className="rounded-[28px] bg-slate-100 px-5 py-4 shadow-sm shadow-slate-200/40 dark:bg-slate-900">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-800" />
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">AI is thinking</p>
                <div className="mt-2 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-swiggy-500" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-slate-400 delay-75" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-slate-400 delay-150" />
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default ChatWindow
