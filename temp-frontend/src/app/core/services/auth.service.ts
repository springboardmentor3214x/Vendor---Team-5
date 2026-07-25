import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of, switchMap, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export const ALLOWED_ROLES = [
  'Administrator',
  'Procurement Manager',
  'Supply Chain Manager',
  'Vendor',
  'Finance Officer',
  'Auditor'
] as const;

export type AppRole = (typeof ALLOWED_ROLES)[number];

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  employeeId?: string | null;
  companyName?: string | null;
  email: string;
  mobileNumber?: string | null;
  password: string;
  confirmPassword: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role?: string;
  redirect_to?: string;
  redirectTo?: string;
}

export interface MessageResponse {
  message: string;
  reset_token?: string;
  resetToken?: string;
}

export interface UpdateProfileRequest {
  fullName?: string;
  companyName?: string | null;
  mobileNumber?: string | null;
  profilePicture?: string | null;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

interface CurrentUserResponse {
  id?: number;
  email: string;
  full_name?: string;
  fullName?: string;
  role: string;
  company_name?: string | null;
  companyName?: string | null;
  employee_id?: string | null;
  employeeId?: string | null;
  mobile_number?: string | null;
  mobileNumber?: string | null;
  profile_picture?: string | null;
  profilePicture?: string | null;
  is_active?: boolean;
  isActive?: boolean;
}

export interface UserProfile {
  id?: number;
  email: string;
  fullName: string;
  role: string;
  companyName?: string | null;
  employeeId?: string | null;
  mobileNumber?: string | null;
  profilePicture?: string | null;
  isActive?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/auth`;

  register(payload: RegisterRequest): Observable<UserProfile> {
    return this.http
      .post<CurrentUserResponse>(`${this.apiUrl}/register`, payload)
      .pipe(map((user) => this.mapUser(user)));
  }

  login(payload: LoginRequest): Observable<UserProfile> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/login`, {
        email: payload.email.trim().toLowerCase(),
        password: payload.password
      })
      .pipe(
        tap((response) => {
          this.persistToken(response.access_token);
        }),
        switchMap(() => this.getProfile())
      );
  }

  me(): Observable<CurrentUserResponse> {
    return this.http.get<CurrentUserResponse>(`${this.apiUrl}/me`);
  }

  getProfile(): Observable<UserProfile> {
    return this.me().pipe(
      map((user) => {
        const profile = this.mapUser(user);
        this.saveSession(this.getToken() ?? '', profile);
        return profile;
      })
    );
  }

  ensureProfile(): Observable<UserProfile | null> {
    const storedUser = this.getStoredUser();
    if (storedUser) {
      return of(storedUser);
    }

    return this.getProfile().pipe(
      catchError(() => {
        this.logout();
        return of(null);
      })
    );
  }

  updateProfile(payload: UpdateProfileRequest): Observable<UserProfile> {
    return this.http.put<CurrentUserResponse>(`${this.apiUrl}/profile`, payload).pipe(
      map((user) => {
        const profile = this.mapUser(user);
        this.saveSession(this.getToken() ?? '', profile);
        return profile;
      })
    );
  }

  forgotPassword(email: string): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.apiUrl}/forgot-password`, {
      email: email.trim().toLowerCase()
    });
  }

  resetPassword(payload: ResetPasswordRequest): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.apiUrl}/reset-password`, payload);
  }

  changePassword(payload: ChangePasswordRequest): Observable<MessageResponse> {
    return this.http.post<MessageResponse>(`${this.apiUrl}/change-password`, payload);
  }

  persistToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  saveSession(token: string, user: UserProfile): void {
    if (token) {
      localStorage.setItem('access_token', token);
    }
    localStorage.setItem('user_profile', JSON.stringify(user));
  }

  getStoredUser(): UserProfile | null {
    const raw = localStorage.getItem('user_profile');
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as UserProfile;
    } catch {
      localStorage.removeItem('user_profile');
      return null;
    }
  }

  getUserRole(): string | null {
    return this.getStoredUser()?.role ?? null;
  }

  hasRole(...roles: string[]): boolean {
    const role = this.getUserRole();
    return !!role && roles.includes(role);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isLoggedIn(): boolean {
    return this.isAuthenticated();
  }

  getToken(): string | null {
    const token = localStorage.getItem('access_token');
    if (!token || this.isTokenExpired(token)) {
      if (token) {
        this.logout();
      }
      return null;
    }
    return token;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_profile');
  }

  private mapUser(user: CurrentUserResponse): UserProfile {
    return {
      id: user.id,
      email: user.email,
      fullName: user.full_name ?? user.fullName ?? '',
      role: user.role,
      companyName: user.company_name ?? user.companyName ?? '',
      employeeId: user.employee_id ?? user.employeeId ?? '',
      mobileNumber: user.mobile_number ?? user.mobileNumber ?? '',
      profilePicture: user.profile_picture ?? user.profilePicture ?? '',
      isActive: user.is_active ?? user.isActive ?? true
    };
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = token.split('.')[1];
      if (!payload) {
        return true;
      }

      const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/');
      const paddedPayload = normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, '=');
      const claims = JSON.parse(atob(paddedPayload)) as { exp?: unknown };

      return typeof claims.exp !== 'number' || claims.exp * 1000 <= Date.now();
    } catch {
      return true;
    }
  }
}
