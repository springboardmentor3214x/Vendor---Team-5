import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-procurement',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './procurement.component.html',
  styleUrl: './procurement.component.css'
})
export class ProcurementComponent {
  readonly activity = [
    { label: 'Purchase order requests', value: '17' },
    { label: 'Approved this week', value: '9' },
    { label: 'Pending delivery', value: '5' }
  ];
}
