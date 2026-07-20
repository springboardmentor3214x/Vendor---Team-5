import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service'; // 1. Import your auth service!

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

  // 2. Updated to route directly to '/dashboard' since that's what you configured!
  private roleRouteMap: Record<UserRole, string> = {
    'Admin': '/dashboard',
    'Procurement Manager': '/procurement-management',
    'Vendor': '/vendor',
    'Auditor': '/auditor',
    'Supply Chain Manager': '/supply-chain-manager',
    'Finance Officer': '/finance-officer',
  };

  isRoleDropdownOpen = false;
  selectedRole: UserRole | null = null;
  isPasswordVisible = false;
  isSubmitting = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService // 3. Uncommented the auth service injection
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [true]
    });
  }

  get email() { return this.loginForm.get('email'); }
  get password() { return this.loginForm.get('password'); }

  toggleRoleDropdown(): void { this.isRoleDropdownOpen = !this.isRoleDropdownOpen; }
  selectRole(role: UserRole): void { this.selectedRole = role; this.isRoleDropdownOpen = false; }
  togglePasswordVisibility(): void { this.isPasswordVisible = !this.isPasswordVisible; }

  onSubmit(): void {
    this.errorMessage = null;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    if (!this.selectedRole) {
      this.errorMessage = 'Please select a role before logging in.';
      return;
    }

    this.isSubmitting = true;

    const payload = {
      email: this.email?.value,
      password: this.password?.value,
      role: this.selectedRole,
      rememberMe: this.loginForm.get('rememberMe')?.value
    };
   
    console.log('Selected Role:', this.selectedRole);
    console.log('Login payload:', payload);
    // 4. Actively use the service subscription so the Guard knows who you are!
    this.authService.login(payload).subscribe({
      next: (user) => {
        console.log('Login logic successful! Routing...', user);
        this.isSubmitting = false;
        const route = this.roleRouteMap[this.selectedRole!];
        this.router.navigate([route]);
      },
      error: (err) => {
        this.errorMessage = err?.message || 'Invalid email or password.';
        this.isSubmitting = false;
      }
    });
  }
}