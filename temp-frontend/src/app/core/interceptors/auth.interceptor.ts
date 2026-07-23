import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return next(req);
  }

  const isApiRequest =
    req.url.includes('/auth/me') ||
    req.url.includes('/vendors') ||
    req.url.includes('/contracts') ||
    req.url.includes('/analytics') ||
    req.url.includes('/procurement') ||
    req.url.includes('/profile');

  if (!isApiRequest) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });

  return next(authReq);
};