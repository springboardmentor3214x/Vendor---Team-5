import { CommonModule, DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Certification, CertificationService } from '../../../core/services/certification.service';

@Component({
  selector: 'app-certification-management', standalone: true, imports: [CommonModule, FormsModule, DatePipe],
  template: `<section class="page-card"><h2>Certification Management</h2><p>Showing certifications for the seeded demo vendor. Change the vendor ID if needed.</p><input class="form-control" type="number" [(ngModel)]="vendorId" placeholder="Vendor ID"><button class="btn btn-primary" (click)="load()">Load</button><p *ngIf="error()" class="alert alert-danger">{{error()}}</p><table *ngIf="items().length"><tr><th>Name</th><th>Expiry</th><th>Status</th></tr><tr *ngFor="let c of items()"><td>{{c.certification_name}}</td><td>{{c.expiry_date|date:'mediumDate'}}</td><td>{{expired(c)?'Expired':'Active'}}</td></tr></table></section>`
})
export class CertificationManagementComponent {
  private readonly service = inject(CertificationService);
  vendorId = 1;
  readonly items = signal<Certification[]>([]);
  readonly error = signal('');
  ngOnInit(): void { this.load(); }
  load(): void { this.service.getVendorCertifications(this.vendorId).subscribe({ next: (items) => this.items.set(items), error: () => this.error.set('Unable to load certifications.') }); }
  expired(certification: Certification): boolean { return !!certification.expiry_date && new Date(certification.expiry_date) < new Date(); }
}
