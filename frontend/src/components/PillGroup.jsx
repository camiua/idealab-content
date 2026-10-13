// Grupo de opciones en forma de píldoras. Por dentro son botones de radio:
// solo se puede elegir una opción y se manejan con el teclado (flechas).
export default function PillGroup({ label, name, options, value, onChange }) {
  return (
    <fieldset>
      <legend className="mb-2 text-sm font-bold">{label}</legend>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const selected = option.value === value
          return (
            <label
              key={option.value}
              className={`cursor-pointer rounded-full border-2 border-black px-4 py-1.5 text-sm font-bold transition has-[:focus-visible]:outline-3 has-[:focus-visible]:outline-offset-2 dark:border-paper ${
                selected
                  ? 'bg-black text-white dark:bg-paper dark:text-carbon'
                  : 'bg-white hover:bg-neutral-100 dark:bg-carbon dark:hover:bg-neutral-800'
              }`}
            >
              <input
                type="radio"
                name={name}
                value={option.value}
                checked={selected}
                onChange={() => onChange(option.value)}
                className="sr-only"
              />
              {option.label}
            </label>
          )
        })}
      </div>
    </fieldset>
  )
}