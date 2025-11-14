export function startHeartbeat() {
  const INTERVAL = 15000

  async function ping() {
    try {
      await frappe.call({
        method: 'crm.heartbeat.ping',
        freeze: false,
      })
    } catch (e) {
      console.warn('Heartbeat error:', e)
    }
  }

  setInterval(ping, INTERVAL)
  ping()
}
