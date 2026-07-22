import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PerformanceMetricsComponent } from './performance-metrics';

describe('PerformanceMetrics', () => {
  let component: PerformanceMetricsComponent;
  let fixture: ComponentFixture<PerformanceMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PerformanceMetricsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PerformanceMetricsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
