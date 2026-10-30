export function debounce<A extends unknown[]>(
  fn: (...args: A) => void,
  delay = 300,
): (...args: A) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  return (...args: A) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}
export function debounceImmediate<A extends unknown[]>(
  fn: (...args: A) => void,
  delay = 300,
): (...args: A) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  let isFirst = true

  return (...args: A) => {
    if (isFirst) {
      fn(...args)
      isFirst = false
    }
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      isFirst = true
    }, delay)
  }
}
