export function useFormatters() {
  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString(undefined, {
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit'
    })
  }

  const getAbsoluteUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http')) return path
    const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/').replace(/\/api\/?$/, '')
    return baseUrl + path
  }

  return {
    formatDate,
    getAbsoluteUrl
  }
}