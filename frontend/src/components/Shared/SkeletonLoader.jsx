/**
 * Lightweight skeleton loaders for loading states
 */

export function ChatSkeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      <div className="rounded-[28px] bg-slate-100 px-4 py-3 dark:bg-slate-800">
        <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="mt-2 space-y-2">
          <div className="h-3 w-full rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-3 w-4/5 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
      </div>
    </div>
  )
}

export function RecommendationSkeleton() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-950 animate-pulse">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-2 h-3 w-24 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-3 flex gap-2">
            <div className="h-6 w-12 rounded-full bg-slate-200 dark:bg-slate-700" />
            <div className="h-6 w-16 rounded-full bg-slate-200 dark:bg-slate-700" />
          </div>
        </div>
        <div className="h-10 w-24 rounded-2xl bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  )
}

export function CartItemSkeleton() {
  return (
    <div className="rounded-3xl bg-slate-50 p-4 shadow-sm dark:bg-slate-900 animate-pulse">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1">
          <div className="h-5 w-40 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-2 h-3 w-32 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-3 h-4 w-16 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
        <div className="h-10 w-24 rounded-full bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  )
}

export function MealPlanSkeleton() {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 shadow-sm dark:border-slate-800 dark:bg-slate-900 animate-pulse">
      <div className="flex items-center justify-between gap-3 px-4 py-4">
        <div className="flex-1">
          <div className="h-3 w-20 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-2 h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
        <div className="h-5 w-5 rounded bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  )
}

export function RecListSkeleton({ count = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <RecommendationSkeleton key={i} />
      ))}
    </div>
  )
}

export function CartSkeleton({ itemCount = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: itemCount }).map((_, i) => (
        <CartItemSkeleton key={i} />
      ))}
      <div className="space-y-2 rounded-3xl bg-slate-100 p-4 dark:bg-slate-900 animate-pulse">
        <div className="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="h-4 w-28 rounded bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  )
}
