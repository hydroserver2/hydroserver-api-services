import { AxiosInstance } from 'axios'
import { ComponentInternalInstance, getCurrentInstance } from 'vue'

let app: ComponentInternalInstance | null = null

export function useApiClient() {
  if (!app) {
    app = getCurrentInstance()
  }
  const $http = app?.appContext.config.globalProperties.$http
  return $http as AxiosInstance
}

/** Transforms the values in a dictionary into strings, and filters out falsey entries and array entries
 * Array values need to be stringified with `stringifyArrayParamValues`
 * @returns the resulting object after filter and transformation
 */
function _stringifyPrimitiveParamValues(params: {
  [key: string]: string | string[]
}): { [key: string]: string } {
  return Object.fromEntries(
    Object.entries(params)
      .filter(([key, value]) => !Array.isArray(value) && !!value)
      .map(([key, value]) => {
        return [key, String(value)]
      })
  )
}

/** Filters array items from a param object and returns a concatenation of query strings
 * i.e: `{ foo: ['bar', 'baz'] }` => `'&foo=bar&foo=baz'`
 * @returns a concatenation of array query strings
 */
function _stringifyArrayParamValues(params: {
  [key: string]: string | string[]
}): string {
  return Object.entries(params)
    .filter(([key, value]) => Array.isArray(value) && value.length > 0)
    .map(([key, value]) => {
      return (value as string[])
        .map((v) => `&${key}=${encodeURIComponent(v)}`)
        .join('')
    })
    .join('')
}

export function getQueryString(params: {
  [key: string]: string | string[]
}): string {
  const primitiveParams = _stringifyPrimitiveParamValues(params)
  const arrayParams = _stringifyArrayParamValues(params)
  return `${new URLSearchParams(primitiveParams)}${arrayParams}`
}
