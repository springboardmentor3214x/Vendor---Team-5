import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService, UserProfile } from '../core/services/auth.service';

interface NavItem {
  label: string;
  path: string;
  exact: boolean;
  roles: string[];
}

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

  readonly currentUser: UserProfile | null = this.authService.getStoredUser();

  private readonly navItems: NavItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      exact: true,
      roles: [
        'Administrator',
        'Procurement Manager',
        'Supply Chain Manager',
        'Vendor',
        'Finance Officer',
        'Auditor'
      ]
    },
    {
      label: 'Vendors',
      path: '/vendors',
      exact: false,
      roles: ['Administrator', 'Procurement Manager', 'Supply Chain Manager']
    },
    {
      label: 'Profile',
      path: '/profile',
      exact: true,
      roles: [
        'Administrator',
        'Procurement Manager',
        'Supply Chain Manager',
        'Vendor',
        'Finance Officer',
        'Auditor'
      ]
    }
  ];

  get visibleNavItems(): NavItem[] {
    const role = this.currentUser?.role;
    if (!role) {
      return [];
    }
    return this.navItems.filter((item) => item.roles.includes(role));
  }

  logout(): void {
    this.authService.logout();
    this.router.navigateByUrl('/login');
  }
}