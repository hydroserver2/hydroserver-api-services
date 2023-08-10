export const required = [
  (value: string) => !!value || 'This field is required.',
]

export const minLength = (length: number) => [
  (value: string) =>
    value.length >= length ||
    `This field must be at least ${length} characters long.`,
]

export const maxLength = (max: number) => [
  (value: string | number) =>
    !value || `${value}`.length <= max || `Maximum ${max} characters allowed.`,
]

export const emailFormat = [
  (value: string) => /.+@.+\..+/.test(value) || 'Email must be valid.',
]

export const phoneNumber = [
  (value: string) => {
    if (!value) return true
    const numericValue = value.replace(/\D/g, '')
    if (numericValue.length == 10) {
      if (/^[\d\+\-\(\)\s]*$/.test(value)) return true
      return 'Phone number can only contain digits, plus sign, parentheses, hyphens, and spaces.'
    }
    return 'Phone number must contain 10 digits.'
  },
]

export const alphanumeric = [
  (value: string) =>
    !value ||
    /^[a-z0-9]+$/i.test(value) ||
    'Only alphanumeric characters are allowed.',
]

export const nameRules = [
  (value: string) =>
    !value ||
    /^[a-z0-9 ._'-]*$/i.test(value) ||
    'Only alphanumeric characters and spaces are allowed.',
]

export const nonNumericCharacter = [
  (value: string) =>
    !value ||
    /\D/.test(value) ||
    'Must contain at least one non-numeric character.',
]

export const passwordMatch = (password: string) => [
  (value: string) => {
    return password === value || 'Passwords must match.'
  },
]

export const urlFormat = [
  (value: string) => {
    const pattern = new RegExp(
      '^(https?:\\/\\/)?' + // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
        '(\\#[-a-z\\d_]*)?$',
      'i'
    ) // fragment locator
    return pattern.test(value) || 'URL must be valid.'
  },
]

export const rules = {
  minLength,
  maxLength,
  alphanumeric,
  nameRules,
  passwordMatch,
  required,
  emailFormat,
  urlFormat,
  phoneNumber,
  nonNumericCharacter,

  email: [...required, ...emailFormat],
  password: [...required, ...minLength(8), ...nonNumericCharacter],
  requiredName: [...required, ...maxLength(200)],
  name: [...maxLength(200)],
  description: [...maxLength(1000), ...required],
  requiredCode: [...maxLength(200), ...required],
}
