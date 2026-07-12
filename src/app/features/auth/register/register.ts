import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

export type UserRole =
  | 'Administration'
  | 'Procurement Manager'
  | 'Vendor'
  | 'Auditor'
  | 'Supply Chain Manager'
  | 'Finance Officer';

function passwordsMatchValidator(): ValidatorFn {
  return (group: AbstractControl): ValidationErrors | null => {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    if (!password || !confirmPassword) {
      return null;
    }
    return password === confirmPassword ? null : { passwordMismatch: true };
  };
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class RegisterComponent {
  registerForm: FormGroup;

  roles: UserRole[] = [
    'Administration',
    'Procurement Manager',
    'Vendor',
    'Auditor',
    'Supply Chain Manager',
    'Finance Officer'
  ];

  isRoleDropdownOpen = false;
  selectedRole: UserRole | null = null;

  isPasswordVisible = false;
  isConfirmPasswordVisible = false;

  isSubmitting = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router
    // private authService: AuthService // wire up your real auth service here
  ) {
    this.registerForm = this.fb.group(
      {
        fullName: ['', [Validators.required, Validators.minLength(2)]],
        employeeId: ['', [Validators.required]],
        companyName: ['', [Validators.required]],
        email: ['', [Validators.required, Validators.email]],
        mobileNumber: ['', [Validators.required, Validators.pattern(/^[0-9+\-\s]{7,15}$/)]],
        password: ['', [Validators.required, Validators.minLength(6)]],
        confirmPassword: ['', [Validators.required]]
      },
      { validators: passwordsMatchValidator() }
    );
  }

  get fullName() {
    return this.registerForm.get('fullName');
  }
  get employeeId() {
    return this.registerForm.get('employeeId');
  }
  get companyName() {
    return this.registerForm.get('companyName');
  }
  get email() {
    return this.registerForm.get('email');
  }
  get mobileNumber() {
    return this.registerForm.get('mobileNumber');
  }
  get password() {
    return this.registerForm.get('password');
  }
  get confirmPassword() {
    return this.registerForm.get('confirmPassword');
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

  toggleConfirmPasswordVisibility(): void {
    this.isConfirmPasswordVisible = !this.isConfirmPasswordVisible;
  }

  onSubmit(): void {
    this.errorMessage = null;

    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    if (!this.selectedRole) {
      this.errorMessage = 'Please select a role before submitting.';
      return;
    }

    this.isSubmitting = true;

    const payload = {
      fullName: this.fullName?.value,
      employeeId: this.employeeId?.value,
      companyName: this.companyName?.value,
      email: this.email?.value,
      mobileNumber: this.mobileNumber?.value,
      password: this.password?.value,
      role: this.selectedRole
    };

    // Replace with your real auth call, e.g.:
    // this.authService.register(payload).subscribe({
    //   next: () => this.router.navigate(['/login']),
    //   error: (err) => {
    //     this.errorMessage = err?.error?.message || 'Registration failed. Please try again.';
    //     this.isSubmitting = false;
    //   }
    // });

    setTimeout(() => {
      console.log('Register payload:', payload);
      this.isSubmitting = false;
      this.router.navigate(['/login']);
    }, 800);
  }
}