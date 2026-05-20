import axios from 'axios'

const baseURL = 'http://localhost:8001/'
const wsURL = 'ws://localhost:8001/ws'

const engineApi = axios.create({
  baseURL: baseURL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
})

let ws = null

export const connectEngineWS = () => {
  if (!ws || ws.readyState === WebSocket.CLOSED) {
    ws = new WebSocket(wsURL)
  }
  return ws
}

export const sendWSTrigger = (trigger_value, description = '') => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ trigger_value, description }))
  }
}

export default engineApi