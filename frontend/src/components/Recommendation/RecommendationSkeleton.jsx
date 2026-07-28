import React from 'react'
import Card from '../ui/Card'
import Skeleton from '../animations/Skeleton'

export function RecommendationSkeleton() {
  return (
    <Card variant="glass" padding="none" className="overflow-hidden">
      <Skeleton variant="card" className="h-44 w-full rounded-none" />
      <div className="p-4 space-y-3">
        <div className="flex gap-2">
          <Skeleton variant="pill" className="h-6 w-16" />
          <Skeleton variant="pill" className="h-6 w-24" />
        </div>
        <Skeleton variant="title" className="h-6 w-3/4" />
        <Skeleton variant="text" className="h-4 w-1/2" />
        <Skeleton variant="text" className="h-4 w-full" />
        <div className="pt-2 flex gap-2">
          <Skeleton variant="pill" className="h-10 w-full" />
        </div>
      </div>
    </Card>
  )
}

export default RecommendationSkeleton
