import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';

interface User {
  userId: string;
  name: string;
  email: string;
  role: string;
  roleClass: string;
  department: string;
  status: 'Active' | 'In Active';
  lastLogin: string;
  joinedOn: string;
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagementComponent {

  constructor(private router: Router) {}

  users: User[] = [
    {
      userId: 'USR-001',
      name: 'Bharathi',
      email: 'bharathi12@gmail.com',
      role: 'Administrator',
      roleClass: 'admin',
      department: 'IT Depart',
      status: 'Active',
      lastLogin: '10 July 2026',
      joinedOn: '10 May 2026'
    },
    {
      userId: 'USR-002',
      name: 'Sonali',
      email: 'sonali65@gmail.com',
      role: 'Procurement Manager',
      roleClass: 'procurement',
      department: 'Procurement',
      status: 'In Active',
      lastLogin: '08 July 2026',
      joinedOn: '17 May 2026'
    },
    {
      userId: 'USR-003',
      name: 'Swathi',
      email: 'swathi123@gmail.com',
      role: 'Analyst',
      roleClass: 'analyst',
      department: 'Analytics',
      status: 'Active',
      lastLogin: '09 July 2026',
      joinedOn: '09 May 2026'
    },
    {
      userId: 'USR-004',
      name: 'Pranjelly',
      email: 'pranjelly20@gmail.com',
      role: 'Finace Manager',
      roleClass: 'finance',
      department: 'Finance',
      status: 'Active',
      lastLogin: '10 July 2026',
      joinedOn: '04 May 2026'
    },
    {
      userId: 'USR-005',
      name: 'Priya',
      email: 'priya120@gmail.com',
      role: 'User',
      roleClass: 'user',
      department: 'Procurement',
      status: 'In Active',
      lastLogin: '09 July 2026',
      joinedOn: '06 May 2026'
    }
  ];

  currentPage = 1;
  totalPages = 20;

  get totalPagesArray(): number[] {
    return [1, 2, 3];
  }

  prevPage(): void {
    if (this.currentPage > 1) this.currentPage--;
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) this.currentPage++;
  }

  goToPage(page: number): void {
    this.currentPage = page;
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}