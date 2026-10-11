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

        <main>
          <p className="text-neutral-600 dark:text-stone-400">Aquí irá el formulario.</p>
        </main>
      </div>
    </div>
  )
}
