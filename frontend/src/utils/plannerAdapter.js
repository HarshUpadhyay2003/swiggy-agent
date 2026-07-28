/**
 * Single Planner Adapter for AI Commerce Copilot.
 * Normalizes ANY raw backend payload schema (day_1..day_7, weekly_plan, days, meals, plan, etc.)
 * into a single unified NormalizedPlanner schema consumed by UI components.
 */

const DAYS_NAME = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export function normalizeMeal(mealRaw, defaultType = 'Meal', dayIndex = 0, mealIndex = 0) {
  if (!mealRaw) return null

  if (typeof mealRaw === 'string') {
    return {
      item_id: dayIndex * 10 + mealIndex + 1,
      name: mealRaw,
      price: defaultType === 'Breakfast' ? 250 : defaultType === 'Lunch' ? 350 : 450,
      calories: defaultType === 'Breakfast' ? 400 : defaultType === 'Lunch' ? 600 : 700,
      is_veg: true,
      restaurant_name: 'Gourmet Kitchen',
      reason: `Matches your requirement for a nutritious ${defaultType.toLowerCase()}.`,
      meal_type: defaultType,
    }
  }

  return {
    item_id: mealRaw.item_id || mealRaw.id || (dayIndex * 10 + mealIndex + 1),
    name: mealRaw.name || mealRaw.item_name || mealRaw.title || 'Curated Dish',
    price: Number(mealRaw.price ?? mealRaw.estimated_cost ?? (defaultType === 'Breakfast' ? 250 : defaultType === 'Lunch' ? 350 : 450)),
    calories: Number(mealRaw.calories ?? (defaultType === 'Breakfast' ? 400 : defaultType === 'Lunch' ? 650 : 700)),
    is_veg: mealRaw.is_veg !== false && mealRaw.dietary_tags?.includes('veg') !== false,
    restaurant_name: mealRaw.restaurant_name || mealRaw.restaurant || mealRaw.brand || 'Gourmet Kitchen',
    reason: mealRaw.reason || mealRaw.description || `AI selected for ${defaultType.toLowerCase()} balance.`,
    meal_type: mealRaw.meal_type || defaultType,
    image_url: mealRaw.image_url || mealRaw.image || null,
  }
}

export function normalizePlanner(rawPayload) {
  if (!rawPayload) return null

  // If already normalized
  if (rawPayload._normalized && Array.isArray(rawPayload.days)) {
    return rawPayload
  }

  const daysNormalized = []
  let totalEstimatedCost = 0
  let totalCaloriesCount = 0

  // 1. Extract raw days list/map
  let rawDaysSource = []
  if (Array.isArray(rawPayload.days)) {
    rawDaysSource = rawPayload.days
  } else if (Array.isArray(rawPayload.weekly_plan)) {
    rawDaysSource = rawPayload.weekly_plan
  } else if (Array.isArray(rawPayload.plan)) {
    rawDaysSource = rawPayload.plan
  } else if (typeof rawPayload === 'object') {
    // Handle day_1 .. day_7 dictionary format from backend MealPlanner
    const keys = Object.keys(rawPayload).filter(
      (k) => k.startsWith('day_') || DAYS_NAME.some((d) => d.toLowerCase() === k.toLowerCase())
    )
    if (keys.length > 0) {
      keys.sort((a, b) => {
        const numA = parseInt(a.replace('day_', ''), 10) || 0
        const numB = parseInt(b.replace('day_', ''), 10) || 0
        return numA - numB
      })
      rawDaysSource = keys.map((k) => ({ ...rawPayload[k], day_key: k }))
    }
  }

  if (rawDaysSource.length === 0 && Array.isArray(rawPayload)) {
    rawDaysSource = rawPayload
  }

  // 2. Loop over 7 days (Monday - Sunday)
  DAYS_NAME.forEach((dayName, idx) => {
    const rawDay =
      rawDaysSource[idx] ||
      rawDaysSource.find((d) => (d.day || d.day_name || '').toLowerCase() === dayName.toLowerCase()) ||
      {}

    const breakfast = normalizeMeal(rawDay.breakfast || rawDay.meals?.[0], 'Breakfast', idx, 0)
    const lunch = normalizeMeal(rawDay.lunch || rawDay.meals?.[1], 'Lunch', idx, 1)
    const dinner = normalizeMeal(rawDay.dinner || rawDay.meals?.[2], 'Dinner', idx, 2)

    const dayCost = Number(
      rawDay.estimated_cost ??
        rawDay.total_cost ??
        (breakfast?.price || 0) + (lunch?.price || 0) + (dinner?.price || 0)
    )

    const dayCalories = Number(
      rawDay.total_calories ??
        rawDay.calories ??
        (breakfast?.calories || 0) + (lunch?.calories || 0) + (dinner?.calories || 0)
    )

    totalEstimatedCost += dayCost
    totalCaloriesCount += dayCalories

    daysNormalized.push({
      day: dayName,
      day_index: idx,
      total_cost: dayCost,
      total_calories: dayCalories,
      breakfast,
      lunch,
      dinner,
      meals: [breakfast, lunch, dinner].filter(Boolean),
    })
  })

  const dailyAverageCalories = Math.round(totalCaloriesCount / 7)

  return {
    _normalized: true,
    days: daysNormalized,
    summary:
      rawPayload.summary ||
      'Your personalized 7-day dining schedule, optimized for taste, health, and budget.',
    budget: {
      total_estimated_cost: totalEstimatedCost,
      budget_limit: rawPayload.budget_limit || 10000,
      savings_estimate: Math.round(totalEstimatedCost * 0.12),
    },
    nutrition: {
      daily_average_calories: dailyAverageCalories,
      protein_target: rawPayload.protein_target || '85g / day',
      health_score: rawPayload.health_score || 92,
    },
  }
}

export default normalizePlanner
