import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementStatusManagementComponent } from './procurement-status-management';

describe('ProcurementStatusManagement', () => {
  let component: ProcurementStatusManagementComponent;
  let fixture: ComponentFixture<ProcurementStatusManagementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementStatusManagementComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementStatusManagementComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
