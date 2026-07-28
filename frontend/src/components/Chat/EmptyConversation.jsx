import React from 'react'
import { Sparkles, Utensils, Calendar, ShoppingBag, Flame, Heart, Clock } from 'lucide-react'
import Card from '../ui/Card'
import Chip from '../ui/Chip'
import Badge from '../ui/Badge'
import { heroGallery } from '../../assets/images'

export function EmptyConversation({ onSelectPrompt }) {
  return (
    <div className="flex flex-col items-center text-center py-6 px-4 space-y-6">
      {/* Header Greeting */}
      <div className="space-y-2 max-w-lg">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-swiggy-50 text-swiggy-700 dark:bg-swiggy-950/40 dark:text-swiggy-400 text-xs font-semibold">
          <Sparkles className="h-3.5 w-3.5" /> CraveAI Copilot Ready
        </div>
        <h3 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100">
          How can I assist your appetite?
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Type a request or select a quick suggestion below to discover meals, build custom plans, or reorder instantly.
        </p>
      </div>

      {/* Suggested Inspiration Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 w-full max-w-2xl text-left">
        {heroGallery.slice(0, 3).map((item) => (
          <Card
            key={item.id}
            variant="glass"
            padding="none"
            hover
            onClick={() => onSelectPrompt && onSelectPrompt(`Recommend ${item.title}`)}
            className="group overflow-hidden relative cursor-pointer"
          >
            <div className="aspect-[16/10] relative overflow-hidden bg-slate-100 dark:bg-slate-800">
              <img
                src={item.url}
                alt={item.title}
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
              <div className="absolute bottom-2 left-2 right-2 text-white">
                <Badge variant="glass" size="sm" className="mb-1">
                  {item.badge}
                </Badge>
                <p className="font-serif text-xs font-semibold truncate text-white">
                  {item.title}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Action Chips */}
      <div className="flex flex-wrap justify-center gap-2 max-w-xl pt-2">
        <Chip
          variant="default"
          size="sm"
          icon={Flame}
          onClick={() => onSelectPrompt && onSelectPrompt('Repeat last order')}
        >
          Repeat last order
        </Chip>
        <Chip
          variant="default"
          size="sm"
          icon={Heart}
          onClick={() => onSelectPrompt && onSelectPrompt('Suggest healthy lunch ideas under ₹300')}
        >
          Healthy Lunch under ₹300
        </Chip>
        <Chip
          variant="default"
          size="sm"
          icon={Calendar}
          onClick={() => onSelectPrompt && onSelectPrompt('Create a 7 day meal plan')}
        >
          Build 7-Day Plan
        </Chip>
      </div>
    </div>
  )
}

export default EmptyConversation
