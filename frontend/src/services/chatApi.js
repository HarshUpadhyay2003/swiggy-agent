import api from './api'

export async function sendMessage(message, session_id) {
  const payload = {
    message,
    session_id,
    user_context: {
      session_id,
    },
  }

  const response = await api.post('/chat', payload)
  return response.data
}

export async function addCartItem(session_id, item_id, quantity = 1) {
  const payload = { session_id, item_id, quantity }
  const response = await api.post('/cart/add', payload)
  return response.data
}

export async function removeCartItem(session_id, item_id, quantity) {
  const payload = { session_id, item_id }
  if (quantity != null) {
    payload.quantity = quantity
  }
  const response = await api.post('/cart/remove', payload)
  return response.data
}

export async function checkoutCart(session_id) {
  const payload = { session_id }
  const response = await api.post('/cart/checkout', payload)
  return response.data
}

export async function getCart(session_id) {
  const response = await api.get('/cart', { params: { session_id } })
  return response.data
}

// Lightweight telemetry helper (fire-and-forget). Backend may ignore /telemetry.
export function sendTelemetry(event, payload = {}) {
  try {
    api.post('/telemetry', { event, payload }).catch((e) => {
      // Swallow telemetry errors; do not interrupt UX
      console.debug('[ChatApi] Telemetry not accepted by backend or failed:', e?.message || e)
    })
  } catch (err) {
    console.debug('[ChatApi] Telemetry call failed synchronously:', err?.message || err)
  }
}
