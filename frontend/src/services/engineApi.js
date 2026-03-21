import axios from 'axios'

// dedicated API client for the FastAPI
const engineApi = axios.create({
  baseURL: 'http://localhost:8001/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
})

export default engineApi