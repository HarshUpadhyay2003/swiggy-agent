import React, { useState } from 'react'
import { ShoppingBag, RefreshCw, Check, Info } from 'lucide-react'
import Button from '../ui/Button'

export function RecommendationFooter({ item, onAdd, onReplace, onDetails }) {
  const [added, setAdded] = useState(false)

  const handleAdd = () => {
    onAdd && onAdd(item)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="pt-2 flex items-center gap-2">
      <Button
        variant={added ? 'accent' : 'primary'}
        size="md"
        icon={added ? Check : ShoppingBag}
        onClick={handleAdd}
        className="flex-1 transition-all duration-200"
      >
        {added ? 'Added to Cart' : 'Add to Cart'}
      </Button>

      {onDetails && (
        <Button
          variant="outline"
          size="icon"
          icon={Info}
          onClick={() => onDetails(item)}
          title="View nutrition & details"
        />
      )}

      {onReplace && (
        <Button
          variant="ghost"
          size="icon"
          icon={RefreshCw}
          onClick={() => onReplace(item)}
          title="Replace option"
        />
      )}
    </div>
  )
}

export default RecommendationFooter
