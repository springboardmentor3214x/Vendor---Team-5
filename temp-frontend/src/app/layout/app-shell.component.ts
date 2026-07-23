import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.css'
})
export class AppShellComponent {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  readonly navItems = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Vendors', path: '/vendors' },
    { label: 'Procurement', path: '/procurement' },
    { label: 'Contracts', path: '/contracts' },
    { label: 'Analytics', path: '/analytics' },
    { label: 'Profile', path: '/profile' }
  ];

  logout(): void {
    this.authService.logout();
    this.router.navigateByUrl('/login');
  }
}
