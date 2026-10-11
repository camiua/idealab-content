// Cuenta caracteres como X (la misma lógica que x_length en backend/app/services/generation.py):
// - los caracteres "normales" (hasta U+10FF: latín, acentos, ñ…) cuentan 1;
// - el resto (emojis, CJK…) cuenta 2;
// - los caracteres invisibles que unen emojis (U+200D y U+FE0F) no cuentan.
export const X_MAX = 280

export function xLength(text) {
  let total = 0
  for (const char of text) {
    const code = char.codePointAt(0)
    if (code === 0x200d || code === 0xfe0f) continue
    total += code <= 0x10ff ? 1 : 2
  }
  return total
}