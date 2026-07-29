import { createContext, useContext, useEffect, useMemo, useReducer } from 'react'
import toast from 'react-hot-toast'
import {
  sendMessage as apiSendMessage,
  addCartItem as apiAddCartItem,
  removeCartItem as apiRemoveCartItem,
  checkoutCart as apiCheckoutCart,
  getCart as apiGetCart,
  sendTelemetry,
} from '../services/chatApi'
import { normalizePlanner } from '../utils/plannerAdapter'

const AppContext = createContext(null)

const DEFAULT_CART = {
  items: [],
  subtotal: 0,
  tax: 0,
  delivery_fee: 0,
  total: 0,
}

const initialState = {
  sessionId: '',
  theme: 'light',
  loading: false,
  typing: false,
  error: null,
  messages: [
    {
      id: 'assistant-1',
      author: 'assistant',
      text: 'Hello! I am your AI commerce copilot. Ask me to recommend meals, manage your cart, or build a weekly meal plan.',
      data: {},
      timestamp: new Date().toISOString(),
    },
  ],
  recommendations: [],
  cart: DEFAULT_CART,
  planner: {},
  orderStatus: null,
  checkoutStatus: { inProgress: false, success: false, message: '' },
  cartSyncStatus: { status: 'idle', message: '' },
  loadingStates: {
    chat: false,
    recommendations: false,
    cart: false,
    checkout: false,
    planner: false,
    sessionRestore: false,
  },
}

const buildCart = (cart = {}) => ({
  items: Array.isArray(cart.items)
    ? cart.items.map((item) => ({
        item_id: item.item_id,
        name: item.name ?? item.item_name ?? 'Unknown item',
        restaurant_name: item.restaurant_name ?? item.restaurant ?? '',
        quantity: item.quantity ?? 1,
        price: item.price ?? 0,
        ...item,
      }))
    : [],
  subtotal: cart.subtotal ?? 0,
  tax: cart.tax ?? 0,
  delivery_fee: cart.delivery_fee ?? 0,
  total: cart.total ?? cart.subtotal ?? 0,
})

const dedupeRecommendations = (items) => {
  const seen = new Set()
  return Array.isArray(items)
    ? items.filter((item) => {
        const id = item.item_id ?? item.item_name ?? item.name
        if (!id || seen.has(id)) return false
        seen.add(id)
        return true
      })
    : []
}

const reducer = (state, action) => {
  console.log('[REDUCER LOG] Action Type:', action.type)
  console.log('[REDUCER LOG] Payload Summary:', action.payload)
  console.log('[REDUCER LOG] Current State Summary:', {
    messagesCount: state.messages?.length,
    recommendationsCount: state.recommendations?.length,
    cartItemsCount: state.cart?.items?.length,
    hasPlanner: Boolean(state.planner?.days),
  })

  let nextState = state
  switch (action.type) {
    case 'INIT_APP':
      nextState = {
        ...state,
        sessionId: action.payload.sessionId,
        theme: action.payload.theme,
      }
      break
    case 'SET_LOADING':
      nextState = { ...state, loading: action.payload }
      break
    case 'SET_LOADING_STATE':
      nextState = {
        ...state,
        loadingStates: {
          ...state.loadingStates,
          [action.payload.key]: action.payload.value,
        },
      }
      break
    case 'SET_TYPING':
      nextState = { ...state, typing: action.payload }
      break
    case 'SET_ERROR':
      nextState = { ...state, error: action.payload }
      break
    case 'ADD_MESSAGE':
      nextState = { ...state, messages: [...state.messages, action.payload] }
      break
    case 'SET_RECOMMENDATIONS': {
      const recs = dedupeRecommendations(action.payload || [])
      console.log('[REDUCER LOG SET_RECOMMENDATIONS] payload length:', Array.isArray(action.payload) ? action.payload.length : 'N/A')
      console.log('[REDUCER LOG SET_RECOMMENDATIONS] recommendation names:', recs.map((i) => i.name || i.item_name))
      nextState = { ...state, recommendations: recs }
      break
    }
    case 'REMOVE_RECOMMENDATION':
      nextState = {
        ...state,
        recommendations: state.recommendations.filter((item) => {
          const id = item.item_id ?? item.item_name ?? item.name
          return id !== action.payload
        }),
      }
      break
    case 'SET_CART': {
      const cartObj = buildCart(JSON.parse(JSON.stringify(action.payload || {})))
      console.log('[REDUCER LOG SET_CART] cart items:', cartObj.items)
      console.log('[REDUCER LOG SET_CART] subtotal:', cartObj.subtotal)
      nextState = { ...state, cart: cartObj }
      break
    }
    case 'CLEAR_CART':
      nextState = { ...state, cart: DEFAULT_CART }
      break
    case 'SET_PLANNER': {
      const normalized = action.payload ? normalizePlanner(action.payload) : {}
      console.log('[REDUCER LOG SET_PLANNER] planner keys:', normalized ? Object.keys(normalized) : [])
      console.log('[REDUCER LOG SET_PLANNER] days count:', normalized?.days?.length)
      nextState = { ...state, planner: normalized }
      break
    }
    case 'SET_ORDER':
      nextState = { ...state, orderStatus: action.payload || null }
      break
    case 'SET_CHECKOUT_STATUS':
      nextState = { ...state, checkoutStatus: { ...state.checkoutStatus, ...action.payload } }
      break
    case 'SET_CART_SYNC_STATUS':
      nextState = { ...state, cartSyncStatus: { ...state.cartSyncStatus, ...action.payload } }
      break
    case 'TOGGLE_THEME':
      nextState = { ...state, theme: state.theme === 'dark' ? 'light' : 'dark' }
      break
    case 'RESET_GUEST_SESSION':
      nextState = {
        ...initialState,
        sessionId: action.payload.newSessionId,
        theme: state.theme,
      }
      break
    default:
      nextState = state
  }

  return nextState
}

