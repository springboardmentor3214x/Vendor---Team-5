import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-performance-history',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './performance-history.html',
  styleUrls: ['./performance-history.css']
})
export class PerformanceHistoryComponent implements AfterViewInit {

  searchText: string = '';

  vendor = {
    name: 'Vendor A Pvt Ltd',
    id: 'VEN-001',
    category: 'Raw Material Supplier',
    status: 'Active',
    score: '92%',
    rank: '2 / 58',
    orders: 128
  };

  purchaseHistory = [
    {
      po: 'PO-2026-1001',
      date: '10-Jul-2026',
      item: 'Steel Rods',
      amount: '₹2,50,000',
      status: 'Completed',
      completed: '15-Jul-2026'
    },
    {
      po: 'PO-2026-1002',
      date: '15-Jul-2026',
      item: 'Copper Wires',
      amount: '₹1,75,000',
      status: 'Completed',
      completed: '20-Jul-2026'
    },
    {
      po: 'PO-2026-1003',
      date: '18-Jul-2026',
      item: 'Industrial Valves',
      amount: '₹3,20,000',
      status: 'Completed',
      completed: '25-Jul-2026'
    }
  ];

  deliveryRecords = [
    {
      po: 'PO-2026-1001',
      expected: '15-Jul-2026',
      actual: '15-Jul-2026',
      status: 'On Time'
    },
    {
      po: 'PO-2026-1002',
      expected: '20-Jul-2026',
      actual: '22-Jul-2026',
      status: 'Delayed'
    }
  ];

  qualityRecords = [
    {
      po: 'PO-2026-1001',
      date: '15-Jul-2026',
      rating: '4.8 / 5'
    },
    {
      po: 'PO-2026-1002',
      date: '22-Jul-2026',
      rating: '4.5 / 5'
    }
  ];

  communicationRecords = [
    {
      po: 'PO-2026-1001',
      time: '35 mins',
      status: 'Good'
    },
    {
      po: 'PO-2026-1002',
      time: '1 hr',
      status: 'Average'
    }
  ];

  serviceRatings = [
    {
      po: 'PO-2026-1001',
      rating: '5 / 5',
      date: '15-Jul-2026'
    },
    {
      po: 'PO-2026-1002',
      rating: '4 / 5',
      date: '22-Jul-2026'
    }
  ];

  complaints = [
    {
      id: 'CMP-001',
      raised: '12-Jul-2026',
      status: 'Resolved'
    }
  ];

  issuesRaised = [
    {
      id: 'ISS-001',
      raised: '13-Jul-2026',
      status: 'Resolved'
    }
  ];

  issuesResolved = [
    {
      id: 'ISS-001',
      resolved: '14-Jul-2026',
      time: '1 Day'
    }
  ];

  procurementHistory = [
    {
      period: 'Jan',
      orders: 20,
      spend: '₹5,00,000'
    },
    {
      period: 'Feb',
      orders: 25,
      spend: '₹6,20,000'
    },
    {
      period: 'Mar',
      orders: 30,
      spend: '₹7,80,000'
    },
    {
      period: 'Apr',
      orders: 28,
      spend: '₹7,10,000'
    },
    {
      period: 'May',
      orders: 35,
      spend: '₹8,60,000'
    },
    {
      period: 'Jun',
      orders: 38,
      spend: '₹9,50,000'
    }
  ];

  ngAfterViewInit(): void {

    const canvas = document.getElementById('performanceChart') as HTMLCanvasElement;

    if (!canvas) {
      return;
    }

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: ['Jan','Feb','Mar','Apr','May','Jun'],
        datasets: [
          {
            label: 'Performance Score',
            data: [72, 80, 78, 85, 91, 92],
            fill: false,
            borderWidth: 3,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

  }

}