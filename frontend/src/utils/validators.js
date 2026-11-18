const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validateRequired(value, label = 'This field') {
  return String(value ?? '').trim() ? '' : `${label} is required.`
}

export function validateEmail(value) {
  return EMAIL_PATTERN.test(String(value || '').trim()) ? '' : 'Enter a valid email address.'
}

export function validatePassword(value, minimumLength = 12) {
  if (typeof value !== 'string' || value.length < minimumLength) {
    return `Password must contain at least ${minimumLength} characters.`
  }
  return ''
}

export function validateMaxLength(value, maximum, label = 'This field') {
  return String(value ?? '').length <= maximum ? '' : `${label} must be ${maximum} characters or fewer.`
}

export function validateForm(values, rules) {
  return Object.entries(rules).reduce((errors, [field, validators]) => {
    const fieldValidators = Array.isArray(validators) ? validators : [validators]
    for (const validator of fieldValidators) {
      const error = validator(values[field], values)
      if (error) {
        errors[field] = error
        break
      }
    }
    return errors
  }, {})
}