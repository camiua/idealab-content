import { Fragment } from 'react'
import PeepModule from 'react-peeps'

// react-peeps es un paquete antiguo (CommonJS): el componente llega dentro de .default
const Peep = PeepModule.default ?? PeepModule

const TITLE = 'Escribe un tema. Te devolvemos el post.'

function Monitor() {
  return (
    <svg viewBox="0 0 250 230" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className="w-28 shrink-0 sm:w-32">
      <rect x="10" y="10" width="230" height="150" rx="14" className="fill-white dark:fill-paper" />
      <rect x="30" y="30" width="190" height="110" rx="8" strokeWidth="3" />
      <path d="M48 54h120M48 72h150M48 90h96" strokeWidth="3" />
      <path d="M48 116h46" strokeWidth="6" />
      <path d="M108 160l-8 44M142 160l8 44M80 206h90" />
      <path d="M196 116l4 8 8 4-8 4-4 8-4-8-8-4 8-4z" fill="currentColor" strokeWidth="2" />
    </svg>
  )
}

export default function Hero({ theme }) {
  // La ilustración no se invierte: siempre trazo oscuro sobre su tarjeta clara
  const ink = theme === 'dark' ? '#1c1c1c' : '#000000'
  const card = theme === 'dark' ? '#f3efe6' : '#ffffff'

  return (
    <section className="flex flex-col gap-8 py-5 md:flex-row md:items-center md:justify-center lg:gap-16 lg:py-6">
      <div className="min-w-0 md:max-w-4xl">
        <h1 className="font-display text-4xl leading-[1.05] tracking-tight sm:text-5xl 2xl:text-6xl">
          {TITLE.split(' ').map((word, i) => (
            <Fragment key={i}>
              <span className="word-rise" style={{ animationDelay: `${300 + i * 150}ms` }}>
                {word}
              </span>{' '}
            </Fragment>
          ))}
        </h1>
        <p className="mt-4 max-w-[44ch] text-lg text-neutral-600 xl:text-xl dark:text-stone-400">
          Para blogs, Instagram, LinkedIn y X, con las reglas de cada red ya cumplidas: longitud, hashtags y tono para tu público.
        </p>
      </div>

      <div
        aria-hidden="true"
        className="flex w-full shrink-0 items-end justify-center rounded-2xl border-3 border-black bg-white p-3 text-black shadow-brutal md:w-80 lg:w-90 dark:border-paper dark:bg-paper dark:text-carbon dark:shadow-none"
      >
        <div className="w-32 shrink-0 sm:w-36">
          <Peep
            style={{ width: '100%', height: 'auto' }}
            body="Device"
            hair="Long"
            face="Smile"
            strokeColor={ink}
            backgroundColor={card}
          />
        </div>
        <Monitor />
      </div>
    </section>
  )
}