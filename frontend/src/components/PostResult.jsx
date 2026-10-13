import { useState } from 'react'
import Markdown from 'react-markdown'
import { X_MAX, xLength } from '../utils/xLength.js'

const PLATFORM_NAMES = { x: 'X', instagram: 'Instagram', linkedin: 'LinkedIn', blog: 'Blog' }
const PROVIDER_NAMES = { groq: 'Groq', ollama: 'Ollama' }

const CARD =
  'flex h-full flex-col rounded-2xl border-3 border-black bg-white p-5 shadow-brutal sm:p-6 dark:border-paper dark:bg-carbon dark:shadow-brutal-paper'
const SMALL_BUTTON =
  'rounded-full border-2 border-black px-4 py-1.5 text-sm font-bold transition hover:bg-neutral-100 active:translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40 dark:border-paper dark:hover:bg-neutral-800'

// Estilos del Markdown del blog (títulos, párrafos y listas)
const MARKDOWN =
  'space-y-4 leading-relaxed [&_h1]:font-display [&_h1]:text-2xl [&_h2]:mt-6 [&_h2]:font-display [&_h2]:text-lg [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6 [&_strong]:font-bold'

export default function PostResult({ result, loading, error, onRegenerate }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(result.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // 1. Cargando
  if (loading) {
    return (
      <div className={`${CARD} animate-pulse`}>
        <p className="font-display text-lg">Generando tu post…</p>
        <div className="mt-5 space-y-3" aria-hidden="true">
          <div className="h-3 w-full rounded-full bg-neutral-200 dark:bg-neutral-700" />
          <div className="h-3 w-11/12 rounded-full bg-neutral-200 dark:bg-neutral-700" />
          <div className="h-3 w-4/5 rounded-full bg-neutral-200 dark:bg-neutral-700" />
        </div>
      </div>
    )
  }

  // 2. Error
  if (error) {
    return (
      <div role="alert" className={CARD}>
        <p className="font-display text-lg">No se ha podido generar</p>
        <p className="mt-2">{error}</p>
      </div>
    )
  }

  // 3. Vacío: todavía no se ha generado nada
  if (!result) {
    return (
      <div className="h-full rounded-2xl border-3 border-dashed border-neutral-400 p-6 text-neutral-500 dark:border-stone-600 dark:text-stone-400">
        <p className="font-display text-lg">Tu post aparecerá aquí</p>
        <p className="mt-2">Elige un tema, la plataforma y el público, y pulsa «Generar post».</p>
      </div>
    )
  }

  // 4. Resultado
  const isX = result.platform === 'x'
  const count = isX ? xLength(result.content) : 0
  const seconds = (result.metrics.elapsed_ms / 1000).toFixed(1).replace('.', ',')

  return (
    <article className={CARD}>
      <header className="flex flex-wrap items-center justify-between gap-3">
        <span className="rounded-full bg-black px-3 py-1 text-sm font-bold text-white dark:bg-paper dark:text-carbon">
          {PLATFORM_NAMES[result.platform]}
        </span>
        <button type="button" onClick={handleCopy} className={SMALL_BUTTON}>
          {copied ? '✓ Copiado' : 'Copiar texto'}
        </button>
      </header>

        <div
        role="region"
        aria-label="Texto del post"
        tabIndex={0}
        className= "mt-5 min-h-0 flex-1 focus-visible:outline-3 focus-visible:outline-offset-4 lg:overflow-y-auto lg:pr-3"
        >
        {result.platform === 'blog' ? (
          <div className={MARKDOWN}>
            <Markdown>{result.content}</Markdown>
          </div>
        ) : (
          <p className="whitespace-pre-wrap leading-relaxed">{result.content}</p>
        )}
      </div>

      {isX && (
        <p className={`mt-4 text-right text-sm font-bold ${count > X_MAX ? 'text-red-600 dark:text-red-400' : ''}`}>
          {count} / {X_MAX} caracteres
        </p>
      )}

      {result.warnings.length > 0 && (
        <ul className="mt-4 space-y-1 rounded-xl border-2 border-black bg-neutral-100 p-3 text-sm dark:border-paper dark:bg-neutral-800">
          {result.warnings.map((warning) => (
            <li key={warning}>⚠ {warning}</li>
          ))}
        </ul>
      )}

      <footer className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t-2 border-dashed border-neutral-300 pt-4 text-sm text-neutral-600 dark:border-stone-600 dark:text-stone-400">
        <span>
          Generado con {PROVIDER_NAMES[result.provider]} ({result.model}) en {seconds} s
        </span>
        <button type="button" onClick={onRegenerate} className={`${SMALL_BUTTON} text-black dark:text-paper`}>
          Generar otra versión
        </button>
      </footer>
    </article>
  )
}