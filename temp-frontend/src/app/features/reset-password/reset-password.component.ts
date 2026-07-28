import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './reset-password.component.html',
  styleUrls: ['../register/register.component.css']
})
export class ResetPasswordComponent {
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly isSubmitting = signal(false);
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      token: ['', [Validators.required]],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(8)]]
    });

    const token = this.route.snapshot.queryParamMap.get('token');
    if (token) {
      this.form.patchValue({ token });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Please fill all required fields correctly.');
      return;
    }

    const { token, newPassword, confirmPassword } = this.form.getRawValue();
    if (newPassword !== confirmPassword) {
      this.errorMessage.set('Password and confirm password must match.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    this.isSubmitting.set(true);

    this.authService
      .resetPassword({
        token: token.trim(),
        newPassword,
        confirmPassword
      })
      .subscribe({
        next: (res) => {
          this.isSubmitting.set(false);
          this.successMessage.set(res.message || 'Password updated successfully.');
          setTimeout(() => this.router.navigateByUrl('/login'), 1200);
        },
        error: (err) => {
          this.isSubmitting.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to reset password.'));
        }
      });
  }

  control(name: string) {
    return this.form.get(name);
  }

  private readError(err: unknown, fallback: string): string {
    const detail = (err as { error?: { detail?: unknown } })?.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item: { msg?: string }) => item?.msg).filter(Boolean).join(', ');
    }
    return fallback;
  }
}
