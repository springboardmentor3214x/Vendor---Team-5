import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';

function passwordsMatchValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.get('newPassword')?.value;
  const confirmPassword = control.get('confirmPassword')?.value;
  return password === confirmPassword ? null : { passwordMismatch: true };
}

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.css'
})
export class ResetPasswordComponent {
  resetForm: FormGroup;

  showNewPassword = false;
  showConfirmPassword = false;

  isSubmitting = false;
  isSubmitted = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
    // private authService: AuthService // wire up your real auth service here
  ) {
    this.resetForm = this.fb.group(
      {
        newPassword: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', [Validators.required]]
      },
      { validators: passwordsMatchValidator }
    );
  }

  toggleNewPassword(): void {
    this.showNewPassword = !this.showNewPassword;
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  onSubmit(): void {
    if (this.resetForm.invalid) {
      this.resetForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;
    this.isSubmitted = false;

    const newPassword = this.resetForm.value.newPassword;
    const token = this.route.snapshot.queryParamMap.get('token');

    // Replace this with your real auth service call, e.g.:
    // this.authService.resetPassword(token, newPassword).subscribe({
    //   next: () => {
    //     this.isSubmitting = false;
    //     this.isSubmitted = true;
    //     setTimeout(() => this.router.navigate(['/login']), 1500);
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