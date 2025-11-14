import { frappeRequest } from 'frappe-ui'

const INTERVAL = 15000 // 15 seconds

async function sendHeartbeat() {
  try {
    await frappeRequest({
      method: 'crm.heartbeat.ping',
    })
  } catch (err) {
    console.warn('Heartbeat failed:', err)
  }
}

export function startHeartbeat() {
  sendHeartbeat()
  setInterval(sendHeartbeat, INTERVAL)
}
