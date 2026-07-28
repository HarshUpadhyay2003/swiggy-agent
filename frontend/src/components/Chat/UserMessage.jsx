import React from 'react'

export function UserMessage({ message }) {
  const content = typeof message === 'string' ? message : message.content || message.text

  return (
    <div className="flex flex-col items-end w-full my-3">
      <div className="bg-swiggy-500 text-white p-4 md:p-6 rounded-[24px] rounded-br-[8px] max-w-[85%] md:max-w-[70%] shadow-md text-base leading-relaxed font-sans font-medium select-text break-words">
        <p>{content}</p>
      </div>
    </div>
  )
}

export default UserMessage
