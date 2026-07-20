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
  employeeId: string;
  companyName: string;
  email: string;
  mobileNumber: string;
  password: string;
  role: string;
}

export interface AuthUser {
  email: string;
  role: string;
  name?: string;
}

const TOKEN_KEY = 'vendoriq_auth_token';
const USER_KEY = 'vendoriq_auth_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  // Reactive signal so components (like the header) can read the current user
  currentUser = signal<AuthUser | null>(this.readStoredUser());

  constructor(private router: Router) {}

  /**
   * Logs the user in. Right now this is a local mock (no real backend yet).
   * When your API is ready, replace the body of this method with:
   *
   * return this.http.post<{ token: string; user: AuthUser }>('/api/auth/login', payload).pipe(
   * tap(res => this.setSession(res.token, res.user))
   * );
   */
  login(payload: LoginPayload): Observable<AuthUser> {
    if (!payload.email || !payload.password) {
      return throwError(() => new Error('Email and password are required.'));
    }

    const fakeToken = `mock-token-${Date.now()}`;
    const user: AuthUser = { email: payload.email, role: payload.role };

    return of(user).pipe(
      delay(500),
      tap(() => this.setSession(fakeToken, user))
    );
  }

  /**
   * Registers a new user. Also a local mock for now — same swap-in note as login().
   */
  register(payload: RegisterPayload): Observable<AuthUser> {
    const fakeToken = `mock-token-${Date.now()}`;
    const user: AuthUser = { email: payload.email, role: payload.role, name: payload.fullName };

    return of(user).pipe(
      delay(500),
      tap(() => this.setSession(fakeToken, user))
    );
  }

  forgotPassword(email: string): Observable<{ success: true }> {
    return of({ success: true as const }).pipe(delay(500));
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  /**
   * Added to fix the role guard error.
   * Reads the current user signal and returns their role string, or an empty string if logged out.
   */
  getUserRole(): string {
    const user = this.currentUser();
    return user ? user.role : '';
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  private setSession(token: string, user: AuthUser): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    this.currentUser.set(user);
  }

  private readStoredUser(): AuthUser | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  }
}