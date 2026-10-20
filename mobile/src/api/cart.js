import { apiFetch } from './client';

export function getCart() {
  return apiFetch('/cart');
}

export function addToCart(productId) {
  return apiFetch('/cart', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId }),
  });
}

export function removeFromCart(cartId) {
  return apiFetch(`/cart/${cartId}`, { method: 'DELETE' });
}
