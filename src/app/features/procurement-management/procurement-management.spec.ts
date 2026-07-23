import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementManagement } from './procurement-management';

describe('ProcurementManagement', () => {
  let component: ProcurementManagement;
  let fixture: ComponentFixture<ProcurementManagement>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementManagement],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementManagement);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
