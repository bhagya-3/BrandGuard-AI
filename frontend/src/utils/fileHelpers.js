import { ACCEPTED_FILE_TYPES, MAX_UPLOAD_SIZE_MB } from './constants.js'

export const acceptedFileTypes = ACCEPTED_FILE_TYPES

export function validateUploadFile(file, maxSizeMb = MAX_UPLOAD_SIZE_MB) {
  if (!(file instanceof File)) return 'Choose a file to upload.'
  if (file.size === 0) return 'The selected file is empty.'
  if (file.size > maxSizeMb * 1024 * 1024) {
    return `File exceeds the ${maxSizeMb} MB limit.`
  }
  const extension = file.name.split('.').pop()?.toLowerCase()
  const allowed = ACCEPTED_FILE_TYPES.split(',').map((item) => item.replace('.', ''))
  if (!extension || !allowed.includes(extension)) {
    return 'Choose a PDF, DOCX, PPTX, PNG, JPG, WEBP, or TXT file.'
  }
  return null
}

export function getFileExtension(filename = '') {
  return filename.includes('.') ? filename.split('.').pop().toLowerCase() : ''
}

export function downloadTextFile(filename, content, mimeType = 'text/plain;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([content], { type: mimeType }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.append(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}