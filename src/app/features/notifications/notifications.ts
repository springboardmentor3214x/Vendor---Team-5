import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrls: ['./notifications.css']
})
export class Notifications implements OnInit {

  notifications: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {

    this.http.get<any[]>(
      `${environment.apiUrl}/notifications`
    ).subscribe({

      next: (data) => {
        this.notifications = data;
      },

      error: (err) => {

        console.error('Failed to load notifications', err);

        this.notifications = [
          {
            title: 'New User Registered',
            message: 'John Doe has successfully created an account.',
            category: 'User Activity',
            date: '2 min ago',
            icon: '👤',
            read: false
          },
          {
            title: 'Server Maintenance',
            message: 'Scheduled maintenance will begin tonight at 11:00 PM.',
            category: 'System',
            date: '1 hour ago',
            icon: '🛠️',
            read: false
          },
          {
            title: 'Payment Received',
            message: 'Payment of ₹12,500 has been received successfully.',
            category: 'Finance',
            date: 'Today',
            icon: '💳',
            read: false
          },
          {
            title: 'Password Changed',
            message: 'Your account password was updated successfully.',
            category: 'Security',
            date: 'Yesterday',
            icon: '🔒',
            read: true
          },
          {
            title: 'Application Approved',
            message: 'Your leave request has been approved.',
            category: 'HR',
            date: 'Yesterday',
            icon: '✅',
            read: true
          },
          {
            title: 'New Message',
            message: 'You have received a new message from Admin.',
            category: 'Messages',
            date: '2 days ago',
            icon: '💬',
            read: false
          }
        ];

      }

    });

  }

  markAllRead(): void {
    this.notifications.forEach(notification => notification.read = true);
  }

  get unreadCount(): number {
    return this.notifications.filter(notification => !notification.read).length;
  }

  get totalCount(): number {
    return this.notifications.length;
  }

  get priorityCount(): number {
    return 3;
  }

  get updateCount(): number {
    return 5;
  }

}