import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly isSubmitting = signal(false);
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      fullName: ['', [Validators.required]],
      employeeId: ['', [Validators.required]],
      companyName: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      mobileNumber: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(8)]],
      role: ['Administrator', [Validators.required]]
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Please fill all required fields correctly.');
      return;
    }

    const {
      fullName,
      employeeId,
      companyName,
      email,
      mobileNumber,
      password,
      confirmPassword,
      role
    } = this.form.getRawValue();

    if (password !== confirmPassword) {
      this.errorMessage.set('Password and confirm password must match.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    this.isSubmitting.set(true);

    const payload = {
      fullName: fullName.trim(),
      employeeId: employeeId.trim(),
      companyName: companyName.trim(),
      email: email.trim().toLowerCase(),
      mobileNumber: mobileNumber.trim(),
      password,
      confirmPassword,
      role
    };

    this.authService.register(payload).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.successMessage.set('Registration successful. Redirecting to login...');
        setTimeout(() => {
          this.router.navigateByUrl('/login');
        }, 1000);
      },
      error: (err) => {
        this.isSubmitting.set(false);

        const detail = err?.error?.detail;
        if (typeof detail === 'string') {
          this.errorMessage.set(detail);
        } else if (Array.isArray(detail)) {
          this.errorMessage.set(detail.map((item: any) => item?.msg).filter(Boolean).join(', '));
        } else {
          this.errorMessage.set('Registration failed. Please verify all fields.');
        }
      }
    });
  }

  control(name: string) {
    return this.form.get(name);
  }
}