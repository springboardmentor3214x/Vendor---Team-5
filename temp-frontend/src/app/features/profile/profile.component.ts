import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, UserProfile } from '../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent {
  readonly profile = signal<UserProfile | null>(null);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly changingPassword = signal(false);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly passwordError = signal('');
  readonly passwordSuccess = signal('');
  readonly form: FormGroup;
  readonly passwordForm: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      fullName: ['', [Validators.required, Validators.minLength(2)]],
      companyName: [''],
      mobileNumber: [''],
      profilePicture: ['']
    });

    this.passwordForm = this.fb.nonNullable.group({
      currentPassword: ['', [Validators.required]],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(8)]]
    });

    if (!this.authService.isAuthenticated()) {
      this.router.navigateByUrl('/login');
      return;
    }

    this.authService.getProfile().subscribe({
      next: (user) => {
        this.profile.set(user);
        this.form.patchValue({
          fullName: user.fullName,
          companyName: user.companyName ?? '',
          mobileNumber: user.mobileNumber ?? '',
          profilePicture: user.profilePicture ?? ''
        });
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.router.navigateByUrl('/login');
      }
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Please fill all required profile fields.');
      this.successMessage.set('');
      return;
    }

    const payload = this.form.getRawValue();
    this.saving.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.authService
      .updateProfile({
        fullName: payload.fullName.trim(),
        companyName: payload.companyName?.trim() || null,
        mobileNumber: payload.mobileNumber?.trim() || null,
        profilePicture: payload.profilePicture?.trim() || null
      })
      .subscribe({
        next: (user) => {
          this.profile.set(user);
          this.saving.set(false);
          this.successMessage.set('Profile updated successfully.');
        },
        error: (err) => {
          this.saving.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to update profile.'));
        }
      });
  }

  changePassword(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      this.passwordError.set('Please fill all password fields correctly.');
      this.passwordSuccess.set('');
      return;
    }

    const { currentPassword, newPassword, confirmPassword } = this.passwordForm.getRawValue();
    if (newPassword !== confirmPassword) {
      this.passwordError.set('Password and confirm password must match.');
      this.passwordSuccess.set('');
      return;
    }

    this.changingPassword.set(true);
    this.passwordError.set('');
    this.passwordSuccess.set('');

    this.authService
      .changePassword({
        currentPassword,
        newPassword,
        confirmPassword
      })
      .subscribe({
        next: (res) => {
          this.changingPassword.set(false);
          this.passwordSuccess.set(res.message || 'Password changed successfully.');
          this.passwordForm.reset();
        },
        error: (err) => {
          this.changingPassword.set(false);
          this.passwordError.set(this.readError(err, 'Unable to change password.'));
        }
      });
  }

  control(name: string) {
    return this.form.get(name);
  }

  passwordControl(name: string) {
    return this.passwordForm.get(name);
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
