import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { tap, delay } from 'rxjs/operators';
import { environment } from '../../environments/environment';

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

  constructor(
    private router: Router,
    private http: HttpClient) {}

  login(payload: LoginPayload): Observable<any> {

  return this.http.post<any>(
    `${environment.apiUrl}/auth/login`,
    {
      email: payload.email,
      password: payload.password
    }
  ).pipe(
    tap((response) => {

      localStorage.setItem(TOKEN_KEY, response.access_token);

      const user: AuthUser = {
        email: payload.email,
        role: payload.role,
      };

      localStorage.setItem(USER_KEY, JSON.stringify(user));
      this.currentUser.set(user);

    })
  );

}

   register(payload: RegisterPayload): Observable<any> {

  return this.http.post(
    `${environment.apiUrl}/auth/register`,
    {
      full_name: payload.fullName,
      email: payload.email,
      password: payload.password,
      role: payload.role
    }
  );

}
  

  forgotPassword(email: string): Observable<any> {

  return this.http.post(
    `${environment.apiUrl}/auth/reset-password`,
    {
      email: email
    }
  );

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