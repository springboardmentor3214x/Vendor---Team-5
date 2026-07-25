import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  readonly errorMessage = signal('');
  readonly isSubmitting = signal(false);
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Enter a valid email and password.');
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set('');

    const payload = {
      email: this.form.getRawValue().email.trim().toLowerCase(),
      password: this.form.getRawValue().password
    };

    this.authService.login(payload).subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.router.navigateByUrl('/dashboard');
        },
        error: (err) => {
          this.isSubmitting.set(false);
          this.errorMessage.set(this.readError(err, 'Login failed. Please check email and password.'));
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
