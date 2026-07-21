import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

export type UserRole =
  | 'Admin'
  | 'Procurement Manager'
  | 'Vendor'
  | 'Auditor'
  | 'Supply Chain Manager'
  | 'Finance Officer';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent {

  loginForm: FormGroup;

  roles: UserRole[] = [
    'Admin',
    'Procurement Manager',
    'Vendor',
    'Auditor',
    'Supply Chain Manager',
    'Finance Officer'
  ];

  private roleRouteMap: Record<UserRole, string> = {
    'Admin': '/dashboard',
    'Procurement Manager': '/procurement-management',
    'Vendor': '/vendor',
    'Auditor': '/auditor',
    'Supply Chain Manager': '/supply-chain-manager',
    'Finance Officer': '/finance-officer'
  };

  isRoleDropdownOpen = false;
  selectedRole: UserRole | null = null;
  isPasswordVisible = false;
  isSubmitting = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {

    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [true]
    });

  }

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  toggleRoleDropdown(): void {
    this.isRoleDropdownOpen = !this.isRoleDropdownOpen;
  }

  selectRole(role: UserRole): void {
    this.selectedRole = role;
    this.isRoleDropdownOpen = false;
  }

  togglePasswordVisibility(): void {
    this.isPasswordVisible = !this.isPasswordVisible;
  }

  onSubmit(): void {

    this.errorMessage = null;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    if (!this.selectedRole) {
      this.errorMessage = 'Please select a role.';
      return;
    }

    this.isSubmitting = true;

    const payload = {
      email: this.email?.value,
      password: this.password?.value,
      role: this.selectedRole,
      rememberMe: this.loginForm.get('rememberMe')?.value
    };

    this.authService.login(payload).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.router.navigate([this.roleRouteMap[this.selectedRole!] || '/dashboard']);
      },
      error: (err) => {
        this.isSubmitting = false;
        this.errorMessage = err?.message || 'Login failed.';
      }
    });

  }
}