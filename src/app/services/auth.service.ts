import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, of, throwError } from 'rxjs';
import { delay, tap } from 'rxjs/operators';

export interface LoginPayload {
  email: string;
  password: string;
  role: string;
  rememberMe?: boolean;
}

export interface RegisterPayload {
  fullName: string;
  employeeId?: string;
  companyName?: string;
  email: string;
  mobileNumber?: string;
  password: string;
  role: string;
}

export interface AuthUser {
  id?: number;
  fullName?: string;
  email: string;
  role: string;
}

const TOKEN_KEY = 'vendoriq_auth_token';
const USER_KEY = 'vendoriq_auth_user';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  currentUser = signal<AuthUser | null>(this.readStoredUser());

  constructor(private router: Router) {}

  login(payload: LoginPayload): Observable<any> {

    if (!payload.email || !payload.password) {
      return throwError(() => new Error('Email and Password are required.'));
    }

    const user: AuthUser = {
      email: payload.email,
      role: payload.role
    };

    return of(user).pipe(
      delay(500),
      tap(() => {
        localStorage.setItem(TOKEN_KEY, 'mock-token');
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        this.currentUser.set(user);
      })
    );
  }

  register(payload: RegisterPayload): Observable<any> {

    return of({
      success: true,
      message: 'Registration Successful',
      user: payload
    }).pipe(delay(500));
  }

  forgotPassword(email: string): Observable<any> {

    return of({
      success: true,
      message: 'Reset link sent.'
    }).pipe(delay(500));
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem(TOKEN_KEY);
  }

  getUserRole(): string {
    return this.currentUser()?.role || '';
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  getCurrentUser(): Observable<AuthUser | null> {
    return of(this.currentUser());
  }

  private readStoredUser(): AuthUser | null {

    const user = localStorage.getItem(USER_KEY);

    if (!user) {
      return null;
    }

    try {
      return JSON.parse(user);
    } catch {
      return null;
    }
  }
}