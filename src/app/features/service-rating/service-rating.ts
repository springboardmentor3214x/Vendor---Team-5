import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-service-rating',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './service-rating.html',
  styleUrls: ['./service-rating.css']
})
export class ServiceRatingComponent {

  searchText: string = '';

  purchaseOrder: string = 'PO-2026-0123';
  vendorName: string = 'Vendor A Pvt Ltd';
  serviceDate: string = '';

  professionalism: string = '4 - Good';
  customerSupport: string = '4 - Good';
  documentationQuality: string = '4 - Good';
  flexibility: string = '4 - Good';
  communicationEffectiveness: string = '4 - Good';
  issueResolution: string = '4 - Good';
  overallRating: string = '5 - Excellent';

  comments: string =
    'Overall service was good. Vendor responded promptly and resolved issues effectively.';

  purchaseOrders = [
    'PO-2026-0123',
    'PO-2026-0124',
    'PO-2026-0125'
  ];

  vendors = [
    'Vendor A Pvt Ltd',
    'Vendor B Solutions',
    'Vendor C Supplies'
  ];

  ratings = [
    '5 - Excellent',
    '4 - Good',
    '3 - Average',
    '2 - Poor',
    '1 - Very Poor'
  ];

  resetForm(): void {

    this.searchText = '';
    this.purchaseOrder = '';
    this.vendorName = '';
    this.serviceDate = '';

    this.professionalism = '';
    this.customerSupport = '';
    this.documentationQuality = '';
    this.flexibility = '';
    this.communicationEffectiveness = '';
    this.issueResolution = '';
    this.overallRating = '';

    this.comments = '';

  }

  saveRating(): void {

    alert('Service Rating Saved Successfully!');

    console.log({
      purchaseOrder: this.purchaseOrder,
      vendorName: this.vendorName,
      serviceDate: this.serviceDate,
      professionalism: this.professionalism,
      customerSupport: this.customerSupport,
      documentationQuality: this.documentationQuality,
      flexibility: this.flexibility,
      communicationEffectiveness: this.communicationEffectiveness,
      issueResolution: this.issueResolution,
      overallRating: this.overallRating,
      comments: this.comments
    });

  }

}