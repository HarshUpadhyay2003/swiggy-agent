function MessageBubble({ author, text, payload, timestamp }) {
  const isAssistant = author === 'assistant'
  const alignment = isAssistant ? 'self-start bg-slate-100 text-slate-900 dark:bg-slate-900 dark:text-slate-100' : 'self-end bg-swiggy-500 text-white'
  const authorLabel = isAssistant ? 'AI assistant' : 'You'

  const sanitizeContent = (value) => {
    if (!value) return ''
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>')
  }

  const formatTimestamp = (value) => {
    if (!value) return ''
    const date = new Date(value)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const renderPayload = () => {
    if (!payload || typeof payload !== 'object' || Object.keys(payload).length === 0) return null

    return (
      <div className="mt-4 space-y-3 rounded-[28px] bg-white/95 p-4 text-sm text-slate-700 shadow-sm shadow-slate-200/50 dark:bg-slate-900/95 dark:text-slate-300">
        {payload.recommendations && Array.isArray(payload.recommendations) ? (
          <div>
            <p className="font-semibold text-slate-900 dark:text-slate-100">Recommendations</p>
            <ul className="mt-3 grid gap-3 sm:grid-cols-2">
              {payload.recommendations.map((item, index) => (
                <li key={`${item.item_name}-${index}`} className="rounded-3xl bg-slate-50 p-3 shadow-sm dark:bg-slate-800">
                  <div className="flex items-center justify-between gap-2 text-sm font-semibold text-slate-900 dark:text-slate-100">
                    <span>{item.item_name}</span>
                    <span>₹{item.price}</span>
                  </div>
                  <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{item.restaurant} · {item.reason}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {payload.cart ? (
          <div>
            <p className="font-semibold text-slate-900 dark:text-slate-100">Cart preview</p>
            <div className="mt-3 space-y-2">
              {(payload.cart.items || []).map((item) => (
                <div key={item.item_id} className="flex items-center justify-between rounded-3xl bg-slate-50 px-3 py-3 text-sm shadow-sm dark:bg-slate-800">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{item.name}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Qty {item.quantity}</p>
                  </div>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">₹{item.price}</span>
                </div>
              ))}
              <div className="rounded-3xl bg-slate-100 px-3 py-3 text-sm font-semibold text-slate-900 dark:bg-slate-800 dark:text-slate-100">
                Total: ₹{payload.cart.total ?? payload.cart.subtotal ?? 0}
              </div>
            </div>
          </div>
        ) : null}

        {payload.order ? (
          <div>
            <p className="font-semibold text-slate-900 dark:text-slate-100">Order summary</p>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Order ID: {payload.order.order_id}</p>
            <p className="text-sm text-slate-600 dark:text-slate-400">Total: ₹{payload.order.total ?? 0}</p>
          </div>
        ) : null}

        {payload.meal_plan ? (
          <div>
            <p className="font-semibold text-slate-900 dark:text-slate-100">Meal plan</p>
            <div className="mt-3 space-y-3">
              {Object.entries(payload.meal_plan).map(([day, value]) => {
                const isStructured = value && typeof value === 'object' && value.breakfast
                return (
                  <div key={day} className="rounded-3xl bg-slate-50 p-3 shadow-sm dark:bg-slate-800">
                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{day.replace('_', ' ').toUpperCase()}</p>
                    {isStructured ? (
                      <div className="mt-2 space-y-2 text-xs text-slate-600 dark:text-slate-400">
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">Breakfast</p>
                          {typeof value.breakfast === 'object' && value.breakfast?.name ? (
                            <p>{value.breakfast.name} · ₹{value.breakfast.price}</p>
                          ) : (
                            <p>{String(value.breakfast)}</p>
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">Lunch</p>
                          {typeof value.lunch === 'object' && value.lunch?.name ? (
                            <p>{value.lunch.name} · ₹{value.lunch.price}</p>
                          ) : (
                            <p>{String(value.lunch)}</p>
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">Dinner</p>
                          {typeof value.dinner === 'object' && value.dinner?.name ? (
                            <p>{value.dinner.name} · ₹{value.dinner.price}</p>
                          ) : (
                            <p>{String(value.dinner)}</p>
                          )}
                        </div>
                        <p className="font-medium text-slate-900 dark:text-slate-100">Cost: ₹{value.estimated_cost}</p>
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{String(value)}</p>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ) : null}
      </div>
    )
  }

  return (
    <div className={`max-w-full rounded-[32px] p-4 shadow-sm transition-all duration-300 ease-out ${alignment}`}>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.25em] text-slate-500 dark:text-slate-400">
        <span>{authorLabel}</span>
        {timestamp ? <span>{formatTimestamp(timestamp)}</span> : null}
      </div>
      <div className="text-sm leading-7" dangerouslySetInnerHTML={{ __html: sanitizeContent(text) }} />
      {renderPayload()}
    </div>
  )
}

export default MessageBubble
