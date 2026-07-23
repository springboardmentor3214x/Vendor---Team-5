import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  employeeId: string;
  companyName: string;
  email: string;
  mobileNumber: string;
  password: string;
  confirmPassword: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  redirect_to?: string;
}

interface CurrentUserResponse {
  id?: number;
  email: string;
  full_name: string;
  role: string;
  company_name?: string | null;
  employee_id?: string | null;
  mobile_number?: string | null;
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
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  register(payload: RegisterRequest): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/auth/register`, payload);
  }

  login(payload: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login`, {
      email: payload.email.trim().toLowerCase(),
      password: payload.password
    }).pipe(
      tap((response) => {
        this.persistToken(response.access_token);
      })
    );
  }

  me(): Observable<CurrentUserResponse> {
    return this.http.get<CurrentUserResponse>(`${this.apiUrl}/auth/me`);
  }

  getProfile(): Observable<UserProfile> {
    return this.me().pipe(map((user) => this.mapUser(user)));
  }

  updateProfile(payload: {
    fullName: string;
    companyName?: string;
    mobileNumber?: string;
    profilePicture?: string;
  }): Observable<UserProfile> {
    const current = this.getStoredUser();

    const updated: UserProfile = {
      id: current?.id,
      email: current?.email ?? '',
      role: current?.role ?? 'Vendor',
      fullName: payload.fullName,
      companyName: payload.companyName ?? '',
      mobileNumber: payload.mobileNumber ?? '',
      employeeId: current?.employeeId ?? '',
      profilePicture: payload.profilePicture ?? ''
    };

    this.saveSession(this.getToken() ?? '', updated);
    return of(updated);
  }

  persistToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  saveSession(token: string, user: UserProfile): void {
    if (token) localStorage.setItem('access_token', token);
    localStorage.setItem('user_profile', JSON.stringify(user));
  }

  getStoredUser(): UserProfile | null {
    const raw = localStorage.getItem('user_profile');
    if (!raw) return null;

    try {
      return JSON.parse(raw) as UserProfile;
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_profile');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isLoggedIn(): boolean {
    return this.isAuthenticated();
  }

  private mapUser(user: CurrentUserResponse): UserProfile {
    return {
      id: user.id,
      email: user.email,
      fullName: user.full_name,
      role: user.role,
      companyName: user.company_name ?? '',
      employeeId: user.employee_id ?? '',
      mobileNumber: user.mobile_number ?? '',
      profilePicture: ''
    };
  }
}