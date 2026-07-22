import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcurementTracking } from './procurement-tracking';

describe('ProcurementTracking', () => {
  let component: ProcurementTracking;
  let fixture: ComponentFixture<ProcurementTracking>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcurementTracking],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcurementTracking);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
