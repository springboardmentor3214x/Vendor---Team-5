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
  readonly saving = signal(false);
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      fullName: ['', [Validators.required]],
      companyName: [''],
      mobileNumber: [''],
      profilePicture: ['']
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
      },
      error: () => {
        this.router.navigateByUrl('/login');
      }
    });
  }

  save(): void {
    const payload = this.form.getRawValue();
    this.saving.set(true);

    this.authService.updateProfile(payload).subscribe({
      next: (user) => {
        this.profile.set(user);
        this.authService.saveSession(this.authService.getToken() ?? '', user);
        this.saving.set(false);
      },
      error: () => this.saving.set(false)
    });
  }
}