import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contracts.component.html',
  styleUrl: './contracts.component.css'
})
export class ContractsComponent {
  readonly contracts = [
    { name: 'Global Supply Partnership', expires: '12 days' },
    { name: 'Acme Manufacturing Agreement', expires: '29 days' },
    { name: 'Nexus Packaging Renewal', expires: '45 days' }
  ];
}
