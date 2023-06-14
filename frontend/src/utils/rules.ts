export const required = [
  (value: string) => !!value || 'This field is required.',
]

export const minLength = (length: number) => [
  (value: string) =>
    value.length >= length ||
    `This field must be at least ${length} characters long.`,
]

export const maxLength = (max: number) => [
  (value: string) =>
    !value || value.length <= max || `Maximum ${max} characters allowed.`,
]

export const emailFormat = [
  (value: string) => /.+@.+\..+/.test(value) || 'Email must be valid.',
]

export const phoneNumber = [
  (value: string) => {
    if (!value) return true
    if (value.length === 9 || value.length === 10) {
      if (/^[0-9]*$/.test(value)) return true
      return 'Phone number can only contain numbers.'
    }
    return 'Phone number must contain exactly 9 or 10 digits.'
  },
]

export const alphanumeric = [
  (value: string) =>
    !value ||
    /^[a-z0-9]+$/i.test(value) ||
    'Only alphanumeric characters are allowed.',
]

export const alphanumericAndSpace = [
  (value: string) =>
    !value ||
    /^[a-z0-9 ]*$/i.test(value) ||
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

export const rules = {
  minLength,
  maxLength,
  alphanumeric,
  alphanumericAndSpace,
  passwordMatch,
  required,
  emailFormat,
  phoneNumber,
  nonNumericCharacter,

  email: [...required, ...emailFormat],
  password: [...required, ...minLength(8), ...nonNumericCharacter],
  requiredName: [...required, ...maxLength(30), ...alphanumericAndSpace],
  name: [...maxLength(30), ...alphanumericAndSpace],
}
