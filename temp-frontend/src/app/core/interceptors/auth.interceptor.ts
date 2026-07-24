import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../../environments/environment';

const PUBLIC_AUTH_PATHS = [
  '/auth/register',
  '/auth/login',
  '/auth/forgot-password',
  '/auth/reset-password'
];

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return next(req);
  }

  const isApiRequest = req.url.startsWith(environment.apiUrl);
  if (!isApiRequest) {
    return next(req);
  }

  const isPublicAuth = PUBLIC_AUTH_PATHS.some((path) => req.url.includes(path));
  if (isPublicAuth) {
    return next(req);
  }

  return next(
    req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    })
  );
};
