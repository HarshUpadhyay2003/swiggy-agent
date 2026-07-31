import React, { useState, useEffect } from 'react'
import { X, Plus, Minus, Trash2, Tag, ArrowRight, ShoppingBag, Check } from 'lucide-react'
import { useAppActions, useAppState } from '../../store/AppStore'
import { getFoodImage } from '../../assets/images'

export function CartDrawer({ isOpen, onClose }) {
  const { cart, checkoutStatus, loadingStates } = useAppState()
  const { addToCart, removeFromCart, checkout } = useAppActions()
  const [checkoutDone, setCheckoutDone] = useState(false)

  const isCheckoutLoading = loadingStates?.checkout

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose && onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const items = cart?.items || []
  const subtotal = cart?.subtotal || items.reduce((sum, item) => sum + (item.price || 0) * (item.quantity || 1), 0)
  const deliveryFee = subtotal > 0 ? 30 : 0
  const savings = subtotal > 300 ? 65 : 0
  const total = Math.max(0, subtotal + deliveryFee - savings)

  const handleCheckout = async () => {
    try {
      await checkout()
      setCheckoutDone(true)
      setTimeout(() => {
        setCheckoutDone(false)
        onClose && onClose()
      }, 2500)
    } catch (err) {
      console.error('Checkout failed:', err)
    }
  }

  const getItemImage = (item, index) => {
    return item.image_url || getFoodImage(item.name || item.item_name, index)
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-[90] animate-fadeIn"
        onClick={onClose}
      />

      {/* Slide-over Cart Drawer */}
      <aside className="fixed top-4 bottom-4 right-4 w-[calc(100%-32px)] md:w-[480px] z-[100] glass-panel rounded-2xl shadow-2xl border border-white/60 dark:border-slate-800 flex flex-col animate-slideLeft bg-white/95 dark:bg-slate-900/95 overflow-hidden">
        {/* Header */}
        <div className="p-5 flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800">
          <div>
            <h2 className="font-serif text-2xl font-bold text-slate-900 dark:text-slate-100">
              Your Cart
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              {items.length} {items.length === 1 ? 'item' : 'items'} selected
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Items Container */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6 scrollbar-thin">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center py-16 space-y-3">
              <div className="w-16 h-16 rounded-full bg-swiggy-500/10 text-swiggy-500 flex items-center justify-center">
                <ShoppingBag className="h-8 w-8" />
              </div>
              <h3 className="font-serif font-bold text-lg text-slate-900 dark:text-slate-100">
                Your cart is empty
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs">
                Explore our recommendations or generate a weekly meal plan to add delicious items.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item, idx) => (
                <div key={item.item_id || idx} className="flex gap-4 group items-start pb-4 border-b border-slate-100 dark:border-slate-800">
                  <div className="w-20 h-20 rounded-xl overflow-hidden shrink-0 shadow-sm bg-slate-100 dark:bg-slate-800">
                    <img
                      src={getItemImage(item, idx)}
                      alt={item.name || item.item_name}
                      className="w-full h-full object-cover transition-transform group-hover:scale-105 duration-300"
                      onError={(e) => {
                        e.target.onerror = null
                        e.target.src = getFoodImage(item.name || item.item_name, idx)
                      }}
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-serif font-bold text-base text-slate-900 dark:text-slate-100 truncate pr-2">
                        {item.name || item.item_name || 'Selected Item'}
                      </h3>
                      <span className="font-semibold text-sm text-slate-900 dark:text-slate-100 shrink-0">
                        ₹{(item.price || 0) * (item.quantity || 1)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-3 truncate">
                      {item.restaurant_name || 'Gourmet Kitchen'}
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-full p-1 border border-slate-200/60 dark:border-slate-700">
                        <button
                          type="button"
                          onClick={() => removeFromCart(item, 1)}
                          className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-white dark:hover:bg-slate-700 transition-colors text-swiggy-600"
                        >
                          <Minus className="h-3.5 w-3.5" />
                        </button>
                        <span className="px-3 font-semibold text-xs text-slate-900 dark:text-slate-100">
                          {item.quantity || 1}
                        </span>
                        <button
                          type="button"
                          onClick={() => addToCart(item, 1)}
                          className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-white dark:hover:bg-slate-700 transition-colors text-swiggy-600"
                        >
                          <Plus className="h-3.5 w-3.5" />
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeFromCart(item, item.quantity || 1)}
                        className="text-xs font-medium text-rose-500 hover:text-rose-600 transition-colors flex items-center gap-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" /> Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Savings Alert Banner */}
          {items.length > 0 && (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 p-3 rounded-xl flex gap-2.5 items-center text-xs text-emerald-800 dark:text-emerald-300">
              <Tag className="h-4 w-4 shrink-0 text-emerald-600" />
              <span>Yay! You're saving ₹65 on this order with <strong className="font-bold">CRAVE50</strong>.</span>
            </div>
          )}
        </div>

        {/* Footer Summary & Checkout */}
        {items.length > 0 && (
          <div className="p-5 bg-slate-50/80 dark:bg-slate-800/80 border-t border-slate-200/60 dark:border-slate-800 space-y-4">
            <div className="space-y-1.5 text-xs text-slate-600 dark:text-slate-300">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Fee</span>
                <span>₹{deliveryFee}</span>
              </div>
              <div className="flex justify-between text-emerald-600 dark:text-emerald-400 font-semibold">
                <span>Crave Savings</span>
                <span>-₹{savings}</span>
              </div>
              <div className="flex justify-between font-serif text-lg font-bold text-slate-900 dark:text-slate-100 pt-2 border-t border-slate-200 dark:border-slate-700">
                <span>Total</span>
                <span>₹{total}</span>
              </div>
            </div>

            <button
              type="button"
              disabled={isCheckoutLoading || checkoutDone}
              onClick={handleCheckout}
              className={`w-full ${
                checkoutDone ? 'bg-emerald-600' : 'bg-swiggy-500 hover:bg-swiggy-600'
              } text-white py-3.5 rounded-full font-bold text-base flex items-center justify-center gap-2 transition-all shadow-md active:scale-[0.99] disabled:opacity-70`}
            >
              {checkoutDone ? (
                <>
                  <Check className="h-5 w-5" /> Order Placed!
                </>
              ) : isCheckoutLoading ? (
                <span>Processing Order...</span>
              ) : (
                <>
                  Checkout <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
            <p className="text-center text-[10px] text-slate-400">
              Secure checkout powered by CraveAI Intelligence
            </p>
          </div>
        )}
      </aside>
    </>
  )
}

export default CartDrawer
