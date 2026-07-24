import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['../register/register.component.css']
})
export class ForgotPasswordComponent {
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly resetToken = signal('');
  readonly isSubmitting = signal(false);
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Enter a valid email address.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    this.resetToken.set('');
    this.isSubmitting.set(true);

    this.authService.forgotPassword(this.form.getRawValue().email).subscribe({
      next: (res) => {
        this.isSubmitting.set(false);
        this.successMessage.set(res.message || 'Password reset request processed.');
        const token = res.reset_token ?? res.resetToken ?? '';
        if (token) {
          this.resetToken.set(token);
        }
      },
      error: (err) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(this.readError(err, 'Unable to process forgot password request.'));
      }
    });
  }

  goToReset(): void {
    const token = this.resetToken();
    this.router.navigate(['/reset-password'], {
      queryParams: token ? { token } : undefined
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
