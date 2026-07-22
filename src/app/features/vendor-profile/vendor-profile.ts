import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-vendor-profile',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-profile.html',
  styleUrls: ['./vendor-profile.css']
})
export class VendorProfileComponent implements OnInit {

  vendorId = 1; // Temporary ID. Replace with route parameter during integration.

  constructor(
    private router: Router,
    private vendorService: VendorService
  ) {}

  company: any = {};

  contact: any = {};

  ngOnInit(): void {
    this.loadVendorProfile();
  }

  loadVendorProfile(): void {
    this.vendorService.getVendor(this.vendorId).subscribe({
      next: (data: any) => {

        this.company = {
          companyName: data.companyName,
          vendorId: data.vendorId,
          email: data.email,
          phone: data.phone,
          website: data.website,
          address: data.address
        };

        this.contact = {
          fullName: data.contactName,
          designation: data.designation,
          email: data.contactEmail,
          phone: data.contactPhone
        };

      },
      error: (err) => {
        console.error('Error loading vendor profile', err);
      }
    });
  }

  editProfile(): void {
    alert('Edit Profile Clicked');
  }

  editContact(): void {
    alert('Edit Contact Clicked');
  }

  logout(): void {
    this.router.navigate(['/login']);
  }

}