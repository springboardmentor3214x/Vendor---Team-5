import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
@Component({
  selector: 'app-vendor-reliability',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-reliability.html',
  styleUrls: ['./vendor-reliability.css']
})
export class VendorReliabilityComponent implements OnInit {

  totalVendors = 128;
  averagePerformance = 86;
  topPerformer = 'TechPro Solutions';
  underPerforming = 8;

  vendors = [
    {
      vendorName: 'TechPro Solutions',
      onTimeDelivery: '96%',
      qualityScore: '94%',
      orderAccuracy: '95%',
      reliabilityScore: '95%',
      status: 'Excellent'
    },
    {
      vendorName: 'Global Supplies',
      onTimeDelivery: '92%',
      qualityScore: '91%',
      orderAccuracy: '90%',
      reliabilityScore: '91%',
      status: 'Excellent'
    },
    {
      vendorName: 'Prime Components',
      onTimeDelivery: '90%',
      qualityScore: '89%',
      orderAccuracy: '92%',
      reliabilityScore: '90%',
      status: 'Good'
    },
    {
      vendorName: 'Reliable Industries',
      onTimeDelivery: '88%',
      qualityScore: '87%',
      orderAccuracy: '86%',
      reliabilityScore: '87%',
      status: 'Good'
    },
    {
      vendorName: 'Advanced Systems',
      onTimeDelivery: '85%',
      qualityScore: '83%',
      orderAccuracy: '85%',
      reliabilityScore: '84%',
      status: 'Average'
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }

}