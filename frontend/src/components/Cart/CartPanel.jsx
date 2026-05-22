import { useAppActions, useAppState } from '../../store/AppStore'

function CartPanel() {
  const { cart, orderStatus, cartSyncStatus, checkoutStatus, loadingStates, loading } = useAppState()
  const { addToCart, removeFromCart, checkout } = useAppActions()

  const items = cart?.items || []
  const cartLoading = loadingStates?.cart
  const processing = checkoutStatus?.inProgress
  const subtotal = cart?.subtotal ?? 0
  const tax = cart?.tax ?? 0
  const deliveryFee = cart?.delivery_fee ?? 0
  const total = cart?.total ?? subtotal + tax + deliveryFee

  const statusLabel = {
    idle: 'Cart is idle',
    syncing: 'Syncing cart…',
    synced: 'Cart synced',
    error: 'Cart sync error',
  }[cartSyncStatus?.status || 'idle']

  const statusClass = {
    idle: 'bg-slate-100 text-slate-600',
    syncing: 'bg-amber-50 text-amber-700',
    synced: 'bg-emerald-50 text-emerald-700',
    error: 'bg-rose-50 text-rose-700',
  }[cartSyncStatus?.status || 'idle']

  return (
    <div className="space-y-5">
      <div className="rounded-3xl bg-slate-950 p-5 text-white shadow-lg shadow-slate-950/10">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Cart overview</p>
            <h2 className="mt-3 text-2xl font-semibold">Shopping panel</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">Live cart updates from the shared application state.</p>
          </div>
          <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass}`}>
            {statusLabel}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/50 dark:border-slate-700 dark:bg-slate-950">
        <div className="space-y-4">
          {cartLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, index) => (
                <div key={index} className="rounded-3xl bg-slate-50 p-4 shadow-sm dark:bg-slate-900">
                  <div className="h-4 w-2/3 rounded-full bg-slate-200 dark:bg-slate-800" />
                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="h-8 w-3/5 rounded-full bg-slate-200 dark:bg-slate-800" />
                    <div className="h-8 w-16 rounded-full bg-slate-200 dark:bg-slate-800" />
                  </div>
                </div>
              ))}
            </div>
          ) : items.length > 0 ? (
            items.map((item) => (
              <div key={item.item_id} className="rounded-3xl bg-slate-50 p-4 shadow-sm dark:bg-slate-900">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-slate-100">{item.name}</p>
                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{item.restaurant_name}</p>
                    <p className="mt-2 text-sm font-semibold text-slate-900 dark:text-slate-100">₹{item.price}</p>
                  </div>
                  <div className="flex flex-col gap-3 sm:items-end">
                    <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                      Qty
                      <button
                        type="button"
                        onClick={() => removeFromCart(item, 1)}
                        disabled={loading || item.quantity <= 0}
                        className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
                      >
                        −
                      </button>
                      <span className="min-w-[32px] text-center text-sm font-semibold text-slate-900 dark:text-slate-100">{item.quantity}</span>
                      <button
                        type="button"
                        onClick={() => addToCart(item, 1)}
                        disabled={loading}
                        className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-swiggy-500 text-white transition hover:bg-swiggy-600 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        +
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFromCart(item, item.quantity)}
                      disabled={loading}
                      className="rounded-full bg-rose-50 px-4 py-2 text-xs font-semibold text-rose-600 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-3xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-900 dark:text-slate-300">
              Your cart is empty. Add a recommendation or ask the assistant to fill it.
            </div>
          )}

          <div className="space-y-3 rounded-3xl bg-slate-100 p-4 text-sm dark:bg-slate-900">
            <div className="flex items-center justify-between text-slate-600 dark:text-slate-300">
              <span>Subtotal</span>
              <span>₹{subtotal}</span>
            </div>
            <div className="flex items-center justify-between text-slate-600 dark:text-slate-300">
              <span>Tax</span>
              <span>₹{tax}</span>
            </div>
            <div className="flex items-center justify-between text-slate-600 dark:text-slate-300">
              <span>Delivery</span>
              <span>₹{deliveryFee}</span>
            </div>
            <div className="flex items-center justify-between rounded-3xl bg-slate-200 px-4 py-3 font-semibold text-slate-900 shadow-sm dark:bg-slate-800 dark:text-slate-100">
              <span>Total</span>
              <span>₹{total}</span>
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={checkout}
          disabled={items.length === 0 || checkoutStatus?.inProgress || loading}
          className="mt-4 w-full rounded-3xl bg-orange-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {checkoutStatus?.inProgress ? 'Processing...' : 'Checkout'}
        </button>

        {orderStatus ? (
          <div className="mt-4 rounded-2xl border border-slate-100 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-900">
            <p className="font-semibold text-slate-900 dark:text-slate-100">Last order: {orderStatus.order_id}</p>
            <p className="text-xs text-slate-600 dark:text-slate-400">Status: {orderStatus.status || 'n/a'}</p>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default CartPanel
