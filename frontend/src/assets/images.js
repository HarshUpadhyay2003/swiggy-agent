import food1Img from '../../../assets/a_colorful_and_fresh_fruit_smoothie_bowl_with_granola_and_berries_top_view/food1.png'
import food2Img from '../../../assets/a_fresh_vibrant_greek_salad_with_feta_cheese_olives_and_crisp_vegetables_in_a/food2.png'
import food3Img from '../../../assets/a_gourmet_grilled_chicken_breast_with_roasted_vegetables_and_quinoa/food3.png'
import food4Img from '../../../assets/professional_food_photography_of_a_classic_margherita_pizza_with_bubbling/food4.png'
import food5Img from '../../../assets/top_view_of_a_gourmet_poke_bowl_with_fresh_salmon_avocado_edamame_and_mango/food5.png'
import food6Img from '../../../assets/a_premium_high_resolution_food_photo_of_a_healthy_avocado_toast_with_poached/food6.png'

export const foodImages = {
  food1: food1Img,
  food2: food2Img,
  food3: food3Img,
  food4: food4Img,
  food5: food5Img,
  food6: food6Img,

  avocadoToast: food6Img,
  greekSalad: food2Img,
  grilledChicken: food3Img,
  smoothieBowl: food1Img,
  pokeBowl: food5Img,
  margheritaPizza: food4Img,
}

/**
 * Intelligent Dish Image Resolver
 * Maps dish name or category to the best premium food photography asset.
 */
export function getFoodImage(dishName = '', index = 0) {
  if (!dishName || typeof dishName !== 'string') {
    const defaultList = [food2Img, food3Img, food1Img, food5Img, food4Img, food6Img]
    return defaultList[index % defaultList.length]
  }

  const name = dishName.toLowerCase()

  if (name.includes('salad') || name.includes('greek') || name.includes('veg bowl') || name.includes('green') || name.includes('cucumber')) {
    return food2Img
  }
  if (name.includes('chicken') || name.includes('grilled') || name.includes('meat') || name.includes('protein') || name.includes('roast')) {
    return food3Img
  }
  if (name.includes('smoothie') || name.includes('berry') || name.includes('fruit') || name.includes('healthy meal') || name.includes('superfood')) {
    return food1Img
  }
  if (name.includes('poke') || name.includes('salmon') || name.includes('fish') || name.includes('seafood') || name.includes('bowl')) {
    return food5Img
  }
  if (name.includes('pizza') || name.includes('margherita') || name.includes('italian') || name.includes('pasta') || name.includes('cheese') || name.includes('fries') || name.includes('burger')) {
    return food4Img
  }
  if (name.includes('hash') || name.includes('brown') || name.includes('toast') || name.includes('avocado') || name.includes('egg') || name.includes('breakfast')) {
    return food6Img
  }

  const fallbackList = [food2Img, food3Img, food1Img, food5Img, food4Img, food6Img]
  return fallbackList[index % fallbackList.length]
}

export const heroGallery = [
  {
    id: 'food6',
    title: 'Poached Egg & Avocado Toast',
    category: 'Healthy Breakfast',
    url: food6Img,
    badge: 'High Protein',
  },
  {
    id: 'food1',
    title: 'Berry Granola Smoothie Bowl',
    category: 'Superfood',
    url: food1Img,
    badge: 'Vegan',
  },
  {
    id: 'food3',
    title: 'Gourmet Grilled Chicken & Quinoa',
    category: 'Lean Dinner',
    url: food3Img,
    badge: 'Low Cal',
  },
  {
    id: 'food4',
    title: 'Woodfired Margherita Pizza',
    category: 'Artisanal Italian',
    url: food4Img,
    badge: 'Chef Choice',
  },
  {
    id: 'food5',
    title: 'Salmon & Edamame Poke Bowl',
    category: 'Fresh Seafood',
    url: food5Img,
    badge: 'Omega-3',
  },
]

export default foodImages
