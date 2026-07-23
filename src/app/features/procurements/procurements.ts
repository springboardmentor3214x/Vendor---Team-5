import { AfterViewInit, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { Router, RouterLink } from '@angular/router';
Chart.register(...registerables);

@Component({
  selector: 'app-procurements',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './procurements.html',
  styleUrls: ['./procurements.css']
})
export class ProcurementsComponent implements AfterViewInit {

  activities = [

    {
      icon: 'ti ti-file-plus',
      title: 'PR-2026-00125 Created',
      description: 'New procurement request created',
      status: 'Today'
    },

    {
      icon: 'ti ti-check',
      title: 'PR-2026-00124 Approved',
      description: 'Approved by Procurement Manager',
      status: '1 Hour Ago'
    },

    {
      icon: 'ti ti-users',
      title: 'Vendor Assigned',
      description: 'ABC Enterprises Assigned',
      status: 'Yesterday'
    },

    {
      icon: 'ti ti-shopping-cart',
      title: 'Purchase Order Created',
      description: 'PO-2026-008 Generated',
      status: 'Yesterday'
    },

    {
      icon: 'ti ti-truck-delivery',
      title: 'Order Delivered',
      description: 'Items Delivered Successfully',
      status: '2 Days Ago'
    },

    {
      icon: 'ti ti-file-invoice',
      title: 'Invoice Received',
      description: 'Invoice Uploaded by Vendor',
      status: '3 Days Ago'
    }

  ];

  ngAfterViewInit(): void {
    this.createChart();
  }

  createChart(): void {

    new Chart('procurementChart', {

      type: 'bar',

      data: {

        labels: [
          'Requests',
          'Pending',
          'Approved',
          'PO',
          'Delivered',
          'Completed',
          'Cancelled'
        ],

        datasets: [

          {
            label: 'Procurement Status',

            data: [
              125,
              18,
              60,
              42,
              30,
              28,
              5
            ],

            backgroundColor: [
              '#3B82F6',
              '#F97316',
              '#22C55E',
              '#8B5CF6',
              '#06B6D4',
              '#10B981',
              '#EF4444'
            ],

            borderRadius: 8

          }

        ]

      },

      options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

          legend: {
            display: false
          }

        },

        scales: {

          y: {
            beginAtZero: true
          }

        }

      }

    });

  }

}