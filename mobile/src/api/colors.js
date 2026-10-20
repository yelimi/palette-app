import { apiFetch } from './client';

export function extractColor(imageAsset) {
  const formData = new FormData();
  formData.append('file', {
    uri: imageAsset.uri,
    name: imageAsset.fileName || 'photo.jpg',
    type: imageAsset.mimeType || 'image/jpeg',
  });
  return apiFetch('/colors/extract', {
    method: 'POST',
    body: formData,
  });
}
