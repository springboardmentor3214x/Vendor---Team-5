import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Contract, ContractService } from '../../../core/services/contract.service';
import { DirectMessageService } from '../../../core/services/direct-message.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-contract-details',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, DatePipe, CurrencyPipe],
  template: `
    <section class="page-card">
      <a routerLink="/contracts">Back to contracts</a>
      <div *ngIf="loading()" class="alert alert-info">Loading...</div>
      <div *ngIf="error()" class="alert alert-danger">{{ error() }}</div>
      <article *ngIf="contract() as contract">
        <header>
          <div><p>Contract #{{ contract.id }}</p><h2>{{ contract.contractTitle }}</h2></div>
          <div class="header-actions">
            <button *ngIf="canMessage" type="button" class="btn btn-outline-primary" (click)="messageCounterparty()">Message counterparty</button>
            <a *ngIf="canManage" class="btn btn-primary" [routerLink]="['/contracts', contract.id, 'edit']">Edit</a>
          </div>
        </header>
        <dl><div><dt>Vendor</dt><dd>{{ contract.vendorId }}</dd></div><div><dt>End date</dt><dd>{{ contract.endDate | date:'mediumDate' }}</dd></div><div><dt>Value</dt><dd>{{ contract.contractValue | currency:'INR' }}</dd></div></dl>
        <div class="actions" *ngIf="canManage"><label>Status<select class="form-select" [(ngModel)]="status"><option>Active</option><option>Expired</option><option>Terminated</option></select></label><button class="btn btn-primary" (click)="updateStatus()">Update status</button><button class="btn btn-primary" (click)="renew()">Renew</button><button *ngIf="canDelete" class="btn btn-danger" (click)="remove()">Delete</button></div>
        <form class="renewal" *ngIf="canManage"><label>New end date<input class="form-control" type="date" [(ngModel)]="newEndDate" name="end"></label><label>Renewal value<input class="form-control" type="number" [(ngModel)]="renewalValue" name="value"></label><label>Remarks<input class="form-control" [(ngModel)]="remarks" name="remarks"></label></form>
        <p class="alert alert-info">Document actions are managed in Vendor Documentation. File replacement is not supported.</p>
      </article>
    </section>`,
  styles: [`section{color:var(--vr-navy)}header,.actions{display:flex;gap:1rem;justify-content:space-between;align-items:end;margin:1rem 0}.header-actions{display:flex;gap:.6rem;flex-wrap:wrap}dl,.renewal{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}dl div{padding:1rem;border:1px solid var(--vr-border);border-radius:12px}dt{color:var(--vr-muted)}dd{margin:.3rem 0;font-weight:700}.actions label{min-width:160px}.btn-danger{background:#b91c1c;color:#fff}@media(max-width:600px){dl,.renewal{grid-template-columns:1fr}.actions,header{align-items:stretch;flex-wrap:wrap}}`]
})
export class ContractDetailsComponent {
  private readonly service = inject(ContractService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly messages = inject(DirectMessageService);
  private readonly auth = inject(AuthService);
  readonly id = Number(this.route.snapshot.paramMap.get('id'));
  readonly contract = signal<Contract | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');
  status = 'Active'; newEndDate = ''; renewalValue = 0; remarks = '';

  get canMessage(): boolean { return this.auth.hasRole('Administrator', 'Procurement Manager', 'Vendor', 'Auditor', 'Finance Officer'); }
  get canManage(): boolean { return this.auth.hasRole('Administrator', 'Procurement Manager'); }
  get canDelete(): boolean { return this.auth.hasRole('Administrator'); }
  ngOnInit(): void { this.load(); }
  load(): void { this.service.get(this.id).subscribe({ next: contract => { this.contract.set(contract); this.status = contract.status; this.loading.set(false); }, error: () => { this.error.set('Contract not found.'); this.loading.set(false); } }); }
  messageCounterparty(): void {
    const contract = this.contract(); if (!contract) return;
    this.error.set('');
    this.messages.getContextContacts('contract', contract.id).subscribe({
      next: contacts => { const contact = contacts[0]; if (!contact) { this.error.set('No active counterparty account is linked to this contract.'); return; } this.router.navigate(['/messages', contact.userId], { queryParams: { relatedEntityType: 'contract', relatedEntityId: contract.id } }); },
      error: () => this.error.set('Unable to resolve the contract message contact.')
    });
  }
  updateStatus(): void { this.service.updateContractStatus(this.id, this.status).subscribe({ next: contract => this.contract.set(contract), error: () => this.error.set('Unable to update status.') }); }
  renew(): void { if (!this.newEndDate) { this.error.set('New end date is required.'); return; } this.service.renewContract(this.id, { newEndDate: `${this.newEndDate}T00:00:00`, renewalValue: this.renewalValue, remarks: this.remarks }).subscribe({ next: contract => this.contract.set(contract), error: () => this.error.set('Unable to renew contract.') }); }
  remove(): void { if (confirm('Delete this contract?')) this.service.deleteContract(this.id).subscribe({ next: () => this.router.navigateByUrl('/contracts'), error: () => this.error.set('Unable to delete contract.') }); }
}
