import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPasswordComponent {
  forgotForm: FormGroup;

  isSubmitting = false;
  isSubmitted = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder
    // private authService: AuthService // wire up your real auth service here
  ) {
    this.forgotForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  onSubmit(): void {
    if (this.forgotForm.invalid) {
      this.forgotForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;
    this.isSubmitted = false;

    const email = this.forgotForm.value.email;

    // Replace this with your real auth service call, e.g.:
    // this.authService.sendResetLink(email).subscribe({
    //   next: () => {
    //     this.isSubmitting = false;
    //     this.isSubmitted = true;
    //   },
    //   error: (err) => {
    //     this.isSubmitting = false;
    //     this.errorMessage = err?.error?.message || 'Something went wrong. Please try again.';
    //   }
    // });

    // Temporary mock behavior so the UI works before the service is wired up:
    setTimeout(() => {
      this.isSubmitting = false;
      this.isSubmitted = true;
    }, 1000);
  }
}