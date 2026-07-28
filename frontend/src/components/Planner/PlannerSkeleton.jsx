import React from 'react'
import Card from '../ui/Card'
import Skeleton from '../animations/Skeleton'

export function PlannerSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Skeleton variant="card" className="h-20 w-full" />
        <Skeleton variant="card" className="h-20 w-full" />
        <Skeleton variant="card" className="h-20 w-full" />
        <Skeleton variant="card" className="h-20 w-full" />
      </div>

      <Card variant="glass" padding="md" className="space-y-3">
        <Skeleton variant="title" className="h-6 w-1/3" />
        <Skeleton variant="card" className="h-24 w-full" />
        <Skeleton variant="card" className="h-24 w-full" />
      </Card>
    </div>
  )
}

export default PlannerSkeleton
