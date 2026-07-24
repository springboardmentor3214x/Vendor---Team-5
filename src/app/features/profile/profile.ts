import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css']
})
export class ProfileComponent {

  user = {
    name: 'Bharathi ',
    email: 'bharathiparimi@example.com',
    phone: '+91 9876543210',
    role: 'Administrator',
    joined: '15 Jan 2024'
  };

  saveChanges() {
    alert('Profile updated successfully!');
    console.log(this.user);
  }

  cancel() {
    this.user = {
      name: 'John Doe',
      email: 'johndoe@example.com',
      phone: '+91 9876543210',
      role: 'Administrator',
      joined: '15 Jan 2024'
    };

    alert('Changes cancelled.');
  }

  changePassword() {
    alert('Redirecting to Change Password...');
    // Example:
    // this.router.navigate(['/change-password']);
  }

  editProfile() {
    alert('Edit Profile clicked');
  }

}