import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analytics.component.html',
  styleUrl: './analytics.component.css'
})
export class AnalyticsComponent {
  readonly metrics = [
    { title: 'Avg. Vendor Reliability', value: '92%' },
    { title: 'Delivery Success', value: '97%' },
    { title: 'Open Quality Alerts', value: '4' }
  ];
}
