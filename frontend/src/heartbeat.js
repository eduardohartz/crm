import { frappeRequest } from 'frappe-ui'

const INTERVAL = 15000

async function sendHeartbeat() {
  try {
    await frappeRequest({
      url: '/api/method/crm.crm.api.heartbeat.ping',
      method: 'POST',
    })
  } catch (err) {
    console.warn('Heartbeat failed:', err)
  }
}

export function startHeartbeat() {
  sendHeartbeat()
  setInterval(sendHeartbeat, INTERVAL)
}
