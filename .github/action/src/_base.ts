import { execSync } from 'node:child_process'
import type { IFallback, IHistory, IMatrixEntry } from './types'
import { DiffType } from './types'

type Members<Q> = { [T in keyof Q]: { T: Q[T] } }[keyof Q]

type DIffedType<P> = {
  [T in keyof P]: P[T] extends object ? DIffedType<P[T]> : DiffType
}

export abstract class Base {
  private modified: boolean = false
  constructor(
    private readonly next: Members<IMatrixEntry>,
    private readonly previous: Members<IHistory>,
    private readonly fallback: Members<IFallback>
  ) {
    process.on('exit', () => {
      if (this.modified) {
        this.updateEnvironment()
      }
    })
  }

  private getFallback(membership: string[], top: any = this.fallback): any {
    const _membership = [...membership]
    if (!membership.length) {
      if (top.$shell) {
        return execSync(top.$shell)
      } else if (top.$last) {
        const _do = (o: any, m: string[]): any => {
          if (!m.length) {
            return o
          }
          // @ts-ignore
          return _do(this.previous[m.shift() as string], m)
        }
        return _do(this.previous, _membership)
      }
    }
    return this.getFallback(membership, top[membership.shift() as string])
  }

  public get value(): unknown {
    if (!this.isEmpty()) {
      return this.next
    }

    // check for fallback values
    let state: string[] = []
    const fillEntry = (o: object, result: any) => {
      for (const [key, value] of Object.entries(o)) {
        if (typeof value === 'object') {
          state.push(key)
          result[key] = {}
          fillEntry(value, result[key])
          continue
        }

        result[key] = result[key] ?? this.getFallback(state, this.next)
        state = []
      }
    }

    const __entry = {}
    fillEntry(this.next, __entry)

    return __entry
  }

  public get diff(): unknown {
    const difference = this.compareFn<Members<IHistory>, Members<IMatrixEntry>>(
      this.previous,
      this.next
    )
    // TODO check this
    const __entry: any = {}

    const fillEntry = (o: typeof difference, result: any) => {
      for (const [key, value] of Object.entries(o)) {
        if (typeof value === 'object') {
          result[key] = {}
          fillEntry(value, result[key])
          continue
        }

        switch (value) {
          case DiffType.EQUAL:
            // @ts-ignore
            result[key] = { repeated: this.next[key] }
            break
          case DiffType.INCREASES:
            this.modified = true
            // @ts-ignore
            result[key] = { increased: this.next[key] }
            break
          case DiffType.DECREASED:
            this.modified = true
            // @ts-ignore
            result[key] = { decreased: this.next[key] }
            break
          case DiffType.CHANGED:
            this.modified = true
            // @ts-ignore
            result[key] = { changed: this.next[key] }
            break

          default:
            break
        }
      }
    }

    fillEntry(difference, __entry)

    return {
      ...difference,
      valueOf() {
        return __entry
      },
    }
  }

  abstract isEmpty(): boolean
  abstract compareFn<TPrev, TNext>(prev: TPrev, next: TNext): DIffedType<TNext>
  abstract updateEnvironment(): void
}
