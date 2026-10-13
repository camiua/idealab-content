// Único punto de llamada al backend (plan §2.5, regla 1)
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function generatePost(payload) {
  let response
  try {
    response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch {
    throw new Error('No se puede conectar con el servidor. ¿Está arrancado el backend?')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail =
      typeof data?.detail === 'string'
        ? data.detail
        : 'No se ha podido generar el post. Revisa los datos e inténtalo de nuevo.'
    throw new Error(detail)
  }
  return data
}