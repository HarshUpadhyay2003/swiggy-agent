function RecommendationCard({ item, onAdd, onRemove, onReplace, title, description, icon: Icon }) {
  const isFeatureCard = !!title

  if (!isFeatureCard && !item) {
    return null
  }

  if (isFeatureCard) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/40 transition hover:-translate-y-1 hover:shadow-glow dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-3xl bg-swiggy-100 text-swiggy-700 dark:bg-swiggy-500/15 dark:text-swiggy-300">
          {Icon ? <Icon className="h-6 w-6" /> : null}
        </div>
        <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{description}</p>
      </div>
    )
  }

  const normalizedItem = {
    item_id: item.item_id,
    item_name: item.item_name ?? item.name,
    name: item.name ?? item.item_name,
    restaurant: item.restaurant ?? item.restaurant_name,
    restaurant_name: item.restaurant_name ?? item.restaurant ?? '',
    price: item.price ?? 0,
    quantity: item.quantity ?? 1,
    ...item,
  }

  const tagItems = [
    item.budget_friendly && { label: 'Budget-friendly', className: 'bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-200' },
    item.spicy && { label: 'Spicy', className: 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-200' },
    item.high_protein && { label: 'High protein', className: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200' },
    item.healthy && { label: 'Healthy', className: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200' },
    (item.vegetarian || item.diet === 'veg' || item.veg) && { label: 'Veg', className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200' },
    (item.non_veg || item.diet === 'non-veg' || item.diet === 'nonveg') && { label: 'Non-veg', className: 'bg-rose-100 text-rose-700 dark:bg-rose-500/10 dark:text-rose-200' },
  ].filter(Boolean)

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-200/40 transition hover:-translate-y-0.5 hover:shadow-glow dark:border-slate-700 dark:bg-slate-950">
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{normalizedItem.name}</h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{normalizedItem.restaurant_name}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <p className="text-sm font-medium text-slate-900 dark:text-slate-100">₹{normalizedItem.price}</p>
              {item.cuisine ? (
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300">{item.cuisine}</span>
              ) : null}
              {tagItems.map((tag) => (
                <span key={tag.label} className={`rounded-full px-2 py-1 text-[11px] font-semibold ${tag.className}`}>
                  {tag.label}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col items-end gap-2">
            <div className="inline-flex items-center gap-2 rounded-full bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-600 dark:bg-orange-500/10 dark:text-orange-200">
              {item.reason ? 'Suggested' : 'Recommended'}
            </div>
            <button
              onClick={() => onAdd?.(normalizedItem)}
              className="rounded-2xl bg-orange-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-orange-600"
            >
              Add to cart
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {onReplace ? (
            <button
              onClick={() => onReplace?.(normalizedItem)}
              className="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              Replace
            </button>
          ) : null}
          {onRemove ? (
            <button
              onClick={() => onRemove?.(normalizedItem)}
              className="rounded-2xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-100 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200 dark:hover:bg-rose-900"
            >
              Remove
            </button>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export default RecommendationCard