const generateSessionId = () => `session-${Date.now()}-${Math.floor(Math.random() * 10000)}`

const initializeState = () => {
  let sessionId = generateSessionId()
  let theme = 'light'
  let guestSession = null

  if (typeof window !== 'undefined') {
    const storedTheme = window.localStorage.getItem('swiggy_theme')
    theme = storedTheme === 'dark' ? 'dark' : 'light'

    try {
      const storedGuestSession = window.sessionStorage.getItem('swiggy_guest_session')
      if (storedGuestSession) {
        guestSession = JSON.parse(storedGuestSession)
      }
    } catch (e) {
      // Ignore parse error
    }
  }

  if (guestSession && guestSession.sessionId) {
    return {
      ...initialState,
      ...guestSession,
      theme,
    }
  }

  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem('swiggy_guest_session', JSON.stringify({ sessionId }))
  }

  return {
    ...initialState,
    sessionId,
    theme,
  }
}

const getPayload = (response) => response?.data ?? response ?? {}
const getData = (response) => {
  const payload = getPayload(response)
  return payload?.data ?? payload ?? {}
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, initializeState)

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.localStorage.setItem('swiggy_theme', state.theme)
    document.documentElement.classList.toggle('dark', state.theme === 'dark')
  }, [state.theme])

  useEffect(() => {
    const restoreSession = async () => {
      dispatch({ type: 'SET_LOADING_STATE', payload: { key: 'sessionRestore', value: true } })
      await syncCart()
      dispatch({ type: 'SET_LOADING_STATE', payload: { key: 'sessionRestore', value: false } })
    }

    if (state.sessionId) {
      restoreSession()
    }
  }, [state.sessionId])

  const setLoadingState = (key, value) => {
    dispatch({ type: 'SET_LOADING_STATE', payload: { key, value } })
  }

  const syncCart = async () => {
    setLoadingState('cart', true)
    try {
      const response = await apiGetCart(state.sessionId)
      const payload = getPayload(response)
      const data = getData(response)

      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Cart synced' } })
      }
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Cart sync failed.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'error', message: 'Cart sync failed' } })
      return null
    } finally {
      setLoadingState('cart', false)
    }
  }

  const sendChat = async (text) => {
    if (!text?.trim()) return
    const userMessage = {
      id: `user-${Date.now()}`,
      author: 'user',
      text: text.trim(),
      data: {},
      timestamp: new Date().toISOString(),
    }

    const wantsRecommendations = /recommend|menu|suggest|meal|dish|food/i.test(text)
    const wantsPlanner = /plan|weekly|meal plan|breakfast|lunch|dinner|replace|healthier|cheaper/i.test(text)
    const wantsCart = /cart|add|remove|checkout|buy/i.test(text)

    dispatch({ type: 'SET_ERROR', payload: null })
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage })
    dispatch({ type: 'SET_LOADING', payload: true })
    dispatch({ type: 'SET_TYPING', payload: true })
    if (wantsRecommendations) setLoadingState('recommendations', true)
    if (wantsPlanner) setLoadingState('planner', true)
    if (wantsCart) setLoadingState('cart', true)
    setLoadingState('chat', true)

    try {
      const response = await apiSendMessage(text.trim(), state.sessionId)
      const payload = getPayload(response)
      const data = getData(response)
      const intent = response?.intent ?? payload?.intent

      console.log('================================')
      console.log('[APPSTORE LOG] response object:', response)
      console.log('[APPSTORE LOG] typeof response:', typeof response)
      console.log('[APPSTORE LOG] response keys:', response ? Object.keys(response) : null)
      console.log('================================')
      console.log('[APPSTORE LOG] Extracted data:', data)
      console.log('[APPSTORE LOG] recommendations:', data?.recommendations)
      console.log('[APPSTORE LOG] meal_plan:', data?.meal_plan)
      console.log('[APPSTORE LOG] planner:', data?.planner)
      console.log('[APPSTORE LOG] cart:', data?.cart)

      // 1. Instantly Sync Core States (Server is the Absolute Source of Truth)
      if (data.cart) {
        console.log('[APPSTORE LOG] Dispatch: SET_CART', data.cart)
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Cart updated' } })
      } else if (['add_to_cart', 'remove_from_cart', 'view_cart', 'checkout_cart', 'cart_action', 'multi_action'].includes(intent)) {
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'syncing', message: 'Syncing cart…' } })
        sendTelemetry('missing_cart_in_response', { intent: response.intent, session_id: state.sessionId, response })
        await syncCart()
      }

      if (Array.isArray(data.recommendations)) {
        console.log('[APPSTORE LOG] Dispatch: SET_RECOMMENDATIONS', data.recommendations)
        dispatch({ type: 'SET_RECOMMENDATIONS', payload: data.recommendations })
      }

      const mealPlanData = data.meal_plan || payload.meal_plan || response?.meal_plan || data.planner || payload.planner || response?.planner
      if (mealPlanData) {
        console.log('[APPSTORE LOG] Dispatch: SET_PLANNER', mealPlanData)
        dispatch({ type: 'SET_PLANNER', payload: mealPlanData })
        toast.success('7-Day Meal Plan generated!')
      }

      if (data.order) {
        dispatch({ type: 'SET_ORDER', payload: data.order })
      }

      setLoadingState('recommendations', false)
      setLoadingState('planner', false)
      setLoadingState('cart', false)

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        author: 'assistant',
        text: response.response || 'The assistant did not return a message.',
        data,
        timestamp: new Date().toISOString(),
      }

      await new Promise((resolve) => setTimeout(resolve, 500 + Math.random() * 700))
      console.log('[APPSTORE LOG] Dispatch: ADD_MESSAGE', assistantMessage)
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.response?.data?.message || err.response?.data?.error || err.message || 'Unexpected error'
      dispatch({ type: 'SET_ERROR', payload: `Chat request failed: ${backendError}` })
      toast.error(`Request failed: ${backendError}`)
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-error-${Date.now()}`,
          author: 'assistant',
          text: `I could not complete the request: ${backendError}`,
          data: {},
          timestamp: new Date().toISOString(),
        },
      })
      throw err
    } finally {
      dispatch({ type: 'SET_TYPING', payload: false })
      dispatch({ type: 'SET_LOADING', payload: false })
      setLoadingState('chat', false)
    }
  }

  const addToCart = async (item, quantity = 1) => {
    if (!item || typeof item.item_id !== 'number') {
      dispatch({ type: 'SET_ERROR', payload: 'Can only add valid menu items to cart.' })
      toast.error('Can only add valid menu items to cart.')
      return null
    }

    dispatch({ type: 'SET_LOADING', payload: true })
    dispatch({ type: 'SET_ERROR', payload: null })
    setLoadingState('cart', true)
    dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'syncing', message: 'Adding item to cart…' } })

    try {
      const response = await apiAddCartItem(state.sessionId, item.item_id, quantity)
      const payload = getPayload(response)
      const data = getData(response)

      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Item added' } })
      } else {
        await syncCart()
      }

      toast.success(`Added ${item.item_name ?? item.name ?? 'item'} to cart!`)

      const updatedCart = data.cart || state.cart
      const cartItemsCount = updatedCart?.items?.reduce((acc, i) => acc + (i.quantity || 1), 0) || 1
      const subtotal = updatedCart?.subtotal || item.price || 0

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-${Date.now()}`,
          author: 'assistant',
          text: `Added ${item.item_name ?? item.name ?? 'item'} to your cart. Your cart now has ${cartItemsCount} item${cartItemsCount === 1 ? '' : 's'} (Subtotal: ₹${subtotal}).`,
          data: { cart: updatedCart },
          timestamp: new Date().toISOString(),
        },
      })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Could not add item to cart.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      toast.error(`Could not add item: ${backendError}`)
      dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'error', message: 'Cart update failed' } })
      throw err
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
      setLoadingState('cart', false)
    }
  }

  const removeFromCart = async (item, quantity = 1) => {
    if (!item || typeof item.item_id !== 'number') {
      dispatch({ type: 'SET_ERROR', payload: 'Can only remove valid cart items.' })
      return null
    }

    dispatch({ type: 'SET_LOADING', payload: true })
    dispatch({ type: 'SET_ERROR', payload: null })
    setLoadingState('cart', true)

    try {
      const response = await apiRemoveCartItem(state.sessionId, item.item_id, quantity)
      const payload = getPayload(response)
      const data = getData(response)

      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Item removed' } })
      } else {
        await syncCart()
      }

      toast.success(`Removed ${item.item_name ?? item.name ?? 'item'} from cart`)

      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Could not remove item from cart.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      toast.error(`Could not remove item: ${backendError}`)
      throw err
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
      setLoadingState('cart', false)
    }
  }

  const checkout = async () => {
    dispatch({ type: 'SET_LOADING', payload: true })
    dispatch({ type: 'SET_ERROR', payload: null })
    setLoadingState('checkout', true)
    dispatch({ type: 'SET_CHECKOUT_STATUS', payload: { inProgress: true, success: false, message: 'Processing checkout…' } })

    try {
      const response = await apiCheckoutCart(state.sessionId)
      const payload = getPayload(response)
      const data = getData(response)

      const orderObj = data.order || { order_id: `ORD-${Date.now().toString().slice(-6)}`, total: state.cart?.total || 450, eta: '25-30 mins' }

      if (data.order) {
        dispatch({ type: 'SET_ORDER', payload: data.order })
        dispatch({ type: 'SET_CHECKOUT_STATUS', payload: { inProgress: false, success: true, message: 'Checkout complete' } })
      }
      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
      } else {
        dispatch({ type: 'CLEAR_CART' })
      }
      toast.success('Order placed successfully! 🎉')

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-order-${Date.now()}`,
          author: 'assistant',
          text: `🎉 Order Confirmed! Your order (${orderObj.order_id || 'ORD-CONFIRMED'}) for ₹${orderObj.total || state.cart?.total || 0} has been placed. Estimated delivery time: 25-30 mins.`,
          data: { order: orderObj },
          timestamp: new Date().toISOString(),
        },
      })

      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Checkout failed.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      toast.error(`Checkout failed: ${backendError}`)
      throw err
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
      setLoadingState('checkout', false)
    }
  }

  const resetGuestSession = () => {
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem('swiggy_guest_session')
      window.localStorage.removeItem('swiggy_copilot_planner')
    }
    const newSessionId = generateSessionId()
    dispatch({ type: 'RESET_GUEST_SESSION', payload: { newSessionId } })
    toast.success('Started a fresh guest session!')
  }

  const requestMealPlan = async () => {
    setLoadingState('planner', true)
    try {
      return await sendChat('Create a weekly meal plan with breakfast, lunch, and dinner recommendations, including estimated cost for each day.')
    } finally {
      setLoadingState('planner', false)
    }
  }

  const removeRecommendation = (item) => {
    const key = item?.item_id ?? item?.item_name ?? item?.name
    if (!key) return
    dispatch({ type: 'REMOVE_RECOMMENDATION', payload: key })
  }

  const replaceRecommendation = async (item) => {
    const label = item?.item_name ?? item?.name ?? 'this recommendation'
    removeRecommendation(item)
    return sendChat(`Show me a replacement recommendation instead of ${label}.`)
  }

  const value = useMemo(
    () => ({
      state,
      actions: {
        syncCart,
        sendChat,
        addToCart,
        removeFromCart,
        checkout,
        requestMealPlan,
        removeRecommendation,
        replaceRecommendation,
        resetGuestSession,
        toggleTheme: () => dispatch({ type: 'TOGGLE_THEME' }),
      },
    }),
    [state, syncCart, sendChat, addToCart, removeFromCart, checkout, requestMealPlan, removeRecommendation, replaceRecommendation, resetGuestSession]
  )

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useAppStore() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppStore must be used within AppProvider')
  }
  return context
}

export function useAppState() {
  return useAppStore().state
}

export function useAppActions() {
  return useAppStore().actions
}
