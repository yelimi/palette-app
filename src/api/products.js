import { apiFetch } from './client';

export function getProductsByColor(hex) {
  return apiFetch(`/products?color=${encodeURIComponent(hex)}&limit=20`);
}

export function getProduct(id) {
  return apiFetch(`/products/${id}`);
}
