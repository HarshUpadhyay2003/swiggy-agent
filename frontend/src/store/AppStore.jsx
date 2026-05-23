import { createContext, useContext, useEffect, useMemo, useReducer } from 'react'
import {
  sendMessage as apiSendMessage,
  addCartItem as apiAddCartItem,
  removeCartItem as apiRemoveCartItem,
  checkoutCart as apiCheckoutCart,
  getCart as apiGetCart,
  sendTelemetry,
} from '../services/chatApi'

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
      text: 'Hello! I am your AI commerce copilot. Ask me to recommend meals, manage your cart, or place an order.',
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
  switch (action.type) {
    case 'INIT_APP':
      return {
        ...state,
        sessionId: action.payload.sessionId,
        theme: action.payload.theme,
      }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_LOADING_STATE':
      return {
        ...state,
        loadingStates: {
          ...state.loadingStates,
          [action.payload.key]: action.payload.value,
        },
      }
    case 'SET_TYPING':
      return { ...state, typing: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] }
    case 'SET_RECOMMENDATIONS':
      return { ...state, recommendations: dedupeRecommendations(action.payload || []) }
    case 'REMOVE_RECOMMENDATION':
      return {
        ...state,
        recommendations: state.recommendations.filter((item) => {
          const id = item.item_id ?? item.item_name ?? item.name
          return id !== action.payload
        }),
      }
    case 'SET_CART':
      return { ...state, cart: buildCart(action.payload || {}) }
    case 'CLEAR_CART':
      return { ...state, cart: DEFAULT_CART }
    case 'SET_PLANNER':
      // Deep clone to force React to drop stale closures and completely re-render the Planner Panel
      return { ...state, planner: action.payload ? JSON.parse(JSON.stringify(action.payload)) : {} }
    case 'SET_ORDER':
      return { ...state, orderStatus: action.payload || null }
    case 'SET_CHECKOUT_STATUS':
      return { ...state, checkoutStatus: { ...state.checkoutStatus, ...action.payload } }
    case 'SET_CART_SYNC_STATUS':
      return { ...state, cartSyncStatus: { ...state.cartSyncStatus, ...action.payload } }
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'dark' ? 'light' : 'dark' }
    default:
      return state
  }
}

const generateSessionId = () => `session-${Date.now()}-${Math.floor(Math.random() * 10000)}`

const initializeState = () => {
  let sessionId = generateSessionId()
  let theme = 'light'

  if (typeof window !== 'undefined') {
    const storedSession = window.localStorage.getItem('swiggy_copilot_session')
    const storedTheme = window.localStorage.getItem('swiggy_theme')
    sessionId = storedSession || sessionId
    theme = storedTheme === 'dark' ? 'dark' : 'light'
    window.localStorage.setItem('swiggy_copilot_session', sessionId)
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

      // 1. Instantly Sync Core States (Server is the Absolute Source of Truth)
      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Cart updated' } })
      } else if (['add_to_cart', 'remove_from_cart', 'view_cart', 'checkout_cart', 'cart_action', 'multi_action'].includes(intent)) {
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'syncing', message: 'Syncing cart…' } })
        sendTelemetry('missing_cart_in_response', { intent: response.intent, session_id: state.sessionId, response })
        await syncCart()
      }

      if (Array.isArray(data.recommendations)) {
        dispatch({ type: 'SET_RECOMMENDATIONS', payload: data.recommendations })
      }

      if (data.meal_plan) {
        dispatch({ type: 'SET_PLANNER', payload: data.meal_plan })
      }

      if (data.order) {
        dispatch({ type: 'SET_ORDER', payload: data.order })
      }

      // 2. Clear UI loading states instantly so panels update immediately
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

      // 3. Fake typing delay ONLY for the conversational message bubble (Prevents delayed UI syncs)
      await new Promise((resolve) => setTimeout(resolve, 500 + Math.random() * 700))
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.response?.data?.message || err.response?.data?.error || err.message || 'Unexpected error'
      dispatch({ type: 'SET_ERROR', payload: `Chat request failed: ${backendError}` })
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
        // Enforce server truth fallback
        await syncCart()
      }

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-${Date.now()}`,
          author: 'assistant',
          text: `Added ${item.item_name ?? item.name ?? 'item'} to your cart.`,
          data: { cart: data.cart },
          timestamp: new Date().toISOString(),
        },
      })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Could not add item to cart.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
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
    dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'syncing', message: 'Removing item from cart…' } })

    try {
      const response = await apiRemoveCartItem(state.sessionId, item.item_id, quantity)
      const payload = getPayload(response)
      const data = getData(response)

      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
        dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Item removed' } })
      } else {
        // Enforce server truth fallback
        await syncCart()
      }

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-${Date.now()}`,
          author: 'assistant',
          text: `Updated your cart.`,
          data: { cart: data.cart },
          timestamp: new Date().toISOString(),
        },
      })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Could not remove item from cart.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'error', message: 'Cart update failed' } })
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
    dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'syncing', message: 'Checking out…' } })

    try {
      const response = await apiCheckoutCart(state.sessionId)
      const payload = getPayload(response)
      const data = getData(response)

      if (data.order) {
        dispatch({ type: 'SET_ORDER', payload: data.order })
        dispatch({ type: 'SET_CHECKOUT_STATUS', payload: { inProgress: false, success: true, message: 'Checkout complete' } })
      }
      if (data.cart) {
        dispatch({ type: 'SET_CART', payload: data.cart })
      } else {
        dispatch({ type: 'CLEAR_CART' })
      }
      dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'synced', message: 'Checkout complete' } })
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `assistant-${Date.now()}`,
          author: 'assistant',
          text: data.order
            ? `Your order ${data.order.order_id} is confirmed.`
            : 'Your checkout is complete.',
          data: { order: data.order, cart: data.cart },
          timestamp: new Date().toISOString(),
        },
      })
      return response
    } catch (err) {
      const backendError = err.response?.data?.detail || err.message || 'Checkout failed.'
      dispatch({ type: 'SET_ERROR', payload: backendError })
      dispatch({ type: 'SET_CHECKOUT_STATUS', payload: { inProgress: false, success: false, message: 'Checkout failed' } })
      dispatch({ type: 'SET_CART_SYNC_STATUS', payload: { status: 'error', message: 'Checkout failed' } })
      throw err
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
      setLoadingState('checkout', false)
    }
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
        toggleTheme: () => dispatch({ type: 'TOGGLE_THEME' }),
      },
    }),
    [state, syncCart, sendChat, addToCart, removeFromCart, checkout, requestMealPlan, removeRecommendation, replaceRecommendation]
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
