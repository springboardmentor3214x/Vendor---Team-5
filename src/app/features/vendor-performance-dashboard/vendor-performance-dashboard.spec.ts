import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorPerformanceDashboard } from './vendor-performance-dashboard';

describe('VendorPerformanceDashboard', () => {
  let component: VendorPerformanceDashboard;
  let fixture: ComponentFixture<VendorPerformanceDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorPerformanceDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorPerformanceDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
