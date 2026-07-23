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
        this.authService.getProfile().subscribe({
          next: (user) => {
            this.authService.saveSession(this.authService.getToken() ?? '', user);
            this.router.navigateByUrl('/dashboard');
          },
          error: () => {
            this.errorMessage.set('Login succeeded but profile loading failed.');
            this.isSubmitting.set(false);
          }
        });
      },
      error: (err) => {
        const detail = err?.error?.detail;

        if (typeof detail === 'string') {
          this.errorMessage.set(detail);
        } else if (Array.isArray(detail)) {
          this.errorMessage.set(detail.map((item: any) => item?.msg).filter(Boolean).join(', '));
        } else {
          this.errorMessage.set('Login failed. Please check email and password.');
        }

        this.isSubmitting.set(false);
      }
    });
  }

  control(name: string) {
    return this.form.get(name);
  }
}