import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);

  // Replace this with your actual authentication check logic 
  // (e.g., checking localStorage or an AuthService)
  const isAuthenticated = true; 

  if (isAuthenticated) {
    return true;
  } else {
    // Redirect unauthenticated users back to login page
    router.navigate(['/login']);
    return false;
  }
};