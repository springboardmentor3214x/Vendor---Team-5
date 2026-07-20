import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeliveryPerformanceMonitoring } from './delivery-performance-monitoring';

describe('DeliveryPerformanceMonitoring', () => {
  let component: DeliveryPerformanceMonitoring;
  let fixture: ComponentFixture<DeliveryPerformanceMonitoring>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeliveryPerformanceMonitoring],
    }).compileComponents();

    fixture = TestBed.createComponent(DeliveryPerformanceMonitoring);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
