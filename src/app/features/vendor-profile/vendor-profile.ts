
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-vendor-profile',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-profile.html',
  styleUrls: ['./vendor-profile.css']
})
export class VendorProfileComponent {

  constructor(private router: Router) {}

  company = {
    companyName: 'TechPro Solutions',
    vendorId: 'VND-2026-002',
    email: 'info@techprosolutions.com',
    phone: '+91 88867908765',
    website: 'www.techprosolutions.com',
    address: '123 Business Avenue, Suite 400, New York, NY 10001, USA'
  };

  contact = {
    fullName: 'Bharathi',
    designation: 'Operations Manager',
    email: 'bharathi12@gmail.com',
    phone: '8885367209'
  };

  editProfile(): void {
    alert('Edit Profile Clicked');
  }

  editContact(): void{
    alert('Edit Contact Clicked');
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}