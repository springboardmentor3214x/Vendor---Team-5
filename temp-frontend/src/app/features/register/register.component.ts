import { CommonModule } from '@angular/common';
import { Component, OnDestroy, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { ALLOWED_ROLES, AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnDestroy {
  readonly roles = ALLOWED_ROLES;
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly isSubmitting = signal(false);
  readonly form: FormGroup;

  private readonly roleSub: Subscription;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      fullName: ['', [Validators.required, Validators.minLength(2)]],
      employeeId: [''],
      companyName: [''],
      email: ['', [Validators.required, Validators.email]],
      mobileNumber: [''],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(8)]],
      role: ['Vendor', [Validators.required]]
    });

    this.applyRoleValidators(this.form.getRawValue().role);
    this.roleSub = this.form.get('role')!.valueChanges.subscribe((role) => {
      this.applyRoleValidators(role);
    });
  }

  ngOnDestroy(): void {
    this.roleSub.unsubscribe();
  }

  get isVendor(): boolean {
    return this.form.getRawValue().role === 'Vendor';
  }

  submit(): void {
    this.applyRoleValidators(this.form.getRawValue().role);

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

    this.authService
      .register({
        fullName: fullName.trim(),
        employeeId: employeeId?.trim() || null,
        companyName: companyName?.trim() || null,
        email: email.trim().toLowerCase(),
        mobileNumber: mobileNumber?.trim() || null,
        password,
        confirmPassword,
        role
      })
      .subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.successMessage.set('Registration successful. Redirecting to login...');
          setTimeout(() => this.router.navigateByUrl('/login'), 1000);
        },
        error: (err) => {
          this.isSubmitting.set(false);
          this.errorMessage.set(this.readError(err, 'Registration failed. Please verify all fields.'));
        }
      });
  }

  control(name: string) {
    return this.form.get(name);
  }

  private applyRoleValidators(role: string): void {
    const employeeId = this.form.get('employeeId');
    const companyName = this.form.get('companyName');

    if (role === 'Vendor') {
      employeeId?.clearValidators();
      companyName?.setValidators([Validators.required]);
    } else {
      companyName?.clearValidators();
      employeeId?.setValidators([Validators.required]);
    }

    employeeId?.updateValueAndValidity({ emitEvent: false });
    companyName?.updateValueAndValidity({ emitEvent: false });
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
