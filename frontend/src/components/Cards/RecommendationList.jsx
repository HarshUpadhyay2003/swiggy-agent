import RecommendationCard from './RecommendationCard'

function RecommendationList({ items, onAdd, onRemove, onReplace, loading }) {
  const uniqueItems = Array.isArray(items)
    ? items.filter((item, index, all) => {
        const id = item?.item_id ?? item?.item_name ?? item?.name
        return id ? all.findIndex((candidate) => (candidate?.item_id ?? candidate?.item_name ?? candidate?.name) === id) === index : index === 0
      })
    : []

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        {Array.from({ length: 4 }).map((_, idx) => (
          <div key={idx} className="rounded-3xl border border-slate-200 bg-slate-100 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <div className="h-6 w-3/4 rounded-full bg-slate-200 dark:bg-slate-700" />
            <div className="mt-3 h-4 w-1/2 rounded-full bg-slate-200 dark:bg-slate-700" />
            <div className="mt-5 flex items-center justify-between gap-3">
              <div className="h-10 w-24 rounded-full bg-slate-200 dark:bg-slate-700" />
              <div className="h-10 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!uniqueItems.length) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-200/40 dark:border-slate-700 dark:bg-slate-950">
        <p className="text-sm text-slate-600 dark:text-slate-400">No recommendations right now — try a different prompt or refresh to discover new meals.</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {uniqueItems.map((it, idx) => (
        <RecommendationCard
          key={it.item_id ?? `${it.item_name}-${idx}`}
          item={it}
          onAdd={onAdd}
          onRemove={() => onRemove && onRemove(it)}
          onReplace={() => onReplace && onReplace(it)}
        />
      ))}
    </div>
  )
}

export default RecommendationList
