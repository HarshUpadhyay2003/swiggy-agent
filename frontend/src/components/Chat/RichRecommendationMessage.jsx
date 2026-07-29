import React from 'react'
import { ShoppingBag, Sparkles, Clock, Star } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'
import VegIndicator from '../ui/VegIndicator'
import { getFoodImage } from '../../assets/images'
import { useAppActions } from '../../store/AppStore'

export function RichRecommendationMessage({ items = [] }) {
  const { addToCart } = useAppActions()

  if (!items || items.length === 0) return null

  return (
    <div className="my-3 space-y-3">
      <div className="flex items-center gap-2 px-1">
        <Sparkles className="h-4 w-4 text-swiggy-500" />
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          AI Suggested Matches ({items.length})
        </span>
      </div>

      <div className="grid gap-3.5 sm:grid-cols-2">
        {items.map((item, idx) => {
          const imgUrl = item.image_url || getFoodImage(item.name || item.title, idx)
          const isVeg = item.is_veg !== false && item.dietary_tags?.includes('veg') !== false

          return (
            <Card
              key={item.id || idx}
              variant="glass"
              padding="none"
              className="flex flex-col justify-between overflow-hidden shadow-gourmet hover:shadow-gourmet-hover transition-all duration-300 group"
            >
              {/* Image & Badges */}
              <div className="relative aspect-[16/10] w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
                <img
                  src={imgUrl}
                  alt={item.name || item.title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />

                <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                  <VegIndicator isVeg={isVeg} size="sm" />
                  {item.match_score && (
                    <Badge variant="glass" size="sm">
                      {Math.round(item.match_score * 100)}% Match
                    </Badge>
                  )}
                </div>

                <div className="absolute top-2.5 right-2.5">
                  <Badge variant="primary" size="sm">
                    ₹{item.price ?? item.estimated_cost ?? 240}
                  </Badge>
                </div>

                <div className="absolute bottom-2.5 left-2.5 right-2.5 text-white">
                  <p className="text-xs font-medium text-amber-300 truncate">
                    {item.restaurant_name || item.cuisine || 'Gourmet Kitchen'}
                  </p>
                  <h4 className="font-serif font-bold text-base text-white truncate leading-snug">
                    {item.name || item.title || 'Special Culinary Option'}
                  </h4>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-3.5 space-y-3 bg-white/70 dark:bg-slate-900/70">
                {item.reason && (
                  <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 italic">
                    "{item.reason}"
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5 text-slate-400" />
                    <span>{item.delivery_time || '25-30 mins'}</span>
                  </div>
                  {item.rating && (
                    <div className="flex items-center gap-1 font-semibold text-amber-600 dark:text-amber-400">
                      <Star className="h-3.5 w-3.5 fill-current" />
                      <span>{item.rating}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="pt-1 flex items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    icon={ShoppingBag}
                    onClick={() => addToCart(item)}
                    className="flex-1"
                  >
                    Add to Cart
                  </Button>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export default RichRecommendationMessage
