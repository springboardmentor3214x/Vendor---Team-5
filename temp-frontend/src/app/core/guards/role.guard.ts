import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';
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

  return authService.ensureProfile().pipe(
    map((profile) => {
      if (profile && allowedRoles.includes(profile.role)) {
        return true;
      }
      return router.createUrlTree(['/profile']);
    })
  );
};
