export default function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark'
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      className="rounded-full border-3 border-black bg-white px-4 py-1.5 font-bold shadow-brutal-sm transition active:translate-x-0.5 active:translate-y-0.5 active:shadow-none dark:border-paper dark:bg-carbon dark:shadow-brutal-paper-sm"
    >
      {isDark ? '○ Claro' : '● Oscuro'}
    </button>
  )
}