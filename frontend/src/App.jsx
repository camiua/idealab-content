import { useState } from 'react'
import { generatePost } from './api/client.js'
import GeneratorForm from './components/GeneratorForm.jsx'
import Hero from './components/Hero.jsx'
import ThemeToggle from './components/ThemeToggle.jsx'
import { useTheme } from './hooks/useTheme.js'

function Logo() {
  return (
    <svg viewBox="0 0 44 44" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="h-8 w-8">
      <path d="M17 6h10M18.5 6v12L8 35.5A2.5 2.5 0 0 0 10.2 39h23.6a2.5 2.5 0 0 0 2.2-3.5L25.5 18V6" />
      <path d="M12 29c4-2 7 2 11 0s7-2 9 0" />
    </svg>
  )
}

export default function App() {
  const { theme, toggleTheme } = useTheme()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleGenerate(payload) {
    setLoading(true)
    setError(null)
    try {
      const data = await generatePost(payload)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen font-sans text-black dark:text-paper">
      <div className="px-4 pb-16 pt-5 sm:px-8 lg:px-16">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-display text-xl">
            <Logo />
            IdeaLab
          </div>
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </header>

        <Hero theme={theme} />

        <main className="mx-auto grid max-w-337 items-start gap-8 lg:grid-cols-2 lg:gap-12">
          <GeneratorForm onGenerate={handleGenerate} loading={loading} />

          {/* Provisional: en el siguiente paso lo sustituye PostResult */}
          <section aria-live="polite">
            {error && <p role="alert" className="font-bold">{error}</p>}
            {result && <pre className="whitespace-pre-wrap font-sans">{result.content}</pre>}
          </section>
        </main>
      </div>
    </div>
  )
}