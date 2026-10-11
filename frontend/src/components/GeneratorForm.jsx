import { useState } from 'react'
import PillGroup from './PillGroup.jsx'

// Los valores coinciden con los que acepta la API (spec §1.3)
const PLATFORMS = [
  { value: 'x', label: 'X' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'blog', label: 'Blog' },
]

const AUDIENCES = [
  { value: 'general', label: 'General' },
  { value: 'profesional', label: 'Profesional' },
  { value: 'juvenil', label: 'Juvenil' },
  { value: 'infantil', label: 'Infantil' },
]

const PROVIDERS = [
  { value: 'groq', label: 'Groq · en la nube' },
  { value: 'ollama', label: 'Ollama · en local' },
]

const TOPIC_MIN = 3
const TOPIC_MAX = 200

export default function GeneratorForm({ onGenerate, loading }) {
  const [topic, setTopic] = useState('')
  const [platform, setPlatform] = useState('instagram')
  const [audience, setAudience] = useState('general')
  const [provider, setProvider] = useState('groq')

  const tooShort = topic.trim().length < TOPIC_MIN

  function handleSubmit(event) {
    event.preventDefault() // evita que el navegador recargue la página
    if (tooShort || loading) return
    onGenerate({ topic: topic.trim(), platform, audience, provider })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-2xl border-3 border-black bg-white p-5 shadow-brutal sm:p-6 dark:border-paper dark:bg-carbon dark:shadow-brutal-paper"
    >
      <div>
        <label htmlFor="topic" className="mb-2 block text-sm font-bold">
          Tema del post
        </label>
        <textarea
          id="topic"
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          maxLength={TOPIC_MAX}
          rows={3}
          placeholder="Ej.: café de especialidad para empezar bien el lunes"
          className="w-full resize-none rounded-xl border-2 border-black bg-white p-3 placeholder:text-neutral-400 focus:outline-3 focus:outline-offset-2 dark:border-paper dark:bg-carbon dark:placeholder:text-stone-500"
        />
        <p className="mt-1 text-right text-xs text-neutral-500 dark:text-stone-400">
          {topic.length} / {TOPIC_MAX}
        </p>
      </div>

      <PillGroup label="Plataforma" name="platform" options={PLATFORMS} value={platform} onChange={setPlatform} />
      <PillGroup label="Audiencia" name="audience" options={AUDIENCES} value={audience} onChange={setAudience} />
      <PillGroup label="Modelo" name="provider" options={PROVIDERS} value={provider} onChange={setProvider} />

      <button
        type="submit"
        disabled={tooShort || loading}
        className="w-full rounded-full border-3 border-black bg-black px-6 py-3 font-display text-lg text-white shadow-brutal-sm transition active:translate-x-0.5 active:translate-y-0.5 active:shadow-none disabled:cursor-not-allowed disabled:opacity-40 dark:border-paper dark:bg-paper dark:text-carbon dark:shadow-brutal-paper-sm"
      >
        {loading ? 'Generando…' : 'Generar post'}
      </button>
    </form>
  )
}