import React from 'react'

export function RecommendationSkeleton() {
  return (
    <div className="glass-panel rounded-2xl shrink-0 w-[300px] sm:w-[320px] md:w-[340px] flex flex-col overflow-hidden shadow-sm border border-slate-200/50 dark:border-slate-800 animate-pulse">
      {/* Image Skeleton */}
      <div className="h-[200px] w-full bg-slate-200 dark:bg-slate-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 dark:via-slate-700/20 to-transparent animate-shimmer" />
        <div className="absolute top-3 right-3 h-6 w-16 bg-slate-300 dark:bg-slate-700 rounded-full" />
      </div>

      {/* Content Skeleton */}
      <div className="p-5 flex flex-col space-y-3 bg-white/40 dark:bg-slate-900/40">
        <div className="h-6 w-3/4 bg-slate-200 dark:bg-slate-800 rounded-md" />
        <div className="h-4 w-1/2 bg-slate-200 dark:bg-slate-800 rounded-md" />

        <div className="flex gap-2 py-1">
          <div className="h-5 w-14 bg-slate-200 dark:bg-slate-800 rounded-md" />
          <div className="h-5 w-20 bg-slate-200 dark:bg-slate-800 rounded-md" />
        </div>

        <div className="h-12 w-full bg-slate-200 dark:bg-slate-800 rounded-xl" />

        <div className="flex gap-2 pt-2">
          <div className="h-10 w-full bg-slate-300 dark:bg-slate-700 rounded-full" />
          <div className="h-10 w-10 bg-slate-200 dark:bg-slate-800 rounded-full shrink-0" />
        </div>
      </div>
    </div>
  )
}

export default RecommendationSkeleton
