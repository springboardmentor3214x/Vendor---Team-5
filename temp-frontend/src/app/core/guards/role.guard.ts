import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  const allowedRoles = route.data['roles'] as string[] | undefined;
  if (!allowedRoles?.length) {
    return true;
  }

  const role = authService.getUserRole();
  if (role && allowedRoles.includes(role)) {
    return true;
  }

  return router.createUrlTree(['/profile']);
};