import { useMemo, useState } from 'react'
import { ChevronDown, RefreshCw } from 'lucide-react'
import { useAppActions, useAppState } from '../../store/AppStore'

const mealTimes = [
  { key: 'breakfast', label: 'Breakfast' },
  { key: 'lunch', label: 'Lunch' },
  { key: 'dinner', label: 'Dinner' },
]

function MealPlanCard() {
  const { planner, loadingStates } = useAppState()
  const { requestMealPlan, addToCart } = useAppActions()
  const [expandedDay, setExpandedDay] = useState(null)

  const plannerLoading = loadingStates?.planner
  const days = useMemo(() => Object.entries(planner || {}), [planner])
  const hasPlan = days.length > 0
  const totalEstimate = useMemo(
    () => days.reduce((sum, [, details]) => sum + Number(details?.estimated_cost || 0), 0),
    [days]
  )

  const addDayToCart = async (dayDetails) => {
    const mealItems = mealTimes
      .map((meal) => dayDetails[meal.key])
      .filter((mealData) => mealData && typeof mealData === 'object' && (mealData.item_id || mealData.name || mealData.item_name))

    for (const mealData of mealItems) {
      /* eslint-disable no-await-in-loop */
      await addToCart(mealData, 1)
      /* eslint-enable no-await-in-loop */
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-950 p-5 text-white shadow-lg shadow-slate-950/20">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Meal plan</p>
            <h2 className="mt-3 text-2xl font-semibold">Weekly plan</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">Your latest planner is stored in session state and updates as the assistant responds.</p>
          </div>
          <button
            type="button"
            onClick={requestMealPlan}
            className="inline-flex items-center gap-2 rounded-3xl bg-swiggy-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-swiggy-600"
          >
            <RefreshCw className="h-4 w-4" /> Regenerate plan
          </button>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/50 dark:border-slate-700 dark:bg-slate-950">
        {plannerLoading && !hasPlan ? (
          <div className="space-y-4">
            {Array.from({ length: 2 }).map((_, idx) => (
              <div key={idx} className="rounded-3xl border border-slate-200 bg-slate-50 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <div className="h-5 w-1/4 rounded-full bg-slate-200 dark:bg-slate-800" />
                <div className="mt-4 space-y-3">
                  <div className="h-4 rounded-full bg-slate-200 dark:bg-slate-800" />
                  <div className="h-4 w-3/4 rounded-full bg-slate-200 dark:bg-slate-800" />
                </div>
              </div>
            ))}
          </div>
        ) : hasPlan ? (
          <div className="space-y-4">
            <div className="rounded-3xl bg-slate-50 p-4 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-300">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <p>Total weekly estimate</p>
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">₹{totalEstimate}</p>
              </div>
              <p className="mt-2 text-xs">Each day includes breakfast, lunch, and dinner recommendations based on your preferences.</p>
            </div>
            {days.map(([day, details]) => {
              const mealsForDay = mealTimes
                .map((meal) => details[meal.key])
                .filter((mealData) => mealData && typeof mealData === 'object' && (mealData.item_id || mealData.name || mealData.item_name))

              return (
                <div key={day} className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 text-slate-900 shadow-sm transition duration-200 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100">
                  <button
                    type="button"
                    onClick={() => setExpandedDay(expandedDay === day ? null : day)}
                    className="flex w-full items-center justify-between gap-3 px-4 py-4 text-left"
                  >
                    <div>
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">{day.replace('_', ' ').toUpperCase()}</p>
                      <p className="mt-2 text-lg font-semibold text-slate-900 dark:text-slate-100">Estimated cost: ₹{details.estimated_cost ?? '—'}</p>
                    </div>
                    <ChevronDown className={`h-5 w-5 transition-transform ${expandedDay === day ? 'rotate-180' : ''}`} />
                  </button>
                  {expandedDay === day ? (
                    <div className="space-y-4 border-t border-slate-200 bg-white px-4 py-4 dark:border-slate-800 dark:bg-slate-950">
                      {mealTimes.map((meal) => {
                        const mealData = details[meal.key]
                        const isStructured = mealData && typeof mealData === 'object' && (mealData.item_id || mealData.name || mealData.item_name)
                        const mealName = isStructured ? (mealData.name || mealData.item_name) : (typeof mealData === 'string' ? mealData : (mealData ? JSON.stringify(mealData) : 'Not available'))

                        return (
                          <div key={meal.key} className="rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
                            <div className="flex flex-col gap-3">
                              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div className="flex-1">
                                  <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{meal.label}</p>
                                  <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">{mealName}</p>
                                  {isStructured && (
                                    <>
                                      <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">{mealData.restaurant_name}</p>
                                      <p className="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">₹{mealData.price}</p>
                                    </>
                                  )}
                                </div>
                                {isStructured ? (
                                  <button
                                    type="button"
                                    onClick={() => addToCart(mealData, 1)}
                                    className="w-full rounded-3xl bg-swiggy-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-swiggy-600 sm:w-auto"
                                  >
                                    Add to cart
                                  </button>
                                ) : null}
                              </div>
                              {isStructured && (
                                <div className="flex flex-wrap gap-2">
                                  {mealData.cuisine && (
                                    <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300">{mealData.cuisine}</span>
                                  )}
                                  {mealData.healthy && (
                                    <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">Healthy</span>
                                  )}
                                  {mealData.vegetarian && (
                                    <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">Veg</span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                      {mealsForDay.length > 0 ? (
                        <button
                          type="button"
                          onClick={() => addDayToCart(details)}
                          className="w-full rounded-3xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-slate-200"
                        >
                          Add day to cart
                        </button>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        ) : (
          <div className="rounded-3xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-900 dark:text-slate-300">
            Ask the assistant for a weekly meal plan and it will appear here with day-by-day recommendations.
          </div>
        )}
      </div>
    </div>
  )
}

export default MealPlanCard
