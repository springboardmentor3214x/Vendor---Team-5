import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface User {
  userId: string;
  name: string;
  email: string;
  role: string;
  department: string;
  status: string;
  statusClass: string;
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

  users: User[] = [
    {
      userId: 'USR-001',
      name: 'Bharathi',
      email: 'bharathi12@gmail.com',
      role: 'Administrator',
      department: 'IT Department',
      status: 'Active',
      statusClass: 'active-status',
      lastLogin: '10 Jul 2026',
      joinedOn: '10 May 2026'
    },
    {
      userId: 'USR-002',
      name: 'Sonali',
      email: 'sonali65@gmail.com',
      role: 'Procurement Manager',
      department: 'Procurement',
      status: 'Inactive',
      statusClass: 'inactive-status',
      lastLogin: '08 Jul 2026',
      joinedOn: '17 May 2026'
    },
    {
      userId: 'USR-003',
      name: 'Swathi',
      email: 'swathi123@gmail.com',
      role: 'Analyst',
      department: 'Analytics',
      status: 'Active',
      statusClass: 'active-status',
      lastLogin: '09 Jul 2026',
      joinedOn: '09 May 2026'
    },
    {
      userId: 'USR-004',
      name: 'Pranjelly',
      email: 'pranjelly20@gmail.com',
      role: 'Finance Manager',
      department: 'Finance',
      status: 'Active',
      statusClass: 'active-status',
      lastLogin: '10 Jul 2026',
      joinedOn: '04 May 2026'
    },
    {
      userId: 'USR-005',
      name: 'Priya',
      email: 'priya120@gmail.com',
      role: 'User',
      department: 'Procurement',
      status: 'Inactive',
      statusClass: 'inactive-status',
      lastLogin: '09 Jul 2026',
      joinedOn: '06 May 2026'
    }
  ];

  viewUser(user: User): void {
    console.log('View User', user);
  }

  editUser(user: User): void {
    console.log('Edit User', user);
  }

  deleteUser(user: User): void {
    if (confirm(`Delete ${user.name}?`)) {
      this.users = this.users.filter(u => u.userId !== user.userId);
    }
  }

}