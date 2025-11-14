import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createDialog } from './utils/dialogs'
import { initSocket } from './socket'
import router from './router'
import translationPlugin from './translation'
import { posthogPlugin } from './telemetry'
import { startHeartbeat } from './heartbeat'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
} from 'frappe-ui'

let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
}

let pinia = createPinia()
let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.use(translationPlugin)
app.use(posthogPlugin)

for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

app.config.globalProperties.$dialog = createDialog

let socket

function mountApp() {
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  app.mount('#app')

  startHeartbeat()
}

if (import.meta.env.DEV) {
  frappeRequest({
    url: '/api/method/crm.www.crm.get_context_for_dev',
  }).then((values) => {
    for (let key in values) {
      window[key] = values[key]
    }
    mountApp()
  })
} else {
  mountApp()
}

if (import.meta.env.DEV) {
  window.$dialog = createDialog
}
